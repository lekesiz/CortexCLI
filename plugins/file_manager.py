"""
Advanced File Manager Plugin - Gelişmiş dosya yönetimi
Kullanım:
  /files list [dizin] [--pattern <pattern>] [--type <type>]
  /files preview <dosya>
  /files search <anahtar_kelime> [dizin]
  /files find <dosya_adı> [dizin]
  /files info <dosya>
  /files copy <kaynak> <hedef>
  /files move <kaynak> <hedef>
  /files rename <eski_ad> <yeni_ad>
  /files delete <dosya> [--force]
  /files mkdir <dizin>
  /files tree [dizin] [--depth <depth>]
"""
import os
import shutil
import mimetypes
import hashlib
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
import fnmatch

def list_files(directory: str = ".", pattern: str = "*", file_type: str = "all") -> str:
    """Dosyaları listeler ve filtreler."""
    try:
        dir_path = Path(directory).resolve()
        if not dir_path.exists():
            return f"[HATA] Dizin bulunamadı: {directory}"
        
        files = []
        for item in dir_path.iterdir():
            if fnmatch.fnmatch(item.name, pattern):
                if file_type == "all" or \
                   (file_type == "file" and item.is_file()) or \
                   (file_type == "dir" and item.is_dir()):
                    files.append(item)
        
        if not files:
            return f"[yellow]'{directory}' dizininde dosya bulunamadı.[/yellow]"
        
        # Dosyaları sırala (önce dizinler, sonra dosyalar)
        files.sort(key=lambda x: (not x.is_dir(), x.name.lower()))
        
        result = f"[bold]Dosyalar ({directory}):[/bold]\n"
        for item in files:
            try:
                stat = item.stat()
                size = stat.st_size
                modified = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M')
                
                if item.is_dir():
                    result += f"[blue]📁 {item.name}/[/blue] - {modified}\n"
                else:
                    # Dosya boyutunu formatla
                    if size < 1024:
                        size_str = f"{size} B"
                    elif size < 1024**2:
                        size_str = f"{size/1024:.1f} KB"
                    elif size < 1024**3:
                        size_str = f"{size/1024**2:.1f} MB"
                    else:
                        size_str = f"{size/1024**3:.1f} GB"
                    
                    result += f"📄 {item.name} - {size_str} - {modified}\n"
            except Exception as e:
                result += f"❓ {item.name} - Erişim hatası\n"
        
        return result
    except Exception as e:
        return f"[HATA] Dosya listeleme hatası: {e}"

