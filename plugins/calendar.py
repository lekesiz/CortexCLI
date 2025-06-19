"""
Calendar Plugin - Takvim ve etkinlik yönetimi
Kullanım:
  /calendar add <başlık> | <tarih> | <açıklama>
  /calendar list [tarih]
  /calendar today
  /calendar week
  /calendar month
  /calendar search <anahtar_kelime>
  /calendar delete <id>
  /calendar reminder <id> <dakika>
"""
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any

CALENDAR_FILE = "calendar.json"

def load_events() -> List[Dict[str, Any]]:
    """Etkinlikleri dosyadan yükler."""
    if os.path.exists(CALENDAR_FILE):
        try:
            with open(CALENDAR_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def save_events(events: List[Dict[str, Any]]) -> None:
    """Etkinlikleri dosyaya kaydeder."""
    with open(CALENDAR_FILE, 'w', encoding='utf-8') as f:
        json.dump(events, f, ensure_ascii=False, indent=2)

def add_event(title: str, date_str: str, description: str = "") -> str:
    """Yeni etkinlik ekler."""
    try:
        events = load_events()
        
        # Tarih formatını parse et
        try:
            if ' ' in date_str:
                event_date = datetime.strptime(date_str, '%Y-%m-%d %H:%M')
            else:
                event_date = datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            return "[HATA] Geçersiz tarih formatı. Kullanım: YYYY-MM-DD veya YYYY-MM-DD HH:MM"
        
        event = {
            "id": len(events) + 1,
            "title": title,
            "date": event_date.isoformat(),
            "description": description,
            "created": datetime.now().isoformat(),
            "reminder": None
        }
        
        events.append(event)
        save_events(events)
        
        return f"[bold green]Etkinlik eklendi:[/bold green] {title} ({event_date.strftime('%Y-%m-%d %H:%M')})"
    except Exception as e:
        return f"[HATA] Etkinlik ekleme hatası: {e}"

def list_events(date_filter: str = None) -> str:
    """Etkinlikleri listeler."""
    try:
        events = load_events()
        
        if not events:
            return "[yellow]Henüz etkinlik yok.[/yellow]"
        
        if date_filter:
            try:
                filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
                events = [e for e in events if datetime.fromisoformat(e['date']).date() == filter_date]
            except ValueError:
                return "[HATA] Geçersiz tarih formatı. Kullanım: YYYY-MM-DD"
        
        if not events:
            return f"[yellow]'{date_filter}' tarihinde etkinlik bulunamadı.[/yellow]"
        
        # Tarihe göre sırala
        events.sort(key=lambda x: x['date'])
        
        result = "[bold]Etkinlikler:[/bold]\n"
        for event in events:
            event_date = datetime.fromisoformat(event['date'])
            result += f"[bold]{event['id']}.[/bold] {event['title']} - {event_date.strftime('%Y-%m-%d %H:%M')}\n"
            if event['description']:
                result += f"  {event['description']}\n"
        
        return result
    except Exception as e:
        return f"[HATA] Etkinlik listeleme hatası: {e}"

def today_events() -> str:
    """Bugünkü etkinlikleri gösterir."""
    today = datetime.now().strftime('%Y-%m-%d')
    return list_events(today)

def week_events() -> str:
    """Bu haftaki etkinlikleri gösterir."""
    try:
        events = load_events()
        
        if not events:
            return "[yellow]Henüz etkinlik yok.[/yellow]"
        
        today = datetime.now().date()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        
        week_events = []
        for event in events:
            event_date = datetime.fromisoformat(event['date']).date()
            if week_start <= event_date <= week_end:
                week_events.append(event)
        
        if not week_events:
            return "[yellow]Bu hafta etkinlik yok.[/yellow]"
        
        # Tarihe göre sırala
        week_events.sort(key=lambda x: x['date'])
        
        result = f"[bold]Bu Hafta ({week_start.strftime('%Y-%m-%d')} - {week_end.strftime('%Y-%m-%d')}):[/bold]\n"
        for event in week_events:
            event_date = datetime.fromisoformat(event['date'])
            day_name = event_date.strftime('%A')
            result += f"[bold]{event['id']}.[/bold] [{day_name}] {event['title']} - {event_date.strftime('%H:%M')}\n"
            if event['description']:
                result += f"  {event['description']}\n"
        
        return result
    except Exception as e:
        return f"[HATA] Haftalık etkinlik hatası: {e}"

def month_events() -> str:
    """Bu ayki etkinlikleri gösterir."""
    try:
        events = load_events()
        
        if not events:
            return "[yellow]Henüz etkinlik yok.[/yellow]"
        
        today = datetime.now().date()
        month_start = today.replace(day=1)
        if today.month == 12:
            month_end = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            month_end = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
        
        month_events = []
        for event in events:
            event_date = datetime.fromisoformat(event['date']).date()
            if month_start <= event_date <= month_end:
                month_events.append(event)
        
        if not month_events:
            return "[yellow]Bu ay etkinlik yok.[/yellow]"
        
        # Tarihe göre sırala
        month_events.sort(key=lambda x: x['date'])
        
        result = f"[bold]Bu Ay ({month_start.strftime('%Y-%m')}):[/bold]\n"
        for event in month_events:
            event_date = datetime.fromisoformat(event['date'])
            result += f"[bold]{event['id']}.[/bold] {event_date.strftime('%d')} - {event['title']} ({event_date.strftime('%H:%M')})\n"
            if event['description']:
                result += f"  {event['description']}\n"
        
        return result
    except Exception as e:
        return f"[HATA] Aylık etkinlik hatası: {e}"

def search_events(keyword: str) -> str:
    """Etkinliklerde arama yapar."""
    try:
        events = load_events()
        
        if not events:
            return "[yellow]Henüz etkinlik yok.[/yellow]"
        
        keyword = keyword.lower()
        found_events = []
        
        for event in events:
            if (keyword in event['title'].lower() or 
                keyword in event.get('description', '').lower()):
                found_events.append(event)
        
        if not found_events:
            return f"[yellow]'{keyword}' için sonuç bulunamadı.[/yellow]"
        
        # Tarihe göre sırala
        found_events.sort(key=lambda x: x['date'])
        
        result = f"[bold]'{keyword}' için bulunan etkinlikler:[/bold]\n"
        for event in found_events:
            event_date = datetime.fromisoformat(event['date'])
            result += f"[bold]{event['id']}.[/bold] {event['title']} - {event_date.strftime('%Y-%m-%d %H:%M')}\n"
            if event['description']:
                result += f"  {event['description']}\n"
        
        return result
    except Exception as e:
        return f"[HATA] Arama hatası: {e}"

def delete_event(event_id: str) -> str:
    """Etkinliği siler."""
    try:
        events = load_events()
        event_id = int(event_id)
        
        for i, event in enumerate(events):
            if event['id'] == event_id:
                deleted_title = event['title']
                del events[i]
                save_events(events)
                return f"[bold green]Etkinlik silindi:[/bold green] {deleted_title}"
        
        return f"[HATA] ID {event_id} ile etkinlik bulunamadı."
    except Exception as e:
        return f"[HATA] Etkinlik silme hatası: {e}"

def set_reminder(event_id: str, minutes: str) -> str:
    """Etkinlik için hatırlatıcı ayarlar."""
    try:
        events = load_events()
        event_id = int(event_id)
        reminder_minutes = int(minutes)
        
        for event in events:
            if event['id'] == event_id:
                event['reminder'] = reminder_minutes
                save_events(events)
                return f"[bold green]Hatırlatıcı ayarlandı:[/bold green] {event['title']} ({reminder_minutes} dakika önce)"
        
        return f"[HATA] ID {event_id} ile etkinlik bulunamadı."
    except Exception as e:
        return f"[HATA] Hatırlatıcı ayarlama hatası: {e}"

def upcoming_events() -> str:
    """Yaklaşan etkinlikleri gösterir."""
    try:
        events = load_events()
        
        if not events:
            return "[yellow]Henüz etkinlik yok.[/yellow]"
        
        now = datetime.now()
        upcoming = []
        
        for event in events:
            event_date = datetime.fromisoformat(event['date'])
            if event_date > now:
                upcoming.append(event)
        
        if not upcoming:
            return "[yellow]Yaklaşan etkinlik yok.[/yellow]"
        
        # Tarihe göre sırala
        upcoming.sort(key=lambda x: x['date'])
        
        result = "[bold]Yaklaşan Etkinlikler:[/bold]\n"
        for event in upcoming[:10]:  # En fazla 10 etkinlik
            event_date = datetime.fromisoformat(event['date'])
            time_diff = event_date - now
            days = time_diff.days
            hours = time_diff.seconds // 3600
            
            if days > 0:
                time_str = f"{days} gün sonra"
            elif hours > 0:
                time_str = f"{hours} saat sonra"
            else:
                time_str = "Bugün"
            
            result += f"[bold]{event['id']}.[/bold] {event['title']} - {event_date.strftime('%Y-%m-%d %H:%M')} ({time_str})\n"
            if event['description']:
                result += f"  {event['description']}\n"
        
        return result
    except Exception as e:
        return f"[HATA] Yaklaşan etkinlik hatası: {e}"

def help():
    return """
/calendar add <başlık> | <tarih> | <açıklama>\n  Yeni etkinlik ekler.\n/calendar list [tarih]\n  Etkinlikleri listeler.\n/calendar today\n  Bugünkü etkinlikleri gösterir.\n/calendar week\n  Bu haftaki etkinlikleri gösterir.\n/calendar month\n  Bu ayki etkinlikleri gösterir.\n/calendar search <anahtar_kelime>\n  Etkinliklerde arama yapar.\n/calendar delete <id>\n  Etkinliği siler.\n/calendar reminder <id> <dakika>\n  Hatırlatıcı ayarlar.\n/calendar upcoming\n  Yaklaşan etkinlikleri gösterir.\nÖrnek: /calendar add Toplantı | 2024-01-15 14:30 | Proje toplantısı\nÖrnek: /calendar list 2024-01-15\n"""

commands = {
    '/calendar': lambda *args: handle_calendar_command(*args)
}

def handle_calendar_command(*args):
    """Takvim komutlarını yönlendirir."""
    if not args:
        return help()
    
    subcommand = args[0].lower()
    
    if subcommand == 'add':
        if len(args) < 4:
            return "[HATA] Kullanım: /calendar add <başlık> | <tarih> | <açıklama>"
        title = args[1]
        date_str = args[2]
        description = ' '.join(args[3:]) if len(args) > 3 else ""
        return add_event(title, date_str, description)
    
    elif subcommand == 'list':
        date_filter = args[1] if len(args) > 1 else None
        return list_events(date_filter)
    
    elif subcommand == 'today':
        return today_events()
    
    elif subcommand == 'week':
        return week_events()
    
    elif subcommand == 'month':
        return month_events()
    
    elif subcommand == 'search':
        if len(args) < 2:
            return "[HATA] Kullanım: /calendar search <anahtar_kelime>"
        keyword = ' '.join(args[1:])
        return search_events(keyword)
    
    elif subcommand == 'delete':
        if len(args) < 2:
            return "[HATA] Kullanım: /calendar delete <id>"
        return delete_event(args[1])
    
    elif subcommand == 'reminder':
        if len(args) < 3:
            return "[HATA] Kullanım: /calendar reminder <id> <dakika>"
        return set_reminder(args[1], args[2])
    
    elif subcommand == 'upcoming':
        return upcoming_events()
    
    else:
        return help() 