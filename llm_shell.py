#!/usr/bin/env python3
"""
CortexCLI - CLI LLM Shell
Claude Code tarzında, terminal üzerinden kullanılabilen hafif LLM sohbet uygulaması
"""

import subprocess
import typer
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.text import Text
from rich.syntax import Syntax
from rich.table import Table
import requests
import json
import os
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path
import config
import shutil
import time
import tempfile
import click
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter, Completer, Completion
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys
import sys
from rich.markdown import Markdown
from rich.progress import Progress
from plugin_system import PluginManager
from multi_model import multi_model_manager
from advanced_code_execution import sandbox_executor, jupyter_integration, code_debugger
from themes import theme_manager, print_themed, apply_cli_theme
from user_settings import user_settings, get_user_preferences, get_user_profile, get_user_stats

app = typer.Typer(help="CortexCLI - CLI LLM Shell")
console = Console()
chat_history = []
current_model = "qwen2.5:7b"
system_prompt = "Sen yardımcı bir AI asistanısın."
plugin_manager = PluginManager()

# Apply theme colors
colors = apply_cli_theme()

# Load user preferences
preferences = get_user_preferences()
current_model = preferences.default_model
system_prompt = preferences.default_system_prompt

def check_ollama() -> bool:
    """Ollama'nın yüklü ve çalışır durumda olup olmadığını kontrol eder"""
    try:
        # Ollama komutunun varlığını kontrol et
        if not shutil.which("ollama"):
            return False
        
        # Ollama servisinin çalışıp çalışmadığını kontrol et
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except:
        return False

def get_available_models() -> list:
    """Ollama'da mevcut modelleri listeler"""
    try:
        response = requests.get(f"{config.OLLAMA_CONFIG['base_url']}{config.OLLAMA_CONFIG['tags_endpoint']}")
        if response.status_code == 200:
            models = response.json().get("models", [])
            return [model["name"] for model in models]
    except:
        pass
    return []

def send_to_ollama(model: str, prompt: str, system_prompt: Optional[str] = None, temperature: float = 0.7) -> str:
    """Ollama API'sine istek gönderir"""
    try:
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "temperature": temperature,
            "num_predict": config.get_setting("max_tokens")
        }
        
        if system_prompt:
            payload["system"] = system_prompt
            
        response = requests.post(
            f"{config.OLLAMA_CONFIG['base_url']}{config.OLLAMA_CONFIG['api_endpoint']}", 
            json=payload,
            timeout=config.OLLAMA_CONFIG['timeout']
        )
        response.raise_for_status()
        
        # İstatistik kaydet
        user_settings.record_query(model)
        
        return response.json()["response"]
    except requests.exceptions.Timeout:
        return "[HATA] Yanıt zaman aşımına uğradı"
    except requests.exceptions.ConnectionError:
        return "[HATA] Ollama servisine bağlanılamıyor. Ollama çalışıyor mu?"
    except Exception as e:
        return f"[HATA] Beklenmeyen hata: {str(e)}"

def save_to_history(prompt: str, response: str, model: str, history_file: str):
    """Sohbet geçmişini dosyaya kaydeder"""
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(history_file, "a", encoding="utf-8") as f:
            f.write(f"=== {timestamp} (Model: {model}) ===\n")
            f.write(f"🧠 Sen: {prompt}\n")
            f.write(f"🤖 Yanıt: {response}\n")
            f.write("-" * 50 + "\n\n")
    except Exception as e:
        console.print(f"[red]Geçmiş kaydedilemedi: {e}[/red]")

def format_code_response(response: str) -> str:
    """Kod içeren yanıtları formatlar"""
    if "```" in response:
        return response
    return response

def load_file_content(file_path: str) -> str:
    """Dosya içeriğini yükler"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"[HATA] Dosya okunamadı: {e}"

def save_file_content(file_path: str, content: str) -> bool:
    """Dosya içeriğini kaydeder"""
    try:
        # Dizini oluştur (yoksa)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        console.print(f"[red]Dosya kaydedilemedi: {e}[/red]")
        return False

def extract_code_blocks(response: str) -> list:
    """Yanıttan kod bloklarını çıkarır"""
    import re
    code_blocks = []
    
    # ```python ... ``` formatındaki kod bloklarını bul
    pattern = r'```(?:(\w+)\n)?(.*?)```'
    matches = re.findall(pattern, response, re.DOTALL)
    
    for lang, code in matches:
        if code.strip():
            code_blocks.append({
                'language': lang or 'text',
                'code': code.strip(),
                'filename': None
            })
    
    return code_blocks

def suggest_filename(language: str, content: str) -> str:
    """İçeriğe göre dosya adı önerir"""
    # İlk satırdan class/function adı çıkar
    lines = content.split('\n')
    for line in lines:
        line = line.strip()
        if line.startswith('class '):
            class_name = line.split('class ')[1].split('(')[0].split(':')[0].strip()
            return f"{class_name.lower()}.py"
        elif line.startswith('def '):
            func_name = line.split('def ')[1].split('(')[0].strip()
            return f"{func_name.lower()}.py"
    
    # Varsayılan dosya adları
    default_names = {
        'python': 'script.py',
        'javascript': 'script.js',
        'html': 'index.html',
        'css': 'style.css',
        'json': 'config.json',
        'yaml': 'config.yaml',
        'bash': 'script.sh',
        'sql': 'query.sql'
    }
    
    return default_names.get(language.lower(), 'output.txt')

def list_project_files(directory: str = ".") -> list:
    """Proje dosyalarını listeler"""
    files = []
    try:
        for root, dirs, filenames in os.walk(directory):
            # .git, __pycache__ gibi klasörleri atla
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
            
            for filename in filenames:
                if not filename.startswith('.'):
                    full_path = os.path.join(root, filename)
                    rel_path = os.path.relpath(full_path, directory)
                    files.append(rel_path)
    except Exception as e:
        console.print(f"[red]Dosya listesi alınamadı: {e}[/red]")
    
    return files

@app.command()
def shell(
    model: str = typer.Option(config.get_setting("model"), help="Model seç"),
    save_history: bool = typer.Option(config.get_setting("save_history"), help="Geçmişi kaydet"),
    history_file: str = typer.Option(config.get_setting("history_file"), help="Geçmiş dosyası adı"),
    system_prompt: Optional[str] = typer.Option(config.get_setting("system_prompt"), help="Sistem prompt'u"),
    system_preset: Optional[str] = typer.Option(None, help="Sistem prompt şablonu (python_expert, security_expert, translator, code_reviewer, teacher, debugger)"),
    multi_line: bool = typer.Option(config.get_setting("multi_line"), help="Çok satırlı giriş desteği"),
    temperature: float = typer.Option(config.get_setting("temperature"), help="Yaratıcılık seviyesi (0.0-1.0)"),
    file_input: Optional[str] = typer.Option(None, help="Dosya içeriğini prompt'a ekle"),
    auto_save: bool = typer.Option(False, help="Kod bloklarını otomatik kaydet"),
    output_dir: str = typer.Option("output", help="Çıktı dosyaları için dizin")
):
    """CortexCLI Shell'i başlatır"""
    
    # Ollama durumunu kontrol et
    if not check_ollama():
        console.print(Panel(
            "[red]❌ Ollama servisi çalışmıyor![/red]\n\n"
            "Ollama'yı başlatmak için:\n"
            "1. ollama serve\n"
            "2. Modelleri yüklemek için: ollama pull qwen:7b",
            title="Ollama Hatası",
            border_style="red"
        ))
        raise typer.Exit(1)
    
    # Model kontrolü
    selected_model = config.get_model_name(model.lower())
    if not selected_model:
        console.print(f"[red]❌ Desteklenmeyen model: {model}[/red]")
        console.print(f"Desteklenen modeller: {', '.join(config.get_available_models())}")
        raise typer.Exit(1)
    
    # Model mevcut mu kontrol et
    available_models = get_available_models()
    if selected_model not in available_models:
        console.print(Panel(
            f"[yellow]⚠️  Model {selected_model} yüklü değil![/yellow]\n\n"
            f"Yüklemek için: ollama pull {selected_model}",
            title="Model Uyarısı",
            border_style="yellow"
        ))
        raise typer.Exit(1)
    
    # Sistem prompt'u ayarla
    final_system_prompt = system_prompt
    if system_preset:
        preset_prompt = config.get_system_prompt(system_preset)
        if preset_prompt:
            final_system_prompt = preset_prompt
            console.print(f"[dim]Sistem şablonu yüklendi: {system_preset}[/dim]")
        else:
            console.print(f"[red]Bilinmeyen sistem şablonu: {system_preset}[/red]")
    
    # Çıktı dizinini oluştur
    if auto_save:
        os.makedirs(output_dir, exist_ok=True)
        console.print(f"[dim]Çıktı dizini: {output_dir}[/dim]")
    
    # Başlangıç mesajı
    console.print(Panel(
        f"[bold green]🚀 CortexCLI Shell[/bold green]\n"
        f"[cyan]Model:[/cyan] {selected_model}\n"
        f"[cyan]Geçmiş:[/cyan] {'Kaydediliyor' if save_history else 'Kaydedilmiyor'}\n"
        f"[cyan]Çok satır:[/cyan] {'Açık' if multi_line else 'Kapalı'}\n"
        f"[cyan]Temperature:[/cyan] {temperature}\n"
        f"[cyan]Otomatik Kaydet:[/cyan] {'Açık' if auto_save else 'Kapalı'}\n\n"
        f"[dim]Çıkmak için: exit, quit, q veya Ctrl+C[/dim]\n"
        f"[dim]Dosya komutları: /read, /write, /list, /save[/dim]",
        title="CortexCLI Shell",
        border_style="green"
    ))
    
    if final_system_prompt:
        console.print(f"[dim]Sistem Prompt: {final_system_prompt}[/dim]\n")
    
    # Ana döngü
    while True:
        try:
            # Prompt al
            if multi_line:
                console.print("[bold cyan]🧠 Sen (çok satırlı, 'END' ile bitir):[/bold cyan]")
                lines = []
                while True:
                    line = input()
                    if line.strip() == "END":
                        break
                    lines.append(line)
                prompt = "\n".join(lines)
            else:
                prompt = Prompt.ask("[bold cyan]🧠 Sen[/bold cyan]")
            
            # Çıkış kontrolü
            if prompt.strip().lower() in ["exit", "quit", "q"]:
                console.print("[bold yellow]👋 Çıkılıyor...[/bold yellow]")
                break
            
            if not prompt.strip():
                continue
            
            # Özel komutları kontrol et
            if prompt.startswith('/'):
                handle_special_commands(prompt, selected_model, final_system_prompt, temperature, output_dir)
                continue
            
            # Dosya içeriği ekle
            if file_input and os.path.exists(file_input):
                file_content = load_file_content(file_input)
                prompt = f"Dosya içeriği:\n{file_content}\n\nSoru: {prompt}"
            
            # Yanıt al
            console.print("[dim]🤔 Düşünüyor...[/dim]")
            response = send_to_ollama(selected_model, prompt, final_system_prompt, temperature)
            
            # Yanıtı formatla ve göster
            formatted_response = format_code_response(response)
            console.print(f"[bold green]🤖 Yanıt:[/bold green]")
            console.print(formatted_response)
            console.print()  # Boş satır
            
            # Kod bloklarını otomatik kaydet
            if auto_save:
                code_blocks = extract_code_blocks(response)
                for i, block in enumerate(code_blocks):
                    if block['code']:
                        suggested_name = suggest_filename(block['language'], block['code'])
                        filename = f"{output_dir}/{suggested_name}"
                        
                        if save_file_content(filename, block['code']):
                            console.print(f"[green]💾 Kod kaydedildi: {filename}[/green]")
            
            # Geçmişi kaydet
            if save_history:
                save_to_history(prompt, response, selected_model, history_file)
                
        except KeyboardInterrupt:
            console.print("\n[bold yellow]⚠️  İşlem iptal edildi.[/bold yellow]")
            break
        except EOFError:
            console.print("\n[bold yellow]👋 Çıkılıyor...[/bold yellow]")
            break

