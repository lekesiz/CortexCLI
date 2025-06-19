"""
CortexCLI Web Arayüzü
Flask tabanlı modern web dashboard
"""

import os
import json
import asyncio
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, send_from_directory
from flask_socketio import SocketIO, emit, join_room, leave_room
import requests
from rich.console import Console
from themes import theme_manager, get_theme_css

console = Console()

# Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'cortexcli-secret-key-2024'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global state
chat_history = []
active_models = {}
current_model = "qwen2.5:7b"
system_prompt = "Sen yardımcı bir AI asistanısın."
theme_manager = None
plugin_manager = None

class WebInterface:
    """Web arayüzü yöneticisi"""
    
    def __init__(self, host: str = "0.0.0.0", port: int = 5000):
        self.host = host
        self.port = port
        self.app = app
        self.socketio = socketio
        
        # Template dizinini oluştur
        self.templates_dir = Path("web_templates")
        self.templates_dir.mkdir(exist_ok=True)
        
        # Static dosyalar için dizin
        self.static_dir = Path("web_static")
        self.static_dir.mkdir(exist_ok=True)
        
        self._setup_routes()
        self._setup_socketio()
        
    def _setup_routes(self):
        """Flask route'larını ayarla"""
        
        @app.route('/')
        def index():
            """Ana sayfa"""
            return render_template('index.html')
            
        @app.route('/chat')
        def chat():
            """Sohbet sayfası"""
            return render_template('chat.html')
            
        @app.route('/models')
        def models():
            """Model yönetimi sayfası"""
            return render_template('models.html')
            
        @app.route('/files')
        def files():
            """Dosya yönetimi sayfası"""
            return render_template('files.html')
            
        @app.route('/plugins')
        def plugins():
            """Plugin yönetimi sayfası"""
            return render_template('plugins.html')
            
        @app.route('/code')
        def code():
            """Kod çalıştırma sayfası"""
            return render_template('code.html')
            
        @app.route('/help')
        def help_page():
            """Yardım/dokümantasyon sayfası"""
            return render_template('help.html')
            
        @app.route('/upload', methods=['GET', 'POST'])
        def upload():
            """CSV dosyası yükleme ve analiz sayfası"""
            return render_template('upload.html')
            
        @app.route('/settings')
        def settings():
            """Kullanıcı ayarları sayfası"""
            return render_template('settings.html')
            
        @app.route('/api/chat', methods=['POST'])
        def api_chat():
            """Chat API endpoint"""
            try:
                data = request.get_json()
                message = data.get('message', '')
                model = data.get('model', current_model)
                
                # LLM sorgusu yap
                response = self._query_llm(message, model)
                
                # Geçmişe ekle
                chat_entry = {
                    'user': message,
                    'assistant': response,
                    'timestamp': datetime.now().isoformat(),
                    'model': model
                }
                chat_history.append(chat_entry)
                
                return jsonify({
                    'success': True,
                    'response': response,
                    'timestamp': chat_entry['timestamp']
                })
                
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
                
        @app.route('/api/models')
        def api_models():
            """Model listesi API"""
            try:
                from llm_shell import get_available_models
                models = get_available_models()
                return jsonify({
                    'success': True,
                    'models': models,
                    'current_model': current_model
                })
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
                
        @app.route('/api/files')
        def api_files():
            """Dosya listesi API"""
            try:
                path = request.args.get('path', '.')
                files = []
                
                for item in Path(path).iterdir():
                    files.append({
                        'name': item.name,
                        'type': 'directory' if item.is_dir() else 'file',
                        'size': item.stat().st_size if item.is_file() else 0,
                        'modified': datetime.fromtimestamp(item.stat().st_mtime).isoformat()
                    })
                    
                return jsonify({
                    'success': True,
                    'files': files,
                    'current_path': str(Path(path).absolute())
                })
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
                
        @app.route('/api/plugins')
        def api_plugins():
            """Plugin listesi API"""
            try:
                from plugin_system import PluginManager
                plugin_manager = PluginManager()
                plugins = plugin_manager.list_plugins()
                
                return jsonify({
                    'success': True,
                    'plugins': plugins
                })
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
                
        @app.route('/api/code/execute', methods=['POST'])
        def api_execute_code():
            """Kod çalıştırma API"""
            try:
                data = request.get_json()
                code = data.get('code', '')
                language = data.get('language', 'python')
                
                from advanced_code_execution import sandbox_executor
                result = sandbox_executor.execute_code(code, language)
                
                return jsonify({
                    'success': result.success,
                    'output': result.output,
                    'error': result.error,
                    'execution_time': result.execution_time
                })
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
                
        @app.route('/api/code/analyze', methods=['POST'])
        def api_analyze_code():
            """Kod analizi API"""
            try:
                data = request.get_json()
                code = data.get('code', '')
                language = data.get('language', 'python')
                
                from advanced_code_execution import sandbox_executor
                analysis = sandbox_executor.analyzer.analyze_code(code, language)
                
                return jsonify({
                    'success': True,
                    'analysis': analysis
                })
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
                
        @app.route('/api/themes')
        def api_themes():
            """Tema listesi API"""
            try:
                from themes import ThemeManager
                theme_manager = ThemeManager()
                themes = theme_manager.list_themes()
                current_theme = theme_manager.get_current_theme()
                
                return jsonify({
                    'success': True,
                    'themes': themes,
                    'current_theme': {
                        'id': theme_manager.current_theme,
                        'name': current_theme.name,
                        'description': current_theme.description
                    }
                })
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
                
        @app.route('/api/themes/set', methods=['POST'])
        def api_set_theme():
            """Tema değiştirme API"""
            try:
                data = request.get_json()
                theme_id = data.get('theme_id')
                
                from themes import ThemeManager
                theme_manager = ThemeManager()
                success = theme_manager.set_theme(theme_id)
                
                return jsonify({
                    'success': success,
                    'message': f'Tema {theme_id} olarak ayarlandı' if success else 'Tema değiştirilemedi'
                })
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
                
        @app.route('/api/themes/create', methods=['POST'])
        def api_create_theme():
            """Yeni tema oluşturma API"""
            try:
                data = request.get_json()
                theme_id = data.get('theme_id')
                name = data.get('name')
                description = data.get('description', '')
                colors = data.get('colors', {})
                
                from themes import ThemeManager
                theme_manager = ThemeManager()
                success = theme_manager.create_theme(theme_id, name, description, colors)
                
                return jsonify({
                    'success': success,
                    'message': f'Tema {name} oluşturuldu' if success else 'Tema oluşturulamadı'
                })
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
                
        @app.route('/api/themes/delete', methods=['POST'])
        def api_delete_theme():
            """Tema silme API"""
            try:
                data = request.get_json()
                theme_id = data.get('theme_id')
                
                from themes import ThemeManager
                theme_manager = ThemeManager()
                success = theme_manager.delete_theme(theme_id)
                
                return jsonify({
                    'success': success,
                    'message': f'Tema {theme_id} silindi' if success else 'Tema silinemedi'
                })
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
                
        @app.route('/api/themes/css')
        def api_theme_css():
            """Tema CSS API"""
            try:
                from themes import ThemeManager
                theme_manager = ThemeManager()
                css = theme_manager.generate_css()
                
                return css, 200, {'Content-Type': 'text/css'}
            except Exception as e:
                return str(e), 500
                
        @app.route('/api/help')
        def api_help():
            """Yardım sistemi API"""
            try:
                from llm_shell import help_system
                category = request.args.get('category', 'all')
                search = request.args.get('search', '')
                
                if search:
                    help_data = help_system.search_help(search)
                elif category != 'all':
                    help_data = help_system.get_category_help(category)
                else:
                    help_data = help_system.get_all_help()
                
                return jsonify({
                    'success': True,
                    'help': help_data
                })
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
                
        @app.route('/api/upload', methods=['POST'])
        def api_upload():
            """CSV dosyası yükleme API"""
            try:
                if 'file' not in request.files:
                    return jsonify({'success': False, 'error': 'Dosya bulunamadı'}), 400
                    
                file = request.files['file']
                if file.filename == '':
                    return jsonify({'success': False, 'error': 'Dosya seçilmedi'}), 400
                    
                if file and file.filename.endswith('.csv'):
                    filename = f"upload_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                    filepath = Path('output') / filename
                    file.save(filepath)
                    
                    return jsonify({
                        'success': True,
                        'filename': filename,
                        'filepath': str(filepath)
                    })
                else:
                    return jsonify({'success': False, 'error': 'Sadece CSV dosyaları kabul edilir'}), 400
                    
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 500
                
        @app.route('/api/data-analyze', methods=['POST'])
        def api_data_analyze():
            """Veri analizi API"""
            try:
                data = request.get_json()
                filename = data.get('filename')
                analysis_type = data.get('type', 'describe')
                
                from plugins.data_analyzer import DataAnalyzerPlugin
                analyzer = DataAnalyzerPlugin()
                
                if analysis_type == 'describe':
                    result = analyzer.describe_csv(f"output/{filename}")
                elif analysis_type == 'plot':
                    plot_type = data.get('plot_type', 'line')
                    columns = data.get('columns', [])
                    result = analyzer.plot_csv(f"output/{filename}", plot_type, columns)
                else:
                    return jsonify({'success': False, 'error': 'Geçersiz analiz türü'}), 400
                
                return jsonify({
                    'success': True,
                    'result': result
                })
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 500
                
        @app.route('/output/<path:filename>')
        def serve_output_file(filename):
            """Output dosyalarını servis et"""
            return send_from_directory('output', filename)
            
        @app.route('/api/settings')
        def api_settings():
            """Kullanıcı ayarları API"""
            try:
                from user_settings import UserSettings
                settings = UserSettings()
                profile = settings.get_profile()
                preferences = settings.get_preferences()
                stats = settings.get_statistics()
                
                return jsonify({
                    'success': True,
                    'profile': profile,
                    'preferences': preferences,
                    'statistics': stats
                })
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
                
        @app.route('/api/settings/update', methods=['POST'])
        def api_update_settings():
            """Ayarları güncelleme API"""
            try:
                data = request.get_json()
                setting_type = data.get('type')
                settings_data = data.get('data', {})
                
                from user_settings import UserSettings
                user_settings = UserSettings()
                
                if setting_type == 'profile':
                    success = user_settings.update_profile(settings_data)
                elif setting_type == 'preferences':
                    success = user_settings.update_preferences(settings_data)
                else:
                    return jsonify({'success': False, 'error': 'Geçersiz ayar türü'}), 400
                
                return jsonify({
                    'success': success,
                    'message': 'Ayarlar güncellendi' if success else 'Ayarlar güncellenemedi'
                })
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
                
        @app.route('/api/file-list', methods=['POST'])
        def api_file_list():
            """Dosya listesi API"""
            try:
                data = request.get_json()
                path = data.get('path', '.')
                show_hidden = data.get('show_hidden', False)
                
                files = []
                for item in Path(path).iterdir():
                    if not show_hidden and item.name.startswith('.'):
                        continue
                    files.append({
                        'name': item.name,
                        'type': 'directory' if item.is_dir() else 'file',
                        'size': item.stat().st_size if item.is_file() else 0,
                        'modified': datetime.fromtimestamp(item.stat().st_mtime).isoformat(),
                        'path': str(item)
                    })
                
                return jsonify({
                    'success': True,
                    'files': files,
                    'current_path': str(Path(path).absolute())
                })
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
                
        @app.route('/api/file-preview', methods=['POST'])
        def api_file_preview():
            """Dosya önizleme API"""
            try:
                data = request.get_json()
                filepath = data.get('filepath')
                max_lines = data.get('max_lines', 50)
                
                if not Path(filepath).is_file():
                    return jsonify({'success': False, 'error': 'Dosya bulunamadı'}), 404
                
                with open(filepath, 'r', encoding='utf-8') as f:
                    lines = f.readlines()[:max_lines]
                    content = ''.join(lines)
                    has_more = len(f.readlines()) > max_lines
                
                return jsonify({
                    'success': True,
                    'content': content,
                    'has_more': has_more,
                    'total_lines': len(lines)
                })
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
                
        @app.route('/api/file-search', methods=['POST'])
        def api_file_search():
            """Dosya arama API"""
            try:
                data = request.get_json()
                search_term = data.get('search_term', '')
                path = data.get('path', '.')
                file_types = data.get('file_types', [])
                
                results = []
                for item in Path(path).rglob('*'):
                    if item.is_file() and search_term.lower() in item.name.lower():
                        if file_types and item.suffix not in file_types:
                            continue
                        results.append({
                            'name': item.name,
                            'path': str(item),
                            'size': item.stat().st_size,
                            'modified': datetime.fromtimestamp(item.stat().st_mtime).isoformat()
                        })
                
                return jsonify({
                    'success': True,
                    'results': results
                })
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
                
        @app.route('/api/file-info', methods=['POST'])
        def api_file_info():
            """Dosya bilgisi API"""
            try:
                data = request.get_json()
                filepath = data.get('filepath')
                
                path = Path(filepath)
                if not path.exists():
                    return jsonify({'success': False, 'error': 'Dosya bulunamadı'}), 404
                
                info = {
                    'name': path.name,
                    'path': str(path.absolute()),
                    'type': 'directory' if path.is_dir() else 'file',
                    'size': path.stat().st_size if path.is_file() else 0,
                    'created': datetime.fromtimestamp(path.stat().st_ctime).isoformat(),
                    'modified': datetime.fromtimestamp(path.stat().st_mtime).isoformat(),
                    'permissions': oct(path.stat().st_mode)[-3:]
                }
                
                return jsonify({
                    'success': True,
                    'info': info
                })
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
                
        @app.route('/api/file-tree', methods=['POST'])
        def api_file_tree():
            """Dosya ağacı API"""
            try:
                data = request.get_json()
                path = data.get('path', '.')
                max_depth = data.get('max_depth', 3)
                
                def build_tree(p, depth=0):
                    if depth > max_depth:
                        return None
                    
                    tree = {
                        'name': p.name,
                        'type': 'directory' if p.is_dir() else 'file',
                        'path': str(p)
                    }
                    
                    if p.is_dir():
                        children = []
                        for child in p.iterdir():
                            if not child.name.startswith('.'):
                                child_tree = build_tree(child, depth + 1)
                                if child_tree:
                                    children.append(child_tree)
                        tree['children'] = children
                    
                    return tree
                
                root_tree = build_tree(Path(path))
                
                return jsonify({
                    'success': True,
                    'tree': root_tree
                })
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
                
    def _setup_socketio(self):
        """SocketIO event'lerini ayarla"""
        
        @socketio.on('connect')
        def handle_connect():
            """Kullanıcı bağlandığında"""
            console.print(f"[green]🌐 Web kullanıcısı bağlandı: {request.sid}[/green]")
            emit('status', {'message': 'Bağlantı kuruldu'})
            
        @socketio.on('disconnect')
        def handle_disconnect():
            """Kullanıcı ayrıldığında"""
            console.print(f"[yellow]🌐 Web kullanıcısı ayrıldı: {request.sid}[/yellow]")
            
        @socketio.on('join_chat')
        def handle_join_chat(data):
            """Chat odasına katıl"""
            room = data.get('room', 'general')
            join_room(room)
            emit('status', {'message': f'{room} odasına katıldınız'})
            
        @socketio.on('send_message')
        def handle_send_message(data):
            """Mesaj gönder"""
            try:
                message = data.get('message', '')
                model = data.get('model', current_model)
                room = data.get('room', 'general')
                
                # LLM sorgusu yap
                response = self._query_llm(message, model)
                
                # Geçmişe ekle
                chat_entry = {
                    'user': message,
                    'assistant': response,
                    'timestamp': datetime.now().isoformat(),
                    'model': model,
                    'user_id': request.sid
                }
                chat_history.append(chat_entry)
                
                # Odadaki herkese gönder
                emit('new_message', {
                    'user': message,
                    'assistant': response,
                    'timestamp': chat_entry['timestamp'],
                    'model': model,
                    'user_id': request.sid
                }, room=room)
                
            except Exception as e:
                emit('error', {'message': str(e)})
                
    def _query_llm(self, message: str, model: str) -> str:
        """LLM sorgusu yap"""
        try:
            from llm_shell import query_llm
            return query_llm(message, model)
        except Exception as e:
            return f"Hata: {str(e)}"
            
    def start(self):
        """Web sunucusunu başlat"""
        console.print(f"[green]🌐 Web arayüzü başlatılıyor: http://{self.host}:{self.port}[/green]")
        socketio.run(app, host=self.host, port=self.port, debug=False)
        
    def stop(self):
        """Web sunucusunu durdur"""
        console.print("[yellow]🌐 Web arayüzü durduruluyor...[/yellow]")

# Global web interface instance
web_interface = WebInterface() 