def preview_file(file_path: str, max_lines: int = 50) -> str:
    """Dosya önizlemesi gösterir."""
    try:
        file_path = Path(file_path).resolve()
        if not file_path.exists():
            return f"[HATA] Dosya bulunamadı: {file_path}"
        
        if not file_path.is_file():
            return f"[HATA] Bu bir dosya değil: {file_path}"
        
        # Dosya boyutunu kontrol et
        size = file_path.stat().st_size
        if size > 10 * 1024 * 1024:  # 10MB
            return f"[HATA] Dosya çok büyük ({size/1024/1024:.1f} MB). Önizleme için çok büyük."
        
        # MIME tipini kontrol et
        mime_type, _ = mimetypes.guess_type(str(file_path))
        if mime_type and not mime_type.startswith('text/'):
            return f"[HATA] Metin dosyası değil: {mime_type}"
        
        # Dosyayı oku
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except UnicodeDecodeError:
            return f"[HATA] Dosya UTF-8 formatında değil."
        
        if not lines:
            return f"[yellow]Dosya boş: {file_path.name}[/yellow]"
        
        # İlk ve son birkaç satırı göster
        preview_lines = lines[:max_lines//2]
        if len(lines) > max_lines:
            preview_lines.append(f"\n... ({len(lines) - max_lines} satır atlandı) ...\n")
            preview_lines.extend(lines[-max_lines//2:])
        
        result = f"[bold]Dosya Önizlemesi: {file_path.name}[/bold]\n"
        result += f"Boyut: {size:,} B, Satır: {len(lines)}\n"
        result += "─" * 50 + "\n"
        result += ''.join(preview_lines)
        
        return result
    except Exception as e:
        return f"[HATA] Dosya önizleme hatası: {e}"

def search_files(keyword: str, directory: str = ".") -> str:
    """Dosya içeriğinde arama yapar."""
    try:
        dir_path = Path(directory).resolve()
        if not dir_path.exists():
            return f"[HATA] Dizin bulunamadı: {directory}"
        
        keyword = keyword.lower()
        found_files = []
        
        for file_path in dir_path.rglob("*"):
            if file_path.is_file():
                try:
                    # Dosya boyutunu kontrol et
                    if file_path.stat().st_size > 5 * 1024 * 1024:  # 5MB
                        continue
                    
                    # MIME tipini kontrol et
                    mime_type, _ = mimetypes.guess_type(str(file_path))
                    if mime_type and not mime_type.startswith('text/'):
                        continue
                    
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read().lower()
                        if keyword in content:
                            found_files.append(file_path)
                except:
                    continue
        
        if not found_files:
            return f"[yellow]'{keyword}' için sonuç bulunamadı.[/yellow]"
        
        result = f"[bold]'{keyword}' için bulunan dosyalar:[/bold]\n"
        for file_path in found_files[:20]:  # En fazla 20 sonuç
            result += f"📄 {file_path.relative_to(dir_path)}\n"
        
        if len(found_files) > 20:
            result += f"\n... ve {len(found_files) - 20} dosya daha"
        
        return result
    except Exception as e:
        return f"[HATA] Arama hatası: {e}"

def find_files(filename: str, directory: str = ".") -> str:
    """Dosya adına göre arama yapar."""
    try:
        dir_path = Path(directory).resolve()
        if not dir_path.exists():
            return f"[HATA] Dizin bulunamadı: {directory}"
        
        found_files = list(dir_path.rglob(filename))
        
        if not found_files:
            return f"[yellow]'{filename}' adında dosya bulunamadı.[/yellow]"
        
        result = f"[bold]'{filename}' adında bulunan dosyalar:[/bold]\n"
        for file_path in found_files:
            try:
                stat = file_path.stat()
                size = stat.st_size
                modified = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M')
                
                if size < 1024:
                    size_str = f"{size} B"
                elif size < 1024**2:
                    size_str = f"{size/1024:.1f} KB"
                else:
                    size_str = f"{size/1024**2:.1f} MB"
                
                result += f"📄 {file_path.relative_to(dir_path)} - {size_str} - {modified}\n"
            except:
                result += f"📄 {file_path.relative_to(dir_path)}\n"
        
        return result
    except Exception as e:
        return f"[HATA] Dosya bulma hatası: {e}"

def file_info(file_path: str) -> str:
    """Dosya hakkında detaylı bilgi verir."""
    try:
        file_path = Path(file_path).resolve()
        if not file_path.exists():
            return f"[HATA] Dosya bulunamadı: {file_path}"
        
        stat = file_path.stat()
        mime_type, encoding = mimetypes.guess_type(str(file_path))
        
        # Dosya boyutunu formatla
        size = stat.st_size
        if size < 1024:
            size_str = f"{size} B"
        elif size < 1024**2:
            size_str = f"{size/1024:.1f} KB"
        elif size < 1024**3:
            size_str = f"{size/1024**2:.1f} MB"
        else:
            size_str = f"{size/1024**3:.1f} GB"
        
        # Dosya hash'i hesapla (küçük dosyalar için)
        file_hash = ""
        if size < 1024 * 1024:  # 1MB'dan küçük dosyalar
            try:
                with open(file_path, 'rb') as f:
                    file_hash = hashlib.md5(f.read()).hexdigest()[:8]
            except:
                pass
        
        result = f"""
[bold]Dosya Bilgileri: {file_path.name}[/bold]

📁 Yol: {file_path}
📏 Boyut: {size_str} ({size:,} B)
📅 Oluşturulma: {datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S')}
📝 Değiştirilme: {datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')}
🔐 İzinler: {oct(stat.st_mode)[-3:]}
"""
        
        if mime_type:
            result += f"📋 MIME Tipi: {mime_type}\n"
        if encoding:
            result += f"🔤 Kodlama: {encoding}\n"
        if file_hash:
            result += f"🔍 Hash: {file_hash}\n"
        
        if file_path.is_dir():
            try:
                file_count = len(list(file_path.rglob("*")))
                dir_count = len([x for x in file_path.rglob("*") if x.is_dir()])
                result += f"📊 İçerik: {file_count} dosya, {dir_count} dizin\n"
            except:
                pass
        
        return result
    except Exception as e:
        return f"[HATA] Dosya bilgisi hatası: {e}"

def copy_file(source: str, destination: str) -> str:
    """Dosya kopyalar."""
    try:
        source_path = Path(source).resolve()
        dest_path = Path(destination).resolve()
        
        if not source_path.exists():
            return f"[HATA] Kaynak dosya bulunamadı: {source}"
        
        if dest_path.exists() and dest_path.is_file():
            return f"[HATA] Hedef dosya zaten mevcut: {destination}"
        
        shutil.copy2(source_path, dest_path)
        return f"[bold green]Dosya kopyalandı:[/bold green] {source} → {destination}"
    except Exception as e:
        return f"[HATA] Kopyalama hatası: {e}"

def move_file(source: str, destination: str) -> str:
    """Dosya taşır."""
    try:
        source_path = Path(source).resolve()
        dest_path = Path(destination).resolve()
        
        if not source_path.exists():
            return f"[HATA] Kaynak dosya bulunamadı: {source}"
        
        if dest_path.exists():
            return f"[HATA] Hedef dosya zaten mevcut: {destination}"
        
        shutil.move(str(source_path), str(dest_path))
        return f"[bold green]Dosya taşındı:[/bold green] {source} → {destination}"
    except Exception as e:
        return f"[HATA] Taşıma hatası: {e}"

def rename_file(old_name: str, new_name: str) -> str:
    """Dosya adını değiştirir."""
    try:
        old_path = Path(old_name).resolve()
        new_path = Path(new_name).resolve()
        
        if not old_path.exists():
            return f"[HATA] Dosya bulunamadı: {old_name}"
        
        if new_path.exists():
            return f"[HATA] Yeni ad zaten mevcut: {new_name}"
        
        old_path.rename(new_path)
        return f"[bold green]Dosya adı değiştirildi:[/bold green] {old_name} → {new_name}"
    except Exception as e:
        return f"[HATA] Ad değiştirme hatası: {e}"

def delete_file(file_path: str, force: bool = False) -> str:
    """Dosya siler."""
    try:
        path = Path(file_path).resolve()
        
        if not path.exists():
            return f"[HATA] Dosya bulunamadı: {file_path}"
        
        if path.is_dir():
            if not force:
                return f"[HATA] Dizin silmek için --force kullanın: {file_path}"
            shutil.rmtree(path)
            return f"[bold green]Dizin silindi:[/bold green] {file_path}"
        else:
            path.unlink()
            return f"[bold green]Dosya silindi:[/bold green] {file_path}"
    except Exception as e:
        return f"[HATA] Silme hatası: {e}"

def make_directory(dir_name: str) -> str:
    """Dizin oluşturur."""
    try:
        dir_path = Path(dir_name).resolve()
        
        if dir_path.exists():
            return f"[HATA] Dizin zaten mevcut: {dir_name}"
        
        dir_path.mkdir(parents=True, exist_ok=True)
        return f"[bold green]Dizin oluşturuldu:[/bold green] {dir_name}"
    except Exception as e:
        return f"[HATA] Dizin oluşturma hatası: {e}"

def tree_view(directory: str = ".", max_depth: int = 3) -> str:
    """Dizin ağacını gösterir."""
    try:
        dir_path = Path(directory).resolve()
        if not dir_path.exists():
            return f"[HATA] Dizin bulunamadı: {directory}"
        
        if not dir_path.is_dir():
            return f"[HATA] Bu bir dizin değil: {directory}"
        
        result = f"[bold]Dizin Ağacı: {directory}[/bold]\n"
        
        def print_tree(path: Path, prefix: str = "", depth: int = 0):
            nonlocal result
            if depth > max_depth:
                return
            
            items = sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
            
            for i, item in enumerate(items):
                is_last = i == len(items) - 1
                current_prefix = "└── " if is_last else "├── "
                next_prefix = "    " if is_last else "│   "
                
                if item.is_dir():
                    result += f"{prefix}{current_prefix}[blue]{item.name}/[/blue]\n"
                    print_tree(item, prefix + next_prefix, depth + 1)
                else:
                    result += f"{prefix}{current_prefix}{item.name}\n"
        
        print_tree(dir_path)
        return result
    except Exception as e:
        return f"[HATA] Ağaç görünümü hatası: {e}"

def help():
    return """
/files list [dizin] [--pattern <pattern>] [--type <type>]\n  Dosyaları listeler ve filtreler.\n/files preview <dosya>\n  Dosya önizlemesi gösterir.\n/files search <anahtar_kelime> [dizin]\n  Dosya içeriğinde arama yapar.\n/files find <dosya_adı> [dizin]\n  Dosya adına göre arama yapar.\n/files info <dosya>\n  Dosya hakkında detaylı bilgi verir.\n/files copy <kaynak> <hedef>\n  Dosya kopyalar.\n/files move <kaynak> <hedef>\n  Dosya taşır.\n/files rename <eski_ad> <yeni_ad>\n  Dosya adını değiştirir.\n/files delete <dosya> [--force]\n  Dosya siler.\n/files mkdir <dizin>\n  Dizin oluşturur.\n/files tree [dizin] [--depth <depth>]\n  Dizin ağacını gösterir.\nÖrnek: /files list . --pattern "*.py"\nÖrnek: /files preview script.py\nÖrnek: /files search "import"\n"""

commands = {
    '/files': lambda *args: handle_file_command(*args)
}

def handle_file_command(*args):
    """Dosya komutlarını yönlendirir."""
    if not args:
        return help()
    
    subcommand = args[0].lower()
    
    if subcommand == 'list':
        directory = args[1] if len(args) > 1 else "."
        pattern = "*"
        file_type = "all"
        
        # Argümanları parse et
        i = 2
        while i < len(args):
            if args[i] == '--pattern' and i + 1 < len(args):
                pattern = args[i + 1]
                i += 2
            elif args[i] == '--type' and i + 1 < len(args):
                file_type = args[i + 1]
                i += 2
            else:
                i += 1
        
        return list_files(directory, pattern, file_type)
    
    elif subcommand == 'preview':
        if len(args) < 2:
            return "[HATA] Kullanım: /files preview <dosya>"
        return preview_file(args[1])
    
    elif subcommand == 'search':
        if len(args) < 2:
            return "[HATA] Kullanım: /files search <anahtar_kelime> [dizin]"
        keyword = args[1]
        directory = args[2] if len(args) > 2 else "."
        return search_files(keyword, directory)
    
    elif subcommand == 'find':
        if len(args) < 2:
            return "[HATA] Kullanım: /files find <dosya_adı> [dizin]"
        filename = args[1]
        directory = args[2] if len(args) > 2 else "."
        return find_files(filename, directory)
    
    elif subcommand == 'info':
        if len(args) < 2:
            return "[HATA] Kullanım: /files info <dosya>"
        return file_info(args[1])
    
    elif subcommand == 'copy':
        if len(args) < 3:
            return "[HATA] Kullanım: /files copy <kaynak> <hedef>"
        return copy_file(args[1], args[2])
    
    elif subcommand == 'move':
        if len(args) < 3:
            return "[HATA] Kullanım: /files move <kaynak> <hedef>"
        return move_file(args[1], args[2])
    
    elif subcommand == 'rename':
        if len(args) < 3:
            return "[HATA] Kullanım: /files rename <eski_ad> <yeni_ad>"
        return rename_file(args[1], args[2])
    
    elif subcommand == 'delete':
        if len(args) < 2:
            return "[HATA] Kullanım: /files delete <dosya> [--force]"
        force = '--force' in args
        return delete_file(args[1], force)
    
    elif subcommand == 'mkdir':
        if len(args) < 2:
            return "[HATA] Kullanım: /files mkdir <dizin>"
        return make_directory(args[1])
    
    elif subcommand == 'tree':
        directory = args[1] if len(args) > 1 else "."
        max_depth = 3
        if len(args) > 2 and args[2] == '--depth' and len(args) > 3:
            try:
                max_depth = int(args[3])
            except:
                pass
        return tree_view(directory, max_depth)
    
    else:
        return help() 