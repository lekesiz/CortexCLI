"""
Notes Plugin - Not alma ve yönetimi
Kullanım:
  /note add <başlık> | <içerik>
  /note list [kategori]
  /note search <anahtar_kelime>
  /note show <id>
  /note delete <id>
  /note categories
"""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

NOTES_FILE = "notes.json"

def load_notes() -> List[Dict[str, Any]]:
    """Notları dosyadan yükler."""
    if os.path.exists(NOTES_FILE):
        try:
            with open(NOTES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def save_notes(notes: List[Dict[str, Any]]) -> None:
    """Notları dosyaya kaydeder."""
    with open(NOTES_FILE, 'w', encoding='utf-8') as f:
        json.dump(notes, f, ensure_ascii=False, indent=2)

def add_note(title: str, content: str, category: str = "genel") -> str:
    """Yeni not ekler."""
    try:
        notes = load_notes()
        
        note = {
            "id": len(notes) + 1,
            "title": title,
            "content": content,
            "category": category,
            "created": datetime.now().isoformat(),
            "tags": []
        }
        
        notes.append(note)
        save_notes(notes)
        
        return f"[bold green]Not eklendi:[/bold green] {title} (ID: {note['id']})"
    except Exception as e:
        return f"[HATA] Not ekleme hatası: {e}"

def list_notes(category: str = None) -> str:
    """Notları listeler."""
    try:
        notes = load_notes()
        
        if not notes:
            return "[yellow]Henüz not yok.[/yellow]"
        
        if category:
            notes = [n for n in notes if n.get('category', '').lower() == category.lower()]
        
        if not notes:
            return f"[yellow]'{category}' kategorisinde not bulunamadı.[/yellow]"
        
        result = "[bold]Notlar:[/bold]\n"
        for note in notes:
            created = datetime.fromisoformat(note['created']).strftime('%Y-%m-%d %H:%M')
            result += f"[bold]{note['id']}.[/bold] {note['title']} ({note['category']}) - {created}\n"
        
        return result
    except Exception as e:
        return f"[HATA] Not listeleme hatası: {e}"

def search_notes(keyword: str) -> str:
    """Notlarda arama yapar."""
    try:
        notes = load_notes()
        
        if not notes:
            return "[yellow]Henüz not yok.[/yellow]"
        
        keyword = keyword.lower()
        found_notes = []
        
        for note in notes:
            if (keyword in note['title'].lower() or 
                keyword in note['content'].lower() or
                keyword in note.get('category', '').lower()):
                found_notes.append(note)
        
        if not found_notes:
            return f"[yellow]'{keyword}' için sonuç bulunamadı.[/yellow]"
        
        result = f"[bold]'{keyword}' için bulunan notlar:[/bold]\n"
        for note in found_notes:
            created = datetime.fromisoformat(note['created']).strftime('%Y-%m-%d %H:%M')
            result += f"[bold]{note['id']}.[/bold] {note['title']} ({note['category']}) - {created}\n"
        
        return result
    except Exception as e:
        return f"[HATA] Arama hatası: {e}"

def show_note(note_id: str) -> str:
    """Belirtilen notu gösterir."""
    try:
        notes = load_notes()
        note_id = int(note_id)
        
        for note in notes:
            if note['id'] == note_id:
                created = datetime.fromisoformat(note['created']).strftime('%Y-%m-%d %H:%M')
                result = f"""
[bold]{note['title']}[/bold]
Kategori: {note['category']}
Oluşturulma: {created}
ID: {note['id']}

[bold]İçerik:[/bold]
{note['content']}
"""
                return result
        
        return f"[HATA] ID {note_id} ile not bulunamadı."
    except Exception as e:
        return f"[HATA] Not gösterme hatası: {e}"

def delete_note(note_id: str) -> str:
    """Notu siler."""
    try:
        notes = load_notes()
        note_id = int(note_id)
        
        for i, note in enumerate(notes):
            if note['id'] == note_id:
                deleted_title = note['title']
                del notes[i]
                save_notes(notes)
                return f"[bold green]Not silindi:[/bold green] {deleted_title}"
        
        return f"[HATA] ID {note_id} ile not bulunamadı."
    except Exception as e:
        return f"[HATA] Not silme hatası: {e}"

def categories() -> str:
    """Mevcut kategorileri listeler."""
    try:
        notes = load_notes()
        
        if not notes:
            return "[yellow]Henüz not yok.[/yellow]"
        
        categories = {}
        for note in notes:
            cat = note.get('category', 'genel')
            categories[cat] = categories.get(cat, 0) + 1
        
        result = "[bold]Kategoriler:[/bold]\n"
        for cat, count in sorted(categories.items()):
            result += f"• {cat}: {count} not\n"
        
        return result
    except Exception as e:
        return f"[HATA] Kategori listeleme hatası: {e}"

def help():
    return """
/note add <başlık> | <içerik>\n  Yeni not ekler.\n/note list [kategori]\n  Notları listeler.\n/note search <anahtar_kelime>\n  Notlarda arama yapar.\n/note show <id>\n  Belirtilen notu gösterir.\n/note delete <id>\n  Notu siler.\n/note categories\n  Kategorileri listeler.\nÖrnek: /note add Alışveriş | Süt, ekmek, yumurta al\nÖrnek: /note search alışveriş\n"""

commands = {
    '/note': lambda *args: handle_note_command(*args)
}

def handle_note_command(*args):
    """Not komutlarını yönlendirir."""
    if not args:
        return help()
    
    subcommand = args[0].lower()
    
    if subcommand == 'add':
        if len(args) < 3:
            return "[HATA] Kullanım: /note add <başlık> | <içerik>"
        title = args[1]
        content = ' '.join(args[2:])
        return add_note(title, content)
    
    elif subcommand == 'list':
        category = args[1] if len(args) > 1 else None
        return list_notes(category)
    
    elif subcommand == 'search':
        if len(args) < 2:
            return "[HATA] Kullanım: /note search <anahtar_kelime>"
        keyword = ' '.join(args[1:])
        return search_notes(keyword)
    
    elif subcommand == 'show':
        if len(args) < 2:
            return "[HATA] Kullanım: /note show <id>"
        return show_note(args[1])
    
    elif subcommand == 'delete':
        if len(args) < 2:
            return "[HATA] Kullanım: /note delete <id>"
        return delete_note(args[1])
    
    elif subcommand == 'categories':
        return categories()
    
    else:
        return help()

class NotesPlugin:
    """Notes Plugin - Not alma ve yönetimi."""
    
    def __init__(self):
        self.name = "Notes"
        self.description = "Not alma ve yönetimi"
        self.commands = commands
        self.help_text = help()
    
    def execute(self, command: str, args: list) -> str:
        """Komutu çalıştırır."""
        if command in self.commands:
            try:
                return self.commands[command](*args)
            except Exception as e:
                return f"[HATA] Komut çalıştırma hatası: {e}"
        else:
            return f"[HATA] Bilinmeyen komut: {command}"
    
    def get_help(self) -> str:
        """Yardım metnini döndürür."""
        return self.help_text 