#!/usr/bin/env python3
"""
DQai - CLI LLM Shell
Claude Code tarzında, terminal üzerinden kullanılabilen hafif LLM sohbet uygulaması
"""

import subprocess
import typer
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.text import Text
from rich.syntax import Syntax
from rich.table import Table
import requests
import json
import os
from datetime import datetime
from typing import Optional
import config

app = typer.Typer(help="DQai - CLI LLM Shell")
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

@app.command()
def shell(
    model: str = typer.Option(config.get_setting("model"), help="Model seç"),
    save_history: bool = typer.Option(config.get_setting("save_history"), help="Geçmişi kaydet"),
    history_file: str = typer.Option(config.get_setting("history_file"), help="Geçmiş dosyası adı"),
    system_prompt: Optional[str] = typer.Option(config.get_setting("system_prompt"), help="Sistem prompt'u"),
    system_preset: Optional[str] = typer.Option(None, help="Sistem prompt şablonu (python_expert, security_expert, translator, code_reviewer, teacher, debugger)"),
    multi_line: bool = typer.Option(config.get_setting("multi_line"), help="Çok satırlı giriş desteği"),
    temperature: float = typer.Option(config.get_setting("temperature"), help="Yaratıcılık seviyesi (0.0-1.0)"),
    file_input: Optional[str] = typer.Option(None, help="Dosya içeriğini prompt'a ekle")
):
    """DQai CLI LLM Shell'i başlatır"""
    
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
    
    # Başlangıç mesajı
    console.print(Panel(
        f"[bold green]🚀 DQai CLI LLM Shell[/bold green]\n"
        f"[cyan]Model:[/cyan] {selected_model}\n"
        f"[cyan]Geçmiş:[/cyan] {'Kaydediliyor' if save_history else 'Kaydedilmiyor'}\n"
        f"[cyan]Çok satır:[/cyan] {'Açık' if multi_line else 'Kapalı'}\n"
        f"[cyan]Temperature:[/cyan] {temperature}\n\n"
        f"[dim]Çıkmak için: exit, quit, q veya Ctrl+C[/dim]",
        title="DQai Shell",
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
            
            # Geçmişi kaydet
            if save_history:
                save_to_history(prompt, response, selected_model, history_file)
                
        except KeyboardInterrupt:
            console.print("\n[bold yellow]⚠️  İşlem iptal edildi.[/bold yellow]")
            break
        except EOFError:
            console.print("\n[bold yellow]👋 Çıkılıyor...[/bold yellow]")
            break

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

if __name__ == "__main__":
    app() 