def handle_special_commands(command: str, model: str, system_prompt: str, temperature: float, output_dir: str):
    """Özel komutları işler"""
    parts = command.split()
    cmd = parts[0].lower()
    
    if cmd == '/read' and len(parts) > 1:
        # Dosya okuma
        file_path = parts[1]
        if os.path.exists(file_path):
            content = load_file_content(file_path)
            console.print(f"[bold blue]📖 Dosya: {file_path}[/bold blue]")
            console.print(Syntax(content, "text", theme="monokai"))
        else:
            console.print(f"[red]❌ Dosya bulunamadı: {file_path}[/red]")
    
    elif cmd == '/write' and len(parts) > 2:
        # Dosya yazma
        file_path = parts[1]
        content = " ".join(parts[2:])
        if save_file_content(file_path, content):
            console.print(f"[green]✅ Dosya yazıldı: {file_path}[/green]")
    
    elif cmd == '/list':
        # Proje dosyalarını listele
        directory = parts[1] if len(parts) > 1 else "."
        files = list_project_files(directory)
        
        table = Table(title=f"📁 Proje Dosyaları ({directory})")
        table.add_column("Dosya", style="cyan")
        table.add_column("Boyut", style="green")
        
        for file_path in files[:20]:  # İlk 20 dosya
            try:
                size = os.path.getsize(file_path)
                table.add_row(file_path, f"{size:,} bytes")
            except:
                table.add_row(file_path, "N/A")
        
        console.print(table)
        if len(files) > 20:
            console.print(f"[dim]... ve {len(files) - 20} dosya daha[/dim]")
    
    elif cmd == '/save' and len(parts) > 2:
        # Yanıttan kod kaydet
        filename = parts[1]
        content = " ".join(parts[2:])
        
        if save_file_content(filename, content):
            console.print(f"[green]✅ Dosya kaydedildi: {filename}[/green]")
    
    elif cmd == '/help':
        # Yardım
        console.print(Panel(
            "[bold cyan]Özel Komutlar:[/bold cyan]\n\n"
            "[green]/read <dosya>[/green] - Dosya içeriğini oku\n"
            "[green]/write <dosya> <içerik>[/green] - Dosyaya yaz\n"
            "[green]/list [dizin][/green] - Proje dosyalarını listele\n"
            "[green]/save <dosya> <içerik>[/green] - Dosyaya kaydet\n"
            "[green]/help[/green] - Bu yardımı göster\n\n"
            "[dim]Örnek: /read main.py[/dim]\n"
            "[dim]Örnek: /write test.py 'print(\"Hello\")'[/dim]",
            title="Komut Yardımı",
            border_style="blue"
        ))
    
    else:
        console.print(f"[red]❌ Bilinmeyen komut: {cmd}[/red]")
        console.print("[dim]Yardım için: /help[/dim]")

@app.command()
def list_models():
    """Mevcut modelleri listeler"""
    table = Table(title="📋 Model Listesi")
    table.add_column("Alias", style="cyan")
    table.add_column("Ollama Adı", style="green")
    table.add_column("Durum", style="yellow")
    
    available_models = get_available_models()
    
    for alias, model_name in config.MODELS.items():
        status = "✅ Yüklü" if model_name in available_models else "❌ Yüklü Değil"
        table.add_row(alias, model_name, status)
    
    console.print(table)

@app.command()
def install_model(model_name: str):
    """Model yükler"""
    if model_name not in config.MODELS:
        console.print(f"[red]❌ Desteklenmeyen model: {model_name}[/red]")
        console.print(f"Desteklenen modeller: {', '.join(config.get_available_models())}")
        raise typer.Exit(1)
    
    model = config.MODELS[model_name]
    console.print(f"[yellow]📥 {model} yükleniyor...[/yellow]")
    
    try:
        result = subprocess.run(
            ["ollama", "pull", model],
            capture_output=True,
            text=True,
            check=True
        )
        console.print(f"[green]✅ {model} başarıyla yüklendi![/green]")
    except subprocess.CalledProcessError as e:
        console.print(f"[red]❌ Model yüklenemedi: {e.stderr}[/red]")
        raise typer.Exit(1)

@app.command()
def list_presets():
    """Sistem prompt şablonlarını listeler"""
    table = Table(title="🎭 Sistem Prompt Şablonları")
    table.add_column("Şablon", style="cyan")
    table.add_column("Açıklama", style="green")
    
    for preset, prompt in config.SYSTEM_PROMPTS.items():
        # İlk 50 karakteri al
        description = prompt[:50] + "..." if len(prompt) > 50 else prompt
        table.add_row(preset, description)
    
    console.print(table)

@app.command()
def quick_chat(
    prompt: str = typer.Argument(..., help="Hızlı soru"),
    model: str = typer.Option(config.get_setting("model"), help="Model seç"),
    temperature: float = typer.Option(config.get_setting("temperature"), help="Yaratıcılık seviyesi")
):
    """Tek seferlik hızlı soru-cevap"""
    
    if not check_ollama():
        console.print("[red]❌ Ollama servisi çalışmıyor![/red]")
        raise typer.Exit(1)
    
    selected_model = config.get_model_name(model.lower())
    if not selected_model:
        console.print(f"[red]❌ Desteklenmeyen model: {model}[/red]")
        raise typer.Exit(1)
    
    console.print(f"[dim]🤔 {selected_model} düşünüyor...[/dim]")
    response = send_to_ollama(selected_model, prompt, temperature=temperature)
    
    console.print(f"[bold green]🤖 Yanıt:[/bold green]")
    console.print(response)

def setup_smart_model() -> bool:
    """Akıllı model kurulumu"""
    global current_model
    
    # Ollama kontrolü
    if not check_ollama():
        console.print("[red]❌ Ollama bulunamadı![/red]")
        console.print("[yellow]Ollama'yı yüklemek için: https://ollama.ai[/yellow]")
        return False
    
    # Mevcut modelleri kontrol et
    available_models = get_available_models()
    if not available_models:
        console.print("[yellow]⚠️ Hiç model bulunamadı![/yellow]")
        
        # En iyi kod modelini öner
        best_model = "qwen2.5:7b"
        if Confirm.ask(f"En iyi kod modeli ({best_model}) otomatik yüklensin mi?"):
            try:
                with Progress() as progress:
                    task = progress.add_task("Model yükleniyor...", total=None)
                    subprocess.run(["ollama", "pull", best_model], check=True)
                    progress.update(task, completed=True)
                
                current_model = best_model
                console.print(f"[green]✅ Model başarıyla yüklendi: {best_model}[/green]")
                return True
            except Exception as e:
                console.print(f"[red]❌ Model yükleme hatası: {e}[/red]")
                return False
        else:
            return False
    
    # Model seçimi
    console.print("\n[bold cyan]Kullanılabilir modeller:[/bold cyan]")
    model_choices = []
    
    for i, model in enumerate(available_models, 1):
        model_choices.append(model)
        console.print(f"[green]{i}[/green]. {model}")
    
    while True:
        try:
            choice = Prompt.ask("Model seçin", default="1")
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(model_choices):
                current_model = model_choices[choice_idx]
                console.print(f"[green]✅ Seçilen model: {current_model}[/green]")
                return True
            else:
                console.print("[red]Geçersiz seçim![/red]")
        except ValueError:
            console.print("[red]Lütfen geçerli bir sayı girin![/red]")

def select_system_prompt() -> str:
    """Sistem promptu seçimi"""
    console.print("\n[bold cyan]Sistem promptu seçin:[/bold cyan]")
    
    presets = list(config.SYSTEM_PROMPTS.keys())
    for i, preset in enumerate(presets, 1):
        desc = config.SYSTEM_PROMPTS[preset][:50] + "..."
        console.print(f"[green]{i}[/green]. {preset} ([dim]{desc}[/dim])")
    console.print(f"[green]0[/green]. [dim]Özel prompt[/dim]")
    
    while True:
        try:
            choice = Prompt.ask("Seçiminiz", default="0")
            choice_idx = int(choice)
            
            if choice_idx == 0:
                custom_prompt = Prompt.ask("Özel sistem promptu girin", default="Sen yardımcı bir AI asistanısın.")
                return custom_prompt
            elif 1 <= choice_idx <= len(presets):
                selected_preset = presets[choice_idx - 1]
                return config.SYSTEM_PROMPTS[selected_preset]
            else:
                console.print("[red]Geçersiz seçim![/red]")
        except ValueError:
            console.print("[red]Lütfen geçerli bir sayı girin![/red]")

def interactive_start():
    """İnteraktif başlangıç"""
    global current_model, system_prompt, chat_history
    
    console.print(Panel.fit(
        "[bold cyan]CortexCLI[/bold cyan] - CLI LLM Shell\n"
        "[dim]Ollama modelleri ile güçlü AI sohbet deneyimi[/dim]",
        border_style="cyan"
    ))
    
    # Plugin sistemini başlat
    console.print("[dim]🔌 Plugin sistemi başlatılıyor...[/dim]")
    discovered_plugins = plugin_manager.discover_plugins()
    if discovered_plugins:
        console.print(f"[green]✅ {len(discovered_plugins)} plugin keşfedildi[/green]")
        # Otomatik olarak tüm plugin'leri yükle
        for plugin_name in discovered_plugins:
            plugin_manager.load_plugin(plugin_name)
    else:
        console.print("[dim]📦 Plugin bulunamadı[/dim]")
    
    # Akıllı model kurulumu
    if not setup_smart_model():
        return
    
    # Sistem promptu seçimi
    system_prompt = select_system_prompt()
    
    # Çok satırlı giriş ayarı
    config.MULTILINE_INPUT = Confirm.ask(
        "Çok satırlı giriş kullanmak ister misiniz?",
        default=True
    )
    
    # Otomatik kod kaydetme
    config.AUTO_SAVE_CODE = Confirm.ask(
        "Kod bloklarını otomatik kaydetmek ister misiniz?",
        default=True
    )
    
    # Geçmiş kaydetme
    config.SAVE_HISTORY = Confirm.ask(
        "Sohbet geçmişini kaydetmek ister misiniz?",
        default=True
    )
    
    console.print("\n[green]✅ Kurulum tamamlandı![/green]")
    
    # Ana sohbet döngüsünü başlat
    chat_loop()

@app.command()
def start():
    """Etkileşimli başlangıç sihirbazı"""
    interactive_start()

