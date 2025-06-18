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
from typing import Optional
from pathlib import Path
import config

app = typer.Typer(help="CortexCLI - CLI LLM Shell")
console = Console()

def check_ollama_status() -> bool:
    """Ollama servisinin çalışıp çalışmadığını kontrol eder"""
    try:
        response = requests.get(f"{config.OLLAMA_CONFIG['base_url']}{config.OLLAMA_CONFIG['tags_endpoint']}", timeout=5)
        return response.status_code == 200
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
    if not check_ollama_status():
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
    
    if not check_ollama_status():
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

def interactive_start():
    console.print(Panel("[bold green]CortexCLI'ye Hoş Geldiniz![/bold green]", title="CortexCLI Başlangıç", border_style="green"))

    # Geçmiş kaydı sorusu
    save_history = Confirm.ask("Sohbet geçmişi kaydedilsin mi?", default=True)

    # Model seçimi
    available_models = [(alias, model) for alias, model in config.MODELS.items() if model in get_available_models()]
    if not available_models:
        console.print("[red]Hiçbir model yüklü değil! Lütfen önce bir model yükleyin.[/red]")
        raise typer.Exit(1)
    
    console.print("\n[bold cyan]Kullanmak istediğiniz modeli seçin:[/bold cyan]")
    for idx, (alias, model) in enumerate(available_models, 1):
        console.print(f"[green]{idx}[/green]. {alias} ([dim]{model}[/dim])")
    
    while True:
        try:
            model_choice = int(Prompt.ask("Model numarasını girin", default="1"))
            if 1 <= model_choice <= len(available_models):
                selected_model = available_models[model_choice-1][0]
                break
            else:
                console.print("[red]Geçersiz seçim![/red]")
        except Exception:
            console.print("[red]Lütfen geçerli bir sayı girin.[/red]")

    # Sistem prompt şablonu seçimi
    console.print("\n[bold cyan]Bir sistem prompt şablonu seçmek ister misiniz?[/bold cyan]")
    preset_keys = list(config.SYSTEM_PROMPTS.keys())
    for idx, key in enumerate(preset_keys, 1):
        console.print(f"[green]{idx}[/green]. {key} ([dim]{config.SYSTEM_PROMPTS[key][:40]}...[/dim])")
    console.print(f"[green]0[/green]. [dim]Şablon kullanma[/dim]")
    
    while True:
        try:
            preset_choice = int(Prompt.ask("Şablon numarasını girin", default="0"))
            if preset_choice == 0:
                system_preset = None
                break
            elif 1 <= preset_choice <= len(preset_keys):
                system_preset = preset_keys[preset_choice-1]
                break
            else:
                console.print("[red]Geçersiz seçim![/red]")
        except Exception:
            console.print("[red]Lütfen geçerli bir sayı girin.[/red]")

    # Çok satırlı giriş
    multi_line = Confirm.ask("Çok satırlı giriş açılsın mı?", default=False)

    # Otomatik kod kaydetme
    auto_save = Confirm.ask("Kod blokları otomatik kaydedilsin mi?", default=False)

    # Shell'i başlat - tüm parametreleri string olarak geç
    shell(
        model=selected_model,
        save_history=save_history,
        history_file="chat_history.txt",
        system_prompt=None,
        system_preset=system_preset,
        multi_line=multi_line,
        temperature=0.7,
        file_input=None,
        auto_save=auto_save,
        output_dir="output"
    )

@app.command()
def start():
    """Etkileşimli başlangıç sihirbazı"""
    interactive_start()

if __name__ == "__main__":
    import sys
    if len(sys.argv) == 1:
        interactive_start()
    else:
        app() 