@app.command()
def web():
    """Web arayüzünü başlatır"""
    try:
        from web_interface import WebInterface
        console.print("[bold green]🌐 Web arayüzü başlatılıyor...[/bold green]")
        console.print("[dim]Tarayıcıda http://localhost:5000 adresini açın[/dim]")
        
        web_interface = WebInterface()
        web_interface.start()
    except KeyboardInterrupt:
        console.print("\n[yellow]Web arayüzü kapatılıyor...[/yellow]")
    except Exception as e:
        console.print(f"[red]Web arayüzü hatası: {e}[/red]")

@app.command()
def voice():
    """Ses komutları yönetimi"""
    try:
        from voice_commands import voice_system, get_voice_commands
        
        console.print("🎤 Ses Komutları Yönetimi")
        console.print("=" * 40)
        
        # Mevcut komutları göster
        categories = get_voice_commands()
        for category, commands in categories.items():
            console.print(f"\n[bold blue]{category.upper()}[/bold blue]")
            for cmd in commands:
                console.print(f"  • {cmd.name}: {cmd.description}")
                console.print(f"    Anahtar kelimeler: {', '.join(cmd.keywords[:3])}")
                
        # Ayarlar
        console.print(f"\n[bold yellow]Ayarlar:[/bold yellow]")
        console.print(f"  Uyandırma kelimesi: {voice_system.wake_word}")
        console.print(f"  Dil: {voice_system.language}")
        console.print(f"  Güven eşiği: {voice_system.confidence_threshold}")
        
        # Komut seçenekleri
        console.print(f"\n[bold green]Komutlar:[/bold green]")
        console.print("  /voice start    - Ses dinlemeyi başlat")
        console.print("  /voice stop     - Ses dinlemeyi durdur")
        console.print("  /voice test     - Ses tanıma testi")
        console.print("  /voice config   - Ses ayarlarını değiştir")
        console.print("  /voice add      - Yeni ses komutu ekle")
        console.print("  /voice remove   - Ses komutu kaldır")
        
    except ImportError:
        console.print("[red]❌ Ses komutları modülü bulunamadı[/red]")
        console.print("Kurulum: pip install SpeechRecognition pyttsx3")

@app.command()
def voice_start():
    """Ses dinlemeyi başlat"""
    try:
        from voice_commands import start_voice_commands
        console.print("🎤 Ses dinleme başlatılıyor...")
        console.print("Uyandırma kelimesi: 'cortex'")
        console.print("Çıkmak için Ctrl+C")
        
        # Ayrı thread'de başlat
        import threading
        voice_thread = threading.Thread(target=start_voice_commands, daemon=True)
        voice_thread.start()
        
        # Ana thread'i bekle
        try:
            voice_thread.join()
        except KeyboardInterrupt:
            console.print("\n[yellow]Ses dinleme durduruldu[/yellow]")
            
    except ImportError:
        console.print("[red]❌ Ses komutları modülü bulunamadı[/red]")

@app.command()
def voice_stop():
    """Ses dinlemeyi durdur"""
    try:
        from voice_commands import stop_voice_commands
        stop_voice_commands()
        console.print("🎤 Ses dinleme durduruldu")
    except ImportError:
        console.print("[red]❌ Ses komutları modülü bulunamadı[/red]")

@app.command()
def voice_test():
    """Ses tanıma testi"""
    try:
        from voice_commands import listen_for_command, speak
        
        console.print("🎤 Ses tanıma testi")
        console.print("Bir şeyler söyleyin...")
        
        text = listen_for_command()
        if text:
            console.print(f"[green]Duyulan: {text}[/green]")
            speak(f"Duyduğum: {text}")
        else:
            console.print("[red]Hiçbir şey duyulamadı[/red]")
            
    except ImportError:
        console.print("[red]❌ Ses komutları modülü bulunamadı[/red]")

@app.command()
def voice_config():
    """Ses ayarlarını değiştir"""
    try:
        from voice_commands import voice_system
        
        console.print("🎤 Ses Ayarları")
        console.print("=" * 30)
        
        # Uyandırma kelimesi
        wake_word = Prompt.ask("Uyandırma kelimesi", default=voice_system.wake_word)
        voice_system.set_wake_word(wake_word)
        
        # Dil
        language = Prompt.ask("Dil (tr-TR/en-US)", default=voice_system.language)
        voice_system.set_language(language)
        
        # Güven eşiği
        confidence = Prompt.ask("Güven eşiği (0.1-1.0)", default=str(voice_system.confidence_threshold))
        voice_system.confidence_threshold = float(confidence)
        
        console.print("[green]✅ Ses ayarları güncellendi[/green]")
        
    except ImportError:
        console.print("[red]❌ Ses komutları modülü bulunamadı[/red]")

@app.command()
def voice_add():
    """Yeni ses komutu ekle"""
    try:
        from voice_commands import add_voice_command
        
        console.print("🎤 Yeni Ses Komutu Ekle")
        console.print("=" * 30)
        
        name = Prompt.ask("Komut adı")
        description = Prompt.ask("Açıklama")
        keywords_input = Prompt.ask("Anahtar kelimeler (virgülle ayırın)")
        keywords = [k.strip() for k in keywords_input.split(",")]
        category = Prompt.ask("Kategori", default="özel")
        requires_confirmation = Confirm.ask("Onay gereksin mi?", default=False)
        
        # Basit bir action fonksiyonu
        def custom_action(text):
            return f"Özel komut çalıştırıldı: {text}"
        
        add_voice_command(name, description, keywords, custom_action, requires_confirmation, category)
        console.print("[green]✅ Ses komutu eklendi[/green]")
        
    except ImportError:
        console.print("[red]❌ Ses komutları modülü bulunamadı[/red]")

@app.command()
def voice_remove():
    """Ses komutu kaldır"""
    try:
        from voice_commands import voice_system, get_voice_commands
        
        console.print("🎤 Ses Komutu Kaldır")
        console.print("=" * 30)
        
        # Mevcut komutları listele
        categories = get_voice_commands()
        all_commands = []
        for category, commands in categories.items():
            for cmd in commands:
                all_commands.append(cmd)
        
        if not all_commands:
            console.print("[yellow]Kaldırılabilir komut yok[/yellow]")
            return
        
        # Komut seç
        for i, cmd in enumerate(all_commands, 1):
            console.print(f"{i}. {cmd.name} ({cmd.category})")
        
        choice = Prompt.ask("Kaldırılacak komut numarası", choices=[str(i) for i in range(1, len(all_commands) + 1)])
        selected_cmd = all_commands[int(choice) - 1]
        
        if Confirm.ask(f"'{selected_cmd.name}' komutunu kaldırmak istediğinizden emin misiniz?"):
            voice_system.remove_command(selected_cmd.name)
            console.print(f"[green]✅ '{selected_cmd.name}' komutu kaldırıldı[/green]")
        
    except ImportError:
        console.print("[red]❌ Ses komutları modülü bulunamadı[/red]")

@app.command()
def suggest():
    """Kod önerileri al"""
    try:
        from advanced_features import get_code_suggestions, get_context_info
        
        context = Prompt.ask("Ne yapmak istiyorsunuz? (bağlam)")
        language = Prompt.ask("Programlama dili", default="python")
        
        suggestions = get_code_suggestions(context, language, limit=5)
        
        if suggestions:
            console.print(f"\n[bold blue]💡 Kod Önerileri ({language})[/bold blue]")
            console.print("=" * 50)
            
            for i, suggestion in enumerate(suggestions, 1):
                console.print(f"\n[bold green]{i}. {suggestion.description}[/bold green]")
                console.print(f"   Güven: {suggestion.confidence:.2f}")
                console.print(f"   Kategori: {suggestion.context}")
                console.print(f"   Etiketler: {', '.join(suggestion.tags)}")
                console.print(f"   [dim]```{suggestion.language}\n{suggestion.code}\n```[/dim]")
        else:
            console.print("[yellow]Bu bağlam için öneri bulunamadı[/yellow]")
            
    except ImportError:
        console.print("[red]❌ Gelişmiş özellikler modülü bulunamadı[/red]")

@app.command()
def smart():
    """Akıllı dosya işlemleri"""
    try:
        from advanced_features import suggest_smart_file_operations, get_context_info
        
        intent = Prompt.ask("Ne yapmak istiyorsunuz? (organize/backup/clean)")
        current_path = os.getcwd()
        
        operations = suggest_smart_file_operations(current_path, intent)
        
        if operations:
            console.print(f"\n[bold blue]🤖 Akıllı İşlem Önerileri[/bold blue]")
            console.print("=" * 40)
            
            for i, op in enumerate(operations, 1):
                console.print(f"\n[bold green]{i}. {op.description}[/bold green]")
                console.print(f"   Kaynak: {op.source}")
                if op.destination:
                    console.print(f"   Hedef: {op.destination}")
                console.print(f"   Risk: {op.risk_level}")
                console.print(f"   Tahmini süre: {op.estimated_time}s")
                
            # İşlem seç
            choice = Prompt.ask("Hangi işlemi yapmak istiyorsunuz?", choices=[str(i) for i in range(1, len(operations) + 1)])
            selected_op = operations[int(choice) - 1]
            
            if Confirm.ask(f"'{selected_op.description}' işlemini gerçekleştirmek istediğinizden emin misiniz?"):
                console.print(f"[green]✅ {selected_op.description} işlemi başlatılıyor...[/green]")
                # Burada gerçek işlem yapılabilir
                
        else:
            console.print("[yellow]Bu niyet için öneri bulunamadı[/yellow]")
            
    except ImportError:
        console.print("[red]❌ Gelişmiş özellikler modülü bulunamadı[/red]")

@app.command()
def context():
    """Bağlam analizi"""
    try:
        from advanced_features import get_context_info, suggest_improvements
        
        context_info = get_context_info()
        
        console.print("[bold blue]🔍 Bağlam Analizi[/bold blue]")
        console.print("=" * 30)
        
        console.print(f"📁 Mevcut dizin: {context_info.current_directory}")
        console.print(f"📋 Proje tipi: {context_info.project_type or 'Bilinmiyor'}")
        console.print(f"🔧 Git durumu: {context_info.git_status or 'Git yok'}")
        
        if context_info.dependencies:
            console.print(f"📦 Bağımlılıklar: {', '.join(context_info.dependencies[:5])}")
        
        if context_info.recent_files:
            console.print(f"📄 Son dosyalar: {', '.join(context_info.recent_files[:5])}")
        
        if context_info.recent_commands:
            console.print(f"⌨️  Son komutlar: {', '.join(context_info.recent_commands[-3:])}")
        
        # İyileştirme önerileri
        improvements = suggest_improvements(context_info)
        if improvements:
            console.print(f"\n[bold yellow]💡 İyileştirme Önerileri:[/bold yellow]")
            for improvement in improvements:
                console.print(f"  • {improvement}")
                
    except ImportError:
        console.print("[red]❌ Gelişmiş özellikler modülü bulunamadı[/red]")

@app.command()
def stats():
    """Kullanım istatistikleri"""
    try:
        from advanced_features import get_usage_stats
        
        days = Prompt.ask("Kaç günlük istatistik?", default="7")
        stats_data = get_usage_stats(int(days))
        
        console.print(f"[bold blue]📊 Kullanım İstatistikleri (Son {days} gün)[/bold blue]")
        console.print("=" * 50)
        
        # Özellik istatistikleri
        if stats_data["feature_stats"]:
            console.print(f"\n[bold green]Özellik Kullanımı:[/bold green]")
            for feature, data in stats_data["feature_stats"].items():
                success_rate = data["success_rate"] * 100
                console.print(f"  • {feature}: {data['count']} kez ({success_rate:.1f}% başarı)")
        else:
            console.print("[yellow]Henüz özellik kullanım verisi yok[/yellow]")
        
        # Dosya işlemleri
        if stats_data["file_operations"]:
            console.print(f"\n[bold green]Dosya İşlemleri:[/bold green]")
            for operation, count in stats_data["file_operations"].items():
                console.print(f"  • {operation}: {count} kez")
        else:
            console.print("[yellow]Henüz dosya işlem verisi yok[/yellow]")
            
    except ImportError:
        console.print("[red]❌ Gelişmiş özellikler modülü bulunamadı[/red]")

@app.command()
def add_suggestion():
    """Yeni kod önerisi ekle"""
    try:
        from advanced_features import add_code_suggestion
        
        console.print("[bold blue]➕ Yeni Kod Önerisi Ekle[/bold blue]")
        console.print("=" * 30)
        
        language = Prompt.ask("Programlama dili", default="python")
        category = Prompt.ask("Kategori", default="genel")
        description = Prompt.ask("Açıklama")
        code = Prompt.ask("Kod (çok satırlı)")
        tags_input = Prompt.ask("Etiketler (virgülle ayırın)")
        tags = [tag.strip() for tag in tags_input.split(",")]
        
        add_code_suggestion(language, category, code, description, tags)
        console.print("[green]✅ Kod önerisi eklendi[/green]")
        
    except ImportError:
        console.print("[red]❌ Gelişmiş özellikler modülü bulunamadı[/red]")

class CortexCompleter(Completer):
    """CortexCLI için özel komut tamamlama sınıfı"""
    
    def __init__(self):
        self.commands = {
            '/help': 'Yardım menüsünü göster',
            '/exit': 'Uygulamadan çık',
            '/quit': 'Uygulamadan çık',
            '/clear': 'Ekranı temizle',
            '/history': 'Sohbet geçmişini göster',
            '/save': 'Sohbet geçmişini kaydet',
            '/load': 'Sohbet geçmişini yükle',
            '/model': 'Model değiştir',
            '/models': 'Kullanılabilir modelleri listele',
            '/system': 'Sistem promptunu değiştir',
            '/read': 'Dosya oku',
            '/write': 'Dosya yaz',
            '/list': 'Dosyaları listele',
            '/delete': 'Dosya sil',
            '/rename': 'Dosya yeniden adlandır',
            '/mkdir': 'Klasör oluştur',
            '/cd': 'Klasör değiştir',
            '/pwd': 'Mevcut dizini göster',
            '/run': 'Kod çalıştır',
            '/install': 'Model yükle',
            '/troubleshoot': 'Sorun giderme',
            '/config': 'Yapılandırmayı göster',
            '/reset': 'Sohbet geçmişini sıfırla',
            '/voice': 'Ses komutları yönetimi',
            '/voice-start': 'Ses dinlemeyi başlat',
            '/voice-stop': 'Ses dinlemeyi durdur',
            '/voice-test': 'Ses tanıma testi',
            '/voice-config': 'Ses ayarlarını değiştir',
            '/voice-add': 'Yeni ses komutu ekle',
            '/voice-remove': 'Ses komutu kaldır',
            '/suggest': 'Kod önerileri al',
            '/smart': 'Akıllı dosya işlemleri',
            '/context': 'Bağlam analizi',
            '/stats': 'Kullanım istatistikleri',
            '/add-suggestion': 'Yeni kod önerisi ekle'
        }
        
        self.file_commands = ['/read', '/write', '/delete', '/rename']
        self.model_commands = ['/model', '/install']
        
    def get_completions(self, document, complete_event):
        word = document.get_word_before_cursor()
        line = document.text_before_cursor
        
        # Komut başlangıcı kontrolü
        if line.startswith('/'):
            # Komut tamamlama
            for cmd, desc in self.commands.items():
                if cmd.startswith(word):
                    yield Completion(cmd, start_position=-len(word), display=cmd, display_meta=desc)
        else:
            # Normal metin tamamlama (geçmişten)
            pass

def setup_advanced_terminal():
    """Gelişmiş terminal özelliklerini kurar"""
    # Klavye kısayolları
    kb = KeyBindings()
    
    @kb.add(Keys.F1)
    def _(event):
        """F1: Yardım menüsü"""
        event.app.current_buffer.insert_text('/help')
        
    @kb.add(Keys.F2)
    def _(event):
        """F2: Model değiştir"""
        event.app.current_buffer.insert_text('/model ')
        
    @kb.add(Keys.F3)
    def _(event):
        """F3: Geçmişi göster"""
        event.app.current_buffer.insert_text('/history')
        
    @kb.add(Keys.F4)
    def _(event):
        """F4: Dosya listesi"""
        event.app.current_buffer.insert_text('/list')
        
    @kb.add(Keys.F5)
    def _(event):
        """F5: Kod çalıştır"""
        event.app.current_buffer.insert_text('/run ')
        
    # Geçmiş dosyası
    history_file = Path.home() / '.cortexcli_history'
    
    # Prompt oturumu
    session = PromptSession(
        completer=CortexCompleter(),
        history=FileHistory(str(history_file)),
        auto_suggest=AutoSuggestFromHistory(),
        key_bindings=kb,
        enable_history_search=True,
        complete_while_typing=True
    )
    
    return session

def handle_file_commands(command: str, args: List[str]) -> bool:
    """Dosya sistemi komutlarını işler"""
    if command == '/read':
        if not args:
            console.print("[red]Kullanım: /read <dosya_yolu>[/red]")
            return True
            
        file_path = args[0]
        content = load_file_content(file_path)
        console.print(Panel(content, title=f"📖 {file_path}", border_style="blue"))
        
        # İstatistik kaydet
        user_settings.record_file_processed()
        return True
        
    elif command == '/write':
        if len(args) < 2:
            console.print("[red]Kullanım: /write <dosya_yolu> <içerik>[/red]")
            return True
            
        file_path = args[0]
        content = ' '.join(args[1:])
        
        if save_file_content(file_path, content):
            console.print(f"[green]✅ Dosya kaydedildi: {file_path}[/green]")
            
            # İstatistik kaydet
            user_settings.record_file_processed()
        return True
        
    elif command == '/list':
        directory = args[0] if args else "."
        files = list_project_files(directory)
        
        if files:
            table = Table(title=f"📁 {directory}")
            table.add_column("Dosya/Klasör", style="cyan")
            table.add_column("Boyut", style="green")
            
            for file_path in files[:20]:  # İlk 20 dosya
                try:
                    full_path = os.path.join(directory, file_path)
                    size = os.path.getsize(full_path) if os.path.isfile(full_path) else 0
                    table.add_row(file_path, f"{size} bytes")
                except:
                    table.add_row(file_path, "N/A")
            
            console.print(table)
            if len(files) > 20:
                console.print(f"[dim]... ve {len(files) - 20} dosya daha[/dim]")
        else:
            console.print("[dim]Dosya bulunamadı[/dim]")
        return True
        
    elif command == '/delete':
        if not args:
            console.print("[red]Kullanım: /delete <dosya_yolu>[/red]")
            return True
            
        file_path = args[0]
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
                console.print(f"[green]✅ Dosya silindi: {file_path}[/green]")
            elif os.path.isdir(file_path):
                import shutil
                shutil.rmtree(file_path)
                console.print(f"[green]✅ Klasör silindi: {file_path}[/green]")
            else:
                console.print(f"[red]❌ Dosya/klasör bulunamadı: {file_path}[/red]")
                return True
                
            # İstatistik kaydet
            user_settings.record_file_processed()
        except Exception as e:
            console.print(f"[red]❌ Silme hatası: {e}[/red]")
        return True
        
    elif command == '/rename':
        if len(args) < 2:
            console.print("[red]Kullanım: /rename <eski_ad> <yeni_ad>[/red]")
            return True
            
        old_name = args[0]
        new_name = args[1]
        
        try:
            os.rename(old_name, new_name)
            console.print(f"[green]✅ Yeniden adlandırıldı: {old_name} → {new_name}[/green]")
            
            # İstatistik kaydet
            user_settings.record_file_processed()
        except Exception as e:
            console.print(f"[red]❌ Yeniden adlandırma hatası: {e}[/red]")
        return True
        
    elif command == '/mkdir':
        if not args:
            console.print("[red]Kullanım: /mkdir <klasör_adı>[/red]")
            return True
            
        dir_name = args[0]
        try:
            os.makedirs(dir_name, exist_ok=True)
            console.print(f"[green]✅ Klasör oluşturuldu: {dir_name}[/green]")
            
            # İstatistik kaydet
        except Exception as e:
            console.print(f"[red]Klasör oluşturma hatası: {e}[/red]")
        return True
        
    elif command == '/cd':
        if not args:
            console.print("[red]Kullanım: /cd <klasör_yolu>[/red]")
            return True
        dir_path = args[0]
        try:
            os.chdir(dir_path)
            console.print(f"[green]✅ Dizin değiştirildi: {os.getcwd()}[/green]")
        except Exception as e:
            console.print(f"[red]Dizin değiştirme hatası: {e}[/red]")
        return True
        
    elif command == '/pwd':
        console.print(f"[cyan]Mevcut dizin: {os.getcwd()}[/cyan]")
        return True
        
    return False

def execute_code(code: str, language: str = "python") -> str:
    """Kodu güvenli bir şekilde çalıştırır"""
    try:
        if language.lower() == "python":
            # Geçici dosya oluştur
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            # Kodu çalıştır
            result = subprocess.run(
                [sys.executable, temp_file],
                capture_output=True,
                text=True,
                timeout=30  # 30 saniye timeout
            )
            
            # Geçici dosyayı sil
            os.unlink(temp_file)
            
            output = f"Çıkış Kodu: {result.returncode}\n"
            if result.stdout:
                output += f"Çıktı:\n{result.stdout}\n"
            if result.stderr:
                output += f"Hata:\n{result.stderr}\n"
                
            return output
            
        elif language.lower() == "bash":
            # Bash komutları için
            result = subprocess.run(
                code,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            output = f"Çıkış Kodu: {result.returncode}\n"
            if result.stdout:
                output += f"Çıktı:\n{result.stdout}\n"
            if result.stderr:
                output += f"Hata:\n{result.stderr}\n"
                
            return output
            
        else:
            return f"Desteklenmeyen dil: {language}"
            
    except subprocess.TimeoutExpired:
        return "Kod çalıştırma zaman aşımına uğradı (30 saniye)"
    except Exception as e:
        return f"Kod çalıştırma hatası: {e}"

def handle_code_execution(command: str, args: List[str]) -> bool:
    """Kod çalıştırma komutlarını işler"""
    if command == '/run':
        if not args:
            console.print("[red]Kullanım: /run <kod> veya /run --file <dosya>[/red]")
            return True
            
        if args[0] == '--file' and len(args) > 1:
            # Dosyadan kod çalıştır
            file_path = args[1]
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    code = f.read()
                language = Path(file_path).suffix[1:] if Path(file_path).suffix else 'python'
            except Exception as e:
                console.print(f"[red]Dosya okuma hatası: {e}[/red]")
                return True
        else:
            # Doğrudan kod çalıştır
            code = ' '.join(args)
            language = 'python'
        
        console.print(f"[yellow]🔄 Kod çalıştırılıyor... ({language})[/yellow]")
        result = execute_code(code, language)
        console.print(Panel(result, title="📊 Çalıştırma Sonucu", border_style="green"))
        return True
        
    return False

def enhance_llm_response(response: str) -> str:
    """LLM yanıtını geliştirir ve kod bloklarını işler"""
    # Kod bloklarını bul ve işle
    import re
    
    # Kod bloklarını bul
    code_blocks = re.findall(r'```(\w+)?\n(.*?)```', response, re.DOTALL)
    
    enhanced_response = response
    
    for lang, code in code_blocks:
        if not lang:
            lang = 'text'
            
        # Kod bloklarını syntax highlighting ile göster
        syntax = Syntax(code, lang, theme="monokai")
        enhanced_response = enhanced_response.replace(
            f'```{lang}\n{code}```',
            str(syntax)
        )
        
        # Otomatik kaydetme
        if config.AUTO_SAVE_CODE and lang in ['python', 'javascript', 'html', 'css', 'bash']:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{lang}_code_{timestamp}.{lang}"
            filepath = Path(config.OUTPUT_DIR) / filename
            
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(code)
                console.print(f"[green]💾 Kod otomatik kaydedildi: {filepath}[/green]")
            except Exception as e:
                console.print(f"[red]Kod kaydetme hatası: {e}[/red]")
    
    return enhanced_response

def show_advanced_help(*args):
    """Gelişmiş yardım menüsünü ve arama/detay fonksiyonunu gösterir"""
    # Yardım veritabanı
    help_db = {
        "temel": {
            "desc": "Temel komutlar ve genel kullanım",
            "commands": {
                "/help": ("Yardım menüsünü gösterir.", "Örnek: /help model"),
                "/exit, /quit": ("Uygulamadan çıkış yapar.", ""),
                "/clear": ("Ekranı temizler.", ""),
                "/config": ("Yapılandırmayı gösterir.", ""),
            }
        },
        "model": {
            "desc": "Model yönetimi ve LLM komutları",
            "commands": {
                "/model <ad>": ("Modeli değiştirir.", "Örnek: /model qwen2.5:7b"),
                "/models": ("Kullanılabilir modelleri listeler.", ""),
                "/system <prompt>": ("Sistem promptunu değiştirir.", "Örnek: /system Sen bir Python uzmanısın."),
                "/install <model>": ("Modeli indirir ve yükler.", "Örnek: /install deepseek-coder"),
                "/troubleshoot": ("Sorun giderme menüsünü açar.", "")
            }
        },
        "multi-model": {
            "desc": "Çoklu model yönetimi ve karşılaştırma",
            "commands": {
                "/add-model <alias> <model>": ("Yeni bir model ekler.", "Örnek: /add-model claude claude-3"),
                "/remove-model <alias>": ("Modeli kaldırır.", ""),
                "/list-models": ("Aktif modelleri listeler.", ""),
                "/compare <sorgu>": ("Modelleri karşılaştırır.", "Örnek: /compare Python'da dosya oku"),
                "/query-model <alias> <sorgu>": ("Belirli bir modelle sorgu yapar.", ""),
                "/metrics": ("Performans metriklerini gösterir.", ""),
                "/save-comparison [dosya]": ("Karşılaştırmayı kaydeder.", ""),
                "/clear-models": ("Model geçmişini temizler.", "")
            }
        },
        "sohbet": {
            "desc": "Sohbet ve geçmiş yönetimi",
            "commands": {
                "/history": ("Sohbet geçmişini gösterir.", ""),
                "/save <dosya>": ("Sohbet geçmişini kaydeder.", ""),
                "/load <dosya>": ("Sohbet geçmişini yükler.", ""),
                "/reset": ("Sohbet geçmişini sıfırlar.", "")
            }
        },
        "dosya": {
            "desc": "Dosya sistemi ve yönetimi",
            "commands": {
                "/read <dosya>": ("Dosya okur.", "Örnek: /read README.md"),
                "/write <dosya> <içerik>": ("Dosya yazar.", "Örnek: /write test.txt Merhaba"),
                "/list [dizin]": ("Dosyaları listeler.", ""),
                "/delete <dosya>": ("Dosya/klasör siler.", ""),
                "/rename <eski> <yeni>": ("Yeniden adlandırır.", ""),
                "/mkdir <klasör>": ("Klasör oluşturur.", ""),
                "/cd <dizin>": ("Dizin değiştirir.", ""),
                "/pwd": ("Mevcut dizini gösterir.", "")
            }
        },
        "kod": {
            "desc": "Kod çalıştırma ve analiz",
            "commands": {
                "/run <kod>": ("Kodu çalıştırır.", "Örnek: /run print('Merhaba')"),
                "/run --file <dosya>": ("Dosyadan kod çalıştırır.", ""),
                "/run-safe <kod>": ("Güvenli ortamda kod çalıştırır.", ""),
                "/analyze <kod>": ("Kod analizi yapar.", ""),
                "/notebook <ad> <kod>": ("Jupyter notebook oluşturur.", ""),
                "/add-cell <notebook> <kod>": ("Notebook'a hücre ekler.", ""),
                "/debug <kod>": ("Kod debug bilgisi verir.", ""),
                "/breakpoint <satır>": ("Breakpoint ekler.", "")
            }
        },
        "plugin": {
            "desc": "Plugin yönetimi ve komutları",
            "commands": {
                "/plugins": ("Yüklü plugin'leri listeler.", ""),
                "/load <plugin>": ("Plugin yükler.", "Örnek: /load web_search"),
                "/unload <plugin>": ("Plugin kaldırır.", ""),
                "/search <sorgu>": ("Web'de arama yapar (web_search plugin).", "Örnek: /search Python decorator"),
                "/weather <şehir>": ("Hava durumu alır (örnek plugin).", ""),
                "/analyze <dosya>": ("Dosya analizi yapar (file_analyzer plugin).", ""),
                "/stats <dosya>": ("Dosya istatistikleri.", ""),
                "/hash <dosya>": ("Dosya hash değeri.", ""),
                "/find <pattern>": ("Dosya arar.", "")
            }
        },
        "tema": {
            "desc": "Tema yönetimi",
            "commands": {
                "/theme": ("Temaları listeler.", ""),
                "/theme set <ad>": ("Temayı değiştirir.", "Örnek: /theme set dark"),
                "/theme create <ad> <açıklama>": ("Yeni tema oluşturur.", ""),
                "/theme delete <ad>": ("Temayı siler.", ""),
                "/theme export <ad> <dosya>": ("Temayı dışa aktarır.", ""),
                "/theme import <dosya>": ("Temayı içe aktarır.", ""),
                "/theme current": ("Mevcut temayı gösterir.", "")
            }
        },
        "kısayol": {
            "desc": "Klavye kısayolları",
            "commands": {
                "F1": ("Yardım menüsü.", ""),
                "F2": ("Model değiştir.", ""),
                "F3": ("Geçmişi göster.", ""),
                "F4": ("Dosya listesi.", ""),
                "F5": ("Kod çalıştır.", ""),
                "Ctrl+R": ("Geçmiş arama.", ""),
                "Tab": ("Komut tamamlama.", "")
            }
        }
    }

    # Komut/kategori arama
    if args and len(args) > 0:
        query = args[0].lower()
        # Kategori yardımı
        if query in help_db:
            cat = help_db[query]
            table = Table(title=f"Yardım: {query.title()} ({cat['desc']})")
            table.add_column("Komut", style="cyan")
            table.add_column("Açıklama", style="yellow")
            table.add_column("Örnek", style="green")
            for cmd, (desc, ex) in cat['commands'].items():
                table.add_row(cmd, desc, ex)
            console.print(table)
            return
        # Komut yardımı
        for cat in help_db.values():
            for cmd, (desc, ex) in cat['commands'].items():
                if query in cmd.lower():
                    console.print(Panel(f"[bold cyan]{cmd}[/bold cyan]\n[yellow]{desc}[/yellow]\n[green]{ex}[/green]", title=f"Yardım: {cmd}", border_style="cyan"))
                    return
        # Plugin yardımı
        if query == "plugin" and len(args) > 1:
            plugin_name = args[1]
            from plugin_system import PluginManager
            pm = PluginManager()
            plugin = pm.plugins.get(plugin_name)
            if plugin and hasattr(plugin, 'help'):  # Plugin help metodu varsa
                console.print(Panel(plugin.help(), title=f"Plugin: {plugin_name}", border_style="blue"))
                return
            else:
                console.print(f"[red]Plugin bulunamadı veya yardım yok: {plugin_name}[/red]")
                return
        # Hiçbir şey bulunamazsa
        console.print(f"[red]Yardım bulunamadı: {query}[/red]")
        return

    # Genel yardım menüsü
    table = Table(title="🚀 CortexCLI Gelişmiş Yardım", show_lines=True)
    table.add_column("Kategori", style="magenta")
    table.add_column("Açıklama", style="yellow")
    table.add_column("Örnek Komutlar", style="cyan")
    for cat, val in help_db.items():
        ex = next(iter(val['commands'].keys()))
        table.add_row(cat.title(), val['desc'], ex)
    console.print(table)
    console.print("[dim]Detay için: /help <kategori> veya /help <komut> yazın. Örnek: /help model, /help /run[/dim]")

def show_config():
    """Mevcut yapılandırmayı göster"""
    console.print("[bold blue]⚙️  Mevcut Yapılandırma[/bold blue]")
    console.print("=" * 30)
    
    console.print(f"🤖 Model: {config.get_setting('model')}")
    console.print(f"🌡️  Sıcaklık: {config.get_setting('temperature')}")
    console.print(f"💾 Geçmiş kaydetme: {config.get_setting('save_history')}")
    console.print(f"📁 Geçmiş dosyası: {config.get_setting('history_file')}")
    console.print(f"📝 Sistem prompt: {config.get_setting('system_prompt')[:50]}...")
    console.print(f"🔧 Çok satırlı giriş: {config.get_setting('multi_line')}")
    console.print(f"📂 Çıktı dizini: {config.get_setting('output_dir')}")

def troubleshoot_issues():
    """Sorun giderme menüsünü gösterir"""
    console.print("\n[bold yellow]🔧 Sorun Giderme Menüsü[/bold yellow]")
    
    issues = [
        ("Ollama çalışmıyor", "Ollama servisinin çalıştığından emin olun: ollama serve"),
        ("Model bulunamıyor", "Model listesini kontrol edin: ollama list"),
        ("Bağlantı hatası", "Ollama API'sinin erişilebilir olduğunu kontrol edin"),
        ("Kod çalıştırma hatası", "Python ve gerekli kütüphanelerin yüklü olduğunu kontrol edin"),
        ("Dosya izin hatası", "Dosya izinlerini kontrol edin"),
        ("Bellek yetersiz", "Daha küçük bir model kullanmayı deneyin")
    ]
    
    for i, (issue, solution) in enumerate(issues, 1):
        console.print(f"[cyan]{i}.[/cyan] {issue}")
        console.print(f"    [dim]{solution}[/dim]\n")
    
    choice = Prompt.ask("Sorun numarasını seçin (çıkmak için Enter)", default="")
    if choice.isdigit() and 1 <= int(choice) <= len(issues):
        issue, solution = issues[int(choice) - 1]
        console.print(f"\n[bold yellow]Sorun:[/bold yellow] {issue}")
        console.print(f"[bold green]Çözüm:[/bold green] {solution}")
        
        # Otomatik çözüm önerileri
        if "ollama serve" in solution:
            if Confirm.ask("Ollama servisini başlatmayı denemek ister misiniz?"):
                try:
                    subprocess.run(["ollama", "serve"], timeout=5)
                    console.print("[green]✅ Ollama servisi başlatıldı[/green]")
                except:
                    console.print("[red]❌ Ollama servisi başlatılamadı[/red]")
        elif "ollama list" in solution:
            if Confirm.ask("Model listesini kontrol etmek ister misiniz?"):
                try:
                    result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
                    console.print(Panel(result.stdout, title="📋 Yüklü Modeller"))
                except:
                    console.print("[red]❌ Model listesi alınamadı[/red]")

def handle_advanced_commands(command: str, args: List[str]) -> bool:
    """Gelişmiş komutları işler"""
    if command == '/help':
        show_advanced_help(*args)
        return True
        
    elif command == '/troubleshoot':
        troubleshoot_issues()
        return True
        
    elif command == '/config':
        show_config()
        return True
        
    elif command == '/reset':
        global chat_history
        chat_history = []
        console.print("[green]✅ Sohbet geçmişi sıfırlandı[/green]")
        return True
        
    elif command == '/clear':
        os.system('clear' if os.name == 'posix' else 'cls')
        return True
        
    elif command == '/theme':
        handle_theme_commands(args)
        return True
        
    elif command == '/settings':
        handle_settings_commands(args)
        return True
        
    elif command == '/suggest':
        try:
            from advanced_features import get_code_suggestions, update_context
            
            if not args:
                context = Prompt.ask("Ne yapmak istiyorsunuz? (bağlam)")
            else:
                context = ' '.join(args)
                
            language = Prompt.ask("Programlama dili", default="python")
            suggestions = get_code_suggestions(context, language, limit=5)
            
            if suggestions:
                console.print(f"\n[bold blue]💡 Kod Önerileri ({language})[/bold blue]")
                console.print("=" * 50)
                
                for i, suggestion in enumerate(suggestions, 1):
                    console.print(f"\n[bold green]{i}. {suggestion.description}[/bold green]")
                    console.print(f"   Güven: {suggestion.confidence:.2f}")
                    console.print(f"   Kategori: {suggestion.context}")
                    console.print(f"   Etiketler: {', '.join(suggestion.tags)}")
                    console.print(f"   [dim]```{suggestion.language}\n{suggestion.code}\n```[/dim]")
                    
                    # Kullanıcı seçimi
                    if Confirm.ask(f"Bu öneriyi kullanmak istiyor musunuz?"):
                        # Kodu panoya kopyala veya dosyaya kaydet
                        filename = suggest_filename(suggestion.language, suggestion.code)
                        if save_file_content(filename, suggestion.code):
                            console.print(f"[green]✅ Kod kaydedildi: {filename}[/green]")
            else:
                console.print("[yellow]Bu bağlam için öneri bulunamadı[/yellow]")
                
            update_context(command)
            return True
            
        except ImportError:
            console.print("[red]❌ Gelişmiş özellikler modülü bulunamadı[/red]")
            return True
            
    elif command == '/smart':
        try:
            from advanced_features import suggest_smart_file_operations, update_context
            
            if not args:
                intent = Prompt.ask("Ne yapmak istiyorsunuz? (organize/backup/clean)")
            else:
                intent = ' '.join(args)
                
            current_path = os.getcwd()
            operations = suggest_smart_file_operations(current_path, intent)
            
            if operations:
                console.print(f"\n[bold blue]🤖 Akıllı İşlem Önerileri[/bold blue]")
                console.print("=" * 40)
                
                for i, op in enumerate(operations, 1):
                    console.print(f"\n[bold green]{i}. {op.description}[/bold green]")
                    console.print(f"   Kaynak: {op.source}")
                    if op.destination:
                        console.print(f"   Hedef: {op.destination}")
                    console.print(f"   Risk: {op.risk_level}")
                    console.print(f"   Tahmini süre: {op.estimated_time}s")
                    
                # İşlem seç
                choice = Prompt.ask("Hangi işlemi yapmak istiyorsunuz?", choices=[str(i) for i in range(1, len(operations) + 1)])
                selected_op = operations[int(choice) - 1]
                
                if Confirm.ask(f"'{selected_op.description}' işlemini gerçekleştirmek istediğinizden emin misiniz?"):
                    console.print(f"[green]✅ {selected_op.description} işlemi başlatılıyor...[/green]")
                    # Burada gerçek işlem yapılabilir
                    
            else:
                console.print("[yellow]Bu niyet için öneri bulunamadı[/yellow]")
                
            update_context(command)
            return True
            
        except ImportError:
            console.print("[red]❌ Gelişmiş özellikler modülü bulunamadı[/red]")
            return True
            
    elif command == '/context':
        try:
            from advanced_features import get_context_info, suggest_improvements, update_context
            
            context_info = get_context_info()
            
            console.print("[bold blue]🔍 Bağlam Analizi[/bold blue]")
            console.print("=" * 30)
            
            console.print(f"📁 Mevcut dizin: {context_info.current_directory}")
            console.print(f"📋 Proje tipi: {context_info.project_type or 'Bilinmiyor'}")
            console.print(f"🔧 Git durumu: {context_info.git_status or 'Git yok'}")
            
            if context_info.dependencies:
                console.print(f"📦 Bağımlılıklar: {', '.join(context_info.dependencies[:5])}")
            
            if context_info.recent_files:
                console.print(f"📄 Son dosyalar: {', '.join(context_info.recent_files[:5])}")
            
            if context_info.recent_commands:
                console.print(f"⌨️  Son komutlar: {', '.join(context_info.recent_commands[-3:])}")
            
            # İyileştirme önerileri
            improvements = suggest_improvements(context_info)
            if improvements:
                console.print(f"\n[bold yellow]💡 İyileştirme Önerileri:[/bold yellow]")
                for improvement in improvements:
                    console.print(f"  • {improvement}")
                    
            update_context(command)
            return True
            
        except ImportError:
            console.print("[red]❌ Gelişmiş özellikler modülü bulunamadı[/red]")
            return True
            
    elif command == '/stats':
        try:
            from advanced_features import get_usage_stats, update_context
            
            days = 7
            if args:
                try:
                    days = int(args[0])
                except ValueError:
                    pass
                    
            stats_data = get_usage_stats(days)
            
            console.print(f"[bold blue]📊 Kullanım İstatistikleri (Son {days} gün)[/bold blue]")
            console.print("=" * 50)
            
            # Özellik istatistikleri
            if stats_data["feature_stats"]:
                console.print(f"\n[bold green]Özellik Kullanımı:[/bold green]")
                for feature, data in stats_data["feature_stats"].items():
                    success_rate = data["success_rate"] * 100
                    console.print(f"  • {feature}: {data['count']} kez ({success_rate:.1f}% başarı)")
            else:
                console.print("[yellow]Henüz özellik kullanım verisi yok[/yellow]")
            
            # Dosya işlemleri
            if stats_data["file_operations"]:
                console.print(f"\n[bold green]Dosya İşlemleri:[/bold green]")
                for operation, count in stats_data["file_operations"].items():
                    console.print(f"  • {operation}: {count} kez")
            else:
                console.print("[yellow]Henüz dosya işlem verisi yok[/yellow]")
                
            update_context(command)
            return True
            
        except ImportError:
            console.print("[red]❌ Gelişmiş özellikler modülü bulunamadı[/red]")
            return True
            
    elif command == '/add-suggestion':
        try:
            from advanced_features import add_code_suggestion, update_context
            
            console.print("[bold blue]➕ Yeni Kod Önerisi Ekle[/bold blue]")
            console.print("=" * 30)
            
            language = Prompt.ask("Programlama dili", default="python")
            category = Prompt.ask("Kategori", default="genel")
            description = Prompt.ask("Açıklama")
            code = Prompt.ask("Kod (çok satırlı)")
            tags_input = Prompt.ask("Etiketler (virgülle ayırın)")
            tags = [tag.strip() for tag in tags_input.split(",")]
            
            add_code_suggestion(language, category, code, description, tags)
            console.print("[green]✅ Kod önerisi eklendi[/green]")
            
            update_context(command)
            return True
            
        except ImportError:
            console.print("[red]❌ Gelişmiş özellikler modülü bulunamadı[/red]")
            return True
    
    return False

def handle_theme_commands(args: List[str]):
    """Tema komutlarını işler"""
    if not args:
        # Mevcut temaları listele
        themes = theme_manager.list_themes()
        table = Table(title="🎨 Kullanılabilir Temalar")
        table.add_column("ID", style="cyan")
        table.add_column("Ad", style="magenta")
        table.add_column("Açıklama", style="yellow")
        table.add_column("Durum", style="green")
        
        for theme in themes:
            status = "✅ Aktif" if theme['current'] else "📋 Kullanılabilir"
            table.add_row(theme['id'], theme['name'], theme['description'], status)
        
        console.print(table)
        return
    
    subcommand = args[0].lower()
    
    if subcommand == 'set':
        if len(args) < 2:
            print_themed("Kullanım: /theme set <tema_adı>", "error")
            return
        
        theme_name = args[1]
        if theme_manager.set_theme(theme_name):
            print_themed(f"✅ Tema değiştirildi: {theme_name}", "success")
            # Renkleri yeniden uygula
            global colors
            colors = apply_cli_theme()
        else:
            print_themed(f"❌ Tema bulunamadı: {theme_name}", "error")
    
    elif subcommand == 'current':
        current = theme_manager.get_current_theme()
        print_themed(f"🎨 Mevcut tema: {current.name}", "info")
        print_themed(f"📝 Açıklama: {current.description}", "muted")
    
    elif subcommand == 'create':
        if len(args) < 3:
            print_themed("Kullanım: /theme create <ad> <açıklama>", "error")
            return
        
        name = args[1]
        description = ' '.join(args[2:])
        
        # Basit tema oluşturma (varsayılan renklerle)
        if theme_manager.create_theme(name, description):
            print_themed(f"✅ Tema oluşturuldu: {name}", "success")
        else:
            print_themed(f"❌ Tema oluşturulamadı: {name}", "error")
    
    elif subcommand == 'delete':
        if len(args) < 2:
            print_themed("Kullanım: /theme delete <tema_adı>", "error")
            return
        
        theme_name = args[1]
        if theme_manager.delete_theme(theme_name):
            print_themed(f"✅ Tema silindi: {theme_name}", "success")
        else:
            print_themed(f"❌ Tema silinemedi: {theme_name}", "error")
    
    elif subcommand == 'export':
        if len(args) < 3:
            print_themed("Kullanım: /theme export <tema_adı> <dosya_yolu>", "error")
            return
        
        theme_name = args[1]
        filepath = args[2]
        
        if theme_manager.export_theme(theme_name, filepath):
            print_themed(f"✅ Tema dışa aktarıldı: {filepath}", "success")
        else:
            print_themed(f"❌ Tema dışa aktarılamadı: {theme_name}", "error")
    
    elif subcommand == 'import':
        if len(args) < 2:
            print_themed("Kullanım: /theme import <dosya_yolu>", "error")
            return
        
        filepath = args[1]
        if theme_manager.import_theme(filepath):
            print_themed(f"✅ Tema içe aktarıldı: {filepath}", "success")
        else:
            print_themed(f"❌ Tema içe aktarılamadı: {filepath}", "error")
    
    else:
        print_themed(f"❌ Bilinmeyen tema komutu: {subcommand}", "error")
        print_themed("Kullanılabilir komutlar: set, current, create, delete, export, import", "info")

def handle_settings_commands(args: List[str]):
    """Ayarlar komutlarını işler"""
    if not args:
        # Ayarlar özetini göster
        profile = get_user_profile()
        preferences = get_user_preferences()
        stats = get_user_stats()
        
        table = Table(title="⚙️ Kullanıcı Ayarları")
        table.add_column("Kategori", style="cyan")
        table.add_column("Değer", style="yellow")
        
        table.add_row("Kullanıcı Adı", profile.username)
        table.add_row("Varsayılan Model", preferences.default_model)
        table.add_row("Varsayılan Sıcaklık", str(preferences.default_temperature))
        table.add_row("Tema", profile.preferred_theme)
        table.add_row("Toplam Sorgu", str(stats.total_queries))
        table.add_row("Kod Çalıştırma", str(stats.total_code_executions))
        
        console.print(table)
        return
    
    subcommand = args[0].lower()
    
    if subcommand == 'profile':
        if len(args) < 3:
            print_themed("Kullanım: /settings profile <alan> <değer>", "error")
            return
        
        field = args[1]
        value = ' '.join(args[2:])
        
        if hasattr(user_settings.profile, field):
            user_settings.update_profile(**{field: value})
            print_themed(f"✅ Profil güncellendi: {field} = {value}", "success")
        else:
            print_themed(f"❌ Geçersiz profil alanı: {field}", "error")
    
    elif subcommand == 'preference':
        if len(args) < 3:
            print_themed("Kullanım: /settings preference <alan> <değer>", "error")
            return
        
        field = args[1]
        value = ' '.join(args[2:])
        
        # Tip dönüşümü
        if field in ['default_temperature']:
            try:
                value = float(value)
            except:
                print_themed(f"❌ Geçersiz değer: {value}", "error")
                return
        elif field in ['auto_save_code', 'auto_save_history', 'multi_line_input', 'enable_notifications']:
            value = value.lower() in ['true', '1', 'yes', 'evet']
        
        if hasattr(user_settings.preferences, field):
            user_settings.update_preferences(**{field: value})
            print_themed(f"✅ Tercih güncellendi: {field} = {value}", "success")
        else:
            print_themed(f"❌ Geçersiz tercih alanı: {field}", "error")
    
    elif subcommand == 'stats':
        stats_summary = user_settings.get_stats_summary()
        table = Table(title="📊 Kullanım İstatistikleri")
        table.add_column("Metrik", style="cyan")
        table.add_column("Değer", style="yellow")
        
        for key, value in stats_summary.items():
            table.add_row(key.replace('_', ' ').title(), str(value))
        
        console.print(table)
    
    elif subcommand == 'reset':
        if Confirm.ask("İstatistikleri sıfırlamak istediğinizden emin misiniz?"):
            user_settings.reset_stats()
            print_themed("✅ İstatistikler sıfırlandı", "success")
    
    elif subcommand == 'export':
        filepath = args[1] if len(args) > 1 else f"settings_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        if user_settings.export_settings(filepath):
            print_themed(f"✅ Ayarlar dışa aktarıldı: {filepath}", "success")
        else:
            print_themed(f"❌ Dışa aktarma hatası", "error")
    
    elif subcommand == 'import':
        if len(args) < 2:
            print_themed("Kullanım: /settings import <dosya_yolu>", "error")
            return
        
        filepath = args[1]
        if user_settings.import_settings(filepath):
            print_themed(f"✅ Ayarlar içe aktarıldı: {filepath}", "success")
        else:
            print_themed(f"❌ İçe aktarma hatası", "error")
    
    else:
        print_themed(f"❌ Bilinmeyen ayar komutu: {subcommand}", "error")
        print_themed("Kullanılabilir komutlar: profile, preference, stats, reset, export, import", "info")

def handle_model_commands(command: str, args: List[str]) -> bool:
    """Model komutlarını işler"""
    global current_model
    
    if command == '/model':
        if not args:
            console.print("[red]Kullanım: /model <model_adı>[/red]")
            return True
            
        new_model = args[0]
        if new_model in get_available_models():
            current_model = new_model
            console.print(f"[green]✅ Model değiştirildi: {current_model}[/green]")
        else:
            console.print(f"[red]❌ Model bulunamadı: {new_model}[/red]")
            console.print("[dim]Kullanılabilir modeller için /models yazın[/dim]")
        return True
        
    elif command == '/models':
        available = get_available_models()
        if available:
            table = Table(title="📋 Kullanılabilir Modeller")
            table.add_column("Model", style="cyan")
            table.add_column("Durum", style="green")
            
            for model in available:
                status = "✅ Aktif" if model == current_model else "📋 Kullanılabilir"
                table.add_row(model, status)
            
            console.print(table)
        else:
            console.print("[red]❌ Hiç model bulunamadı[/red]")
        return True
        
    elif command == '/install':
        if not args:
            console.print("[red]Kullanım: /install <model_adı>[/red]")
            return True
            
        model_name = args[0]
        console.print(f"[yellow]🔄 {model_name} yükleniyor...[/yellow]")
        
        try:
            with Progress() as progress:
                task = progress.add_task("Model yükleniyor...", total=None)
                subprocess.run(["ollama", "pull", model_name], check=True)
                progress.update(task, completed=True)
            
            console.print(f"[green]✅ Model başarıyla yüklendi: {model_name}[/green]")
        except Exception as e:
            console.print(f"[red]❌ Model yükleme hatası: {e}[/red]")
        return True
        
    elif command == '/system':
        global system_prompt
        if not args:
            console.print("[red]Kullanım: /system <yeni_prompt>[/red]")
            return True
            
        new_prompt = ' '.join(args)
        system_prompt = new_prompt
        console.print(f"[green]✅ Sistem promptu güncellendi[/green]")
        return True
        
    return False

def handle_chat_commands(command: str, args: List[str]) -> bool:
    """Sohbet komutlarını işler"""
    global chat_history
    
    if command == '/history':
        if not chat_history:
            console.print("[dim]Henüz sohbet geçmişi yok[/dim]")
            return True
            
        table = Table(title="💬 Sohbet Geçmişi")
        table.add_column("Tarih", style="cyan")
        table.add_column("Model", style="magenta")
        table.add_column("Kullanıcı", style="green")
        table.add_column("Asistan", style="yellow")
        
        for entry in chat_history[-10:]:  # Son 10 mesaj
            timestamp = entry['timestamp'][:19]  # İlk 19 karakter (YYYY-MM-DD HH:MM:SS)
            user_msg = entry['user'][:50] + "..." if len(entry['user']) > 50 else entry['user']
            assistant_msg = entry['assistant'][:50] + "..." if len(entry['assistant']) > 50 else entry['assistant']
            
            table.add_row(timestamp, entry['model'], user_msg, assistant_msg)
        
        console.print(table)
        return True
        
    elif command == '/save':
        filename = args[0] if args else f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(chat_history, f, ensure_ascii=False, indent=2)
            console.print(f"[green]✅ Sohbet geçmişi kaydedildi: {filename}[/green]")
        except Exception as e:
            console.print(f"[red]❌ Kaydetme hatası: {e}[/red]")
        return True
        
    elif command == '/load':
        if not args:
            console.print("[red]Kullanım: /load <dosya_adı>[/red]")
            return True
            
        filename = args[0]
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                loaded_history = json.load(f)
            chat_history = loaded_history
            console.print(f"[green]✅ Sohbet geçmişi yüklendi: {filename}[/green]")
            console.print(f"[dim]{len(chat_history)} mesaj yüklendi[/dim]")
        except Exception as e:
            console.print(f"[red]❌ Yükleme hatası: {e}[/red]")
        return True
        
    return False

def handle_plugin_commands(command: str, args: List[str]) -> bool:
    """Plugin komutlarını işler"""
    # Plugin komutlarını al
    plugin_commands = plugin_manager.get_plugin_commands()
    
    if command in plugin_commands:
        try:
            # Plugin komutunu çalıştır
            result = plugin_commands[command](*args)
            console.print(Panel(result, title=f"🔌 Plugin: {command}", border_style="blue"))
            
            # İstatistik kaydet
            user_settings.record_plugin_used()
            user_settings.record_command(command)
            return True
        except Exception as e:
            console.print(f"[red]❌ Plugin komut hatası: {e}[/red]")
            return True
            
    elif command == '/plugins':
        # Plugin listesini göster
        plugins = plugin_manager.list_plugins()
        if plugins:
            table = Table(title="🔌 Yüklü Plugin'ler")
            table.add_column("Plugin", style="cyan")
            table.add_column("Versiyon", style="magenta")
            table.add_column("Durum", style="green")
            table.add_column("Açıklama", style="yellow")
            
            for name, info in plugins.items():
                status = "✅ Yüklü" if info["loaded"] else "📦 Mevcut"
                table.add_row(name, info["version"], status, info["description"])
            
            console.print(table)
        else:
            console.print("[dim]Henüz plugin yüklenmemiş[/dim]")
        return True
        
    elif command == '/load':
        if not args:
            console.print("[red]Kullanım: /load <plugin_adı>[/red]")
            return True
            
        plugin_name = args[0]
        if plugin_manager.load_plugin(plugin_name):
            console.print(f"[green]✅ Plugin yüklendi: {plugin_name}[/green]")
        else:
            console.print(f"[red]❌ Plugin yüklenemedi: {plugin_name}[/red]")
        return True
        
    elif command == '/unload':
        if not args:
            console.print("[red]Kullanım: /unload <plugin_adı>[/red]")
            return True
            
        plugin_name = args[0]
        if plugin_manager.unload_plugin(plugin_name):
            console.print(f"[green]✅ Plugin kaldırıldı: {plugin_name}[/green]")
        else:
            console.print(f"[red]❌ Plugin kaldırılamadı: {plugin_name}[/red]")
        return True
        
    return False

def handle_multi_model_commands(command: str, args: List[str]) -> bool:
    """Çoklu model komutlarını işler"""
    if command == '/add-model':
        if len(args) < 2:
            console.print("[red]Kullanım: /add-model <alias> <model_adı>[/red]")
            return True
            
        alias, model_name = args[0], args[1]
        multi_model_manager.add_model(alias, model_name)
        return True
        
    elif command == '/remove-model':
        if not args:
            console.print("[red]Kullanım: /remove-model <alias>[/red]")
            return True
            
        alias = args[0]
        multi_model_manager.remove_model(alias)
        return True
        
    elif command == '/list-models':
        models = multi_model_manager.list_models()
        if models:
            table = Table(title="🤖 Aktif Modeller")
            table.add_column("Alias", style="cyan")
            table.add_column("Model", style="green")
            
            for alias, model_name in models.items():
                table.add_row(alias, model_name)
            
            console.print(table)
        else:
            console.print("[dim]Henüz model eklenmemiş[/dim]")
        return True
        
    elif command == '/compare':
        if not args:
            console.print("[red]Kullanım: /compare <sorgu>[/red]")
            return True
            
        prompt = ' '.join(args)
        multi_model_manager.compare_models(prompt, system_prompt)
        return True
        
    elif command == '/query-model':
        if len(args) < 2:
            console.print("[red]Kullanım: /query-model <alias> <sorgu>[/red]")
            return True
            
        alias = args[0]
        prompt = ' '.join(args[1:])
        
        console.print(f"[yellow]🔄 {alias} modeli sorgulanıyor...[/yellow]")
        result = multi_model_manager.query_single_model(alias, prompt, system_prompt)
        
        if result.error:
            console.print(f"[red]❌ Hata: {result.error}[/red]")
        else:
            console.print(Panel(
                result.response,
                title=f"🤖 {alias} ({result.model_name}) - {result.response_time:.2f}s",
                border_style="blue"
            ))
        return True
        
    elif command == '/metrics':
        multi_model_manager.show_performance_metrics()
        return True
        
    elif command == '/save-comparison':
        filename = args[0] if args else None
        multi_model_manager.save_comparison(filename)
        return True
        
    elif command == '/clear-models':
        multi_model_manager.clear_history()
        return True
        
    return False

def chat_loop():
    """Ana sohbet döngüsü"""
    global chat_history, current_model, system_prompt
    
    # Gelişmiş terminal kurulumu
    session = setup_advanced_terminal()
    
    console.print(f"\n[bold green]🚀 CortexCLI başlatıldı![/bold green]")
    console.print(f"[dim]Model: {current_model} | Sistem: {system_prompt[:50]}...[/dim]")
    console.print(f"[dim]Yardım için /help yazın[/dim]\n")
    
    while True:
        try:
            # Gelişmiş prompt ile kullanıcı girişi
            user_input = session.prompt(f"[bold cyan]🤖 {current_model}[/bold cyan] > ")
            
            if not user_input.strip():
                continue
                
            # Komut kontrolü
            if user_input.startswith('/'):
                parts = user_input.split()
                command = parts[0]
                args = parts[1:] if len(parts) > 1 else []
                
                # Komut işleme
                if handle_advanced_commands(command, args):
                    continue
                elif handle_file_commands(command, args):
                    continue
                elif handle_code_execution(command, args):
                    continue
                elif handle_model_commands(command, args):
                    continue
                elif handle_chat_commands(command, args):
                    continue
                elif handle_plugin_commands(command, args):
                    continue
                elif handle_multi_model_commands(command, args):
                    continue
                elif handle_advanced_code_commands(command, args):
                    continue
                elif command in ['/exit', '/quit']:
                    console.print("[yellow]👋 Görüşürüz![/yellow]")
                    break
                else:
                    console.print(f"[red]Bilinmeyen komut: {command}[/red]")
                    console.print("[dim]Yardım için /help yazın[/dim]")
                    continue
            
            # LLM sorgusu
            console.print(f"[dim]🔄 {current_model} düşünüyor...[/dim]")
            
            try:
                response = query_ollama(user_input, current_model, system_prompt)
                
                if response:
                    # Yanıtı geliştir
                    enhanced_response = enhance_llm_response(response)
                    
                    # Yanıtı göster
                    console.print(Panel(
                        Markdown(enhanced_response),
                        title=f"🤖 {current_model}",
                        border_style="green"
                    ))
                    
                    # Geçmişe ekle
                    if config.SAVE_HISTORY:
                        chat_history.append({
                            'user': user_input,
                            'assistant': response,
                            'timestamp': datetime.now().isoformat(),
                            'model': current_model
                        })
                        
                else:
                    console.print("[red]❌ Yanıt alınamadı[/red]")
                    
            except Exception as e:
                console.print(f"[red]❌ LLM hatası: {e}[/red]")
                console.print("[dim]Sorun giderme için /troubleshoot yazın[/dim]")
                
        except KeyboardInterrupt:
            console.print("\n[yellow]⚠️ Ctrl+C ile çıkılıyor...[/yellow]")
            if Confirm.ask("Çıkmak istediğinizden emin misiniz?"):
                break
        except EOFError:
            console.print("\n[yellow]👋 Görüşürüz![/yellow]")
            break
        except Exception as e:
            console.print(f"[red]❌ Beklenmeyen hata: {e}[/red]")

def query_ollama(prompt: str, model: str, system_prompt: str = None) -> str:
    """Ollama API'si ile LLM sorgusu yapar"""
    try:
        url = f"http://localhost:11434/api/generate"
        payload = {
            "model": model,
            "prompt": prompt,
            "system": system_prompt or "Sen yardımcı bir AI asistanısın.",
            "stream": False
        }
        response = requests.post(url, json=payload, timeout=120)
        response.raise_for_status()
        data = response.json()
        return data.get("response") or data.get("message") or ""
    except Exception as e:
        raise RuntimeError(f"Ollama API hatası: {e}")

def handle_advanced_code_commands(command: str, args: List[str]) -> bool:
    """Gelişmiş kod çalıştırma komutlarını işler"""
    if command == '/run-safe':
        if not args:
            console.print("[red]Kullanım: /run-safe <kod> veya /run-safe --file <dosya>[/red]")
            return True
            
        if args[0] == '--file' and len(args) > 1:
            # Dosyadan kod çalıştır
            file_path = args[1]
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    code = f.read()
                language = Path(file_path).suffix[1:] if Path(file_path).suffix else 'python'
            except Exception as e:
                console.print(f"[red]Dosya okuma hatası: {e}[/red]")
                return True
        else:
            # Doğrudan kod çalıştır
            code = ' '.join(args)
            language = 'python'
        
        console.print(f"[yellow]🔄 Kod güvenli ortamda çalıştırılıyor... ({language})[/yellow]")
        
        with Progress() as progress:
            task = progress.add_task("Kod analiz ediliyor...", total=None)
            result = sandbox_executor.execute_code(code, language)
            progress.update(task, completed=True)
        
        # Sonucu göster
        if result.success:
            console.print(Panel(
                result.output,
                title=f"✅ Başarılı - {result.execution_time:.2f}s",
                border_style="green"
            ))
        else:
            console.print(Panel(
                result.error,
                title=f"❌ Hata - {result.execution_time:.2f}s",
                border_style="red"
            ))
        return True
        
    elif command == '/analyze':
        if not args:
            console.print("[red]Kullanım: /analyze <kod> veya /analyze --file <dosya>[/red]")
            return True
            
        if args[0] == '--file' and len(args) > 1:
            file_path = args[1]
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    code = f.read()
                language = Path(file_path).suffix[1:] if Path(file_path).suffix else 'python'
            except Exception as e:
                console.print(f"[red]Dosya okuma hatası: {e}[/red]")
                return True
        else:
            code = ' '.join(args)
            language = 'python'
            
        # Kod analizi
        analysis = sandbox_executor.analyzer.analyze_code(code, language)
        
        # Analiz sonuçlarını göster
        table = Table(title="📊 Kod Analizi")
        table.add_column("Özellik", style="cyan")
        table.add_column("Değer", style="green")
        
        table.add_row("Dil", analysis['language'])
        table.add_row("Satır", str(analysis['lines']))
        table.add_row("Karakter", str(analysis['characters']))
        table.add_row("Kelime", str(analysis['words']))
        table.add_row("Karmaşıklık", analysis['complexity'])
        table.add_row("Import Sayısı", str(len(analysis['imports'])))
        table.add_row("Fonksiyon Sayısı", str(len(analysis['functions'])))
        table.add_row("Güvenlik Riskleri", str(len(analysis['security_risks'])))
        
        console.print(table)
        
        # Detayları göster
        if analysis['imports']:
            console.print(f"[cyan]📦 Import'lar:[/cyan] {', '.join(analysis['imports'])}")
            
        if analysis['functions']:
            console.print(f"[cyan]🔧 Fonksiyonlar:[/cyan] {', '.join(analysis['functions'])}")
            
        if analysis['security_risks']:
            console.print("[red]⚠️ Güvenlik Riskleri:[/red]")
            for risk in analysis['security_risks']:
                console.print(f"  • {risk}")
                
        return True
        
    elif command == '/notebook':
        if len(args) < 2:
            console.print("[red]Kullanım: /notebook <ad> <kod>[/red]")
            return True
            
        name = args[0]
        code = ' '.join(args[1:])
        
        notebook_path = jupyter_integration.create_notebook(name, code)
        console.print(f"[green]✅ Notebook oluşturuldu: {notebook_path}[/green]")
        return True
        
    elif command == '/add-cell':
        if len(args) < 3:
            console.print("[red]Kullanım: /add-cell <notebook> <kod>[/red]")
            return True
            
        notebook_path = args[0]
        code = ' '.join(args[1:])
        
        if jupyter_integration.add_cell(notebook_path, code):
            console.print(f"[green]✅ Hücre eklendi: {notebook_path}[/green]")
        return True
        
    elif command == '/debug':
        if not args:
            console.print("[red]Kullanım: /debug <kod>[/red]")
            return True
            
        code = ' '.join(args)
        debug_info = code_debugger.debug_code(code)
        
        # Debug bilgilerini göster
        table = Table(title="🐛 Debug Bilgileri")
        table.add_column("Özellik", style="cyan")
        table.add_column("Değer", style="green")
        
        table.add_row("Toplam Satır", str(debug_info['total_lines']))
        table.add_row("Breakpoint Sayısı", str(len(debug_info['breakpoints'])))
        table.add_row("Değişken Sayısı", str(len(debug_info['variables'])))
        
        console.print(table)
        
        # Çalıştırma yolunu göster
        console.print("[cyan]📋 Çalıştırma Yolu:[/cyan]")
        for step in debug_info['execution_path'][:10]:  # İlk 10 satır
            status = "✅" if step['executed'] else "⏸️"
            console.print(f"  {status} {step['line']}: {step['code']}")
            
        if len(debug_info['execution_path']) > 10:
            console.print(f"  ... ve {len(debug_info['execution_path']) - 10} satır daha")
            
        return True
        
    elif command == '/breakpoint':
        if len(args) < 2:
            console.print("[red]Kullanım: /breakpoint <satır> [koşul][/red]")
            return True
            
        try:
            line = int(args[0])
            condition = args[1] if len(args) > 1 else None
            code_debugger.add_breakpoint(line, condition)
            console.print(f"[green]✅ Breakpoint eklendi: satır {line}[/green]")
        except ValueError:
            console.print("[red]❌ Geçersiz satır numarası[/red]")
        return True
        
    return False

def main():
    """Ana CLI fonksiyonu"""
    app = typer.Typer(help="CortexCLI - AI Assistant CLI")
    
    @app.command()
    def start():
        """CortexCLI'yi başlat"""
        start_interactive_shell()
    
    @app.command()
    def web():
        """Web arayüzünü başlat"""
        try:
            from web_interface import WebInterface
            console.print("[bold green]🌐 Web arayüzü başlatılıyor...[/bold green]")
            console.print("[dim]Tarayıcıda http://localhost:5000 adresini açın[/dim]")
            
            web_interface = WebInterface()
            web_interface.start()
        except KeyboardInterrupt:
            console.print("\n[yellow]Web arayüzü kapatılıyor...[/yellow]")
        except Exception as e:
            console.print(f"[red]Web arayüzü hatası: {e}[/red]")

if __name__ == "__main__":
    if len(sys.argv) == 1:
        interactive_start()
    else:
        app() 