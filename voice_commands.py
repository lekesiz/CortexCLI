"""
Ses Komutları Sistemi
CortexCLI için ses tanıma ve komut sistemi
"""

import speech_recognition as sr
import pyttsx3
import threading
import time
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from datetime import datetime

@dataclass
class VoiceCommand:
    """Ses komutu tanımı"""
    name: str
    description: str
    keywords: List[str]
    action: Callable
    requires_confirmation: bool = False
    category: str = "genel"

class VoiceCommandSystem:
    """Ses komutları yönetim sistemi"""
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.engine = pyttsx3.init()
        self.commands: Dict[str, VoiceCommand] = {}
        self.is_listening = False
        self.is_speaking = False
        self.wake_word = "cortex"
        self.language = "tr-TR"
        self.confidence_threshold = 0.7
        
        # Ses ayarları
        self.engine.setProperty('rate', 150)
        self.engine.setProperty('volume', 0.8)
        
        # Varsayılan komutları yükle
        self._load_default_commands()
        
    def _load_default_commands(self):
        """Varsayılan ses komutlarını yükle"""
        
        # Model komutları
        self.add_command(VoiceCommand(
            name="model_değiştir",
            description="Model değiştirme",
            keywords=["model değiştir", "modeli değiştir", "farklı model", "yeni model"],
            action=self._change_model,
            category="model"
        ))
        
        self.add_command(VoiceCommand(
            name="modelleri_listele",
            description="Kullanılabilir modelleri listele",
            keywords=["modelleri listele", "hangi modeller var", "model listesi"],
            action=self._list_models,
            category="model"
        ))
        
        # Sohbet komutları
        self.add_command(VoiceCommand(
            name="sohbet_başlat",
            description="Yeni sohbet başlat",
            keywords=["yeni sohbet", "sohbet başlat", "temizle"],
            action=self._start_new_chat,
            category="sohbet"
        ))
        
        self.add_command(VoiceCommand(
            name="geçmişi_göster",
            description="Sohbet geçmişini göster",
            keywords=["geçmişi göster", "önceki mesajlar", "sohbet geçmişi"],
            action=self._show_history,
            category="sohbet"
        ))
        
        # Dosya komutları
        self.add_command(VoiceCommand(
            name="dosyaları_listele",
            description="Dosyaları listele",
            keywords=["dosyaları listele", "dosya listesi", "klasör içeriği"],
            action=self._list_files,
            category="dosya"
        ))
        
        self.add_command(VoiceCommand(
            name="dosya_oku",
            description="Dosya oku",
            keywords=["dosya oku", "dosyayı aç", "içeriği göster"],
            action=self._read_file,
            category="dosya"
        ))
        
        # Kod komutları
        self.add_command(VoiceCommand(
            name="kod_çalıştır",
            description="Kod çalıştır",
            keywords=["kod çalıştır", "programı çalıştır", "execute"],
            action=self._execute_code,
            category="kod"
        ))
        
        self.add_command(VoiceCommand(
            name="kod_analiz",
            description="Kod analizi yap",
            keywords=["kod analiz", "kodu incele", "güvenlik kontrol"],
            action=self._analyze_code,
            category="kod"
        ))
        
        # Plugin komutları
        self.add_command(VoiceCommand(
            name="plugin_listesi",
            description="Plugin'leri listele",
            keywords=["plugin listesi", "eklentiler", "yüklü plugin"],
            action=self._list_plugins,
            category="plugin"
        ))
        
        self.add_command(VoiceCommand(
            name="web_arama",
            description="Web'de arama yap",
            keywords=["web ara", "internet ara", "google ara"],
            action=self._web_search,
            category="plugin"
        ))
        
        # Sistem komutları
        self.add_command(VoiceCommand(
            name="yardım",
            description="Yardım menüsü",
            keywords=["yardım", "komutlar", "ne yapabilirsin"],
            action=self._show_help,
            category="sistem"
        ))
        
        self.add_command(VoiceCommand(
            name="çıkış",
            description="Uygulamadan çık",
            keywords=["çıkış", "kapat", "bitir", "güle güle"],
            action=self._exit_app,
            requires_confirmation=True,
            category="sistem"
        ))
        
    def add_command(self, command: VoiceCommand):
        """Yeni ses komutu ekle"""
        self.commands[command.name] = command
        
    def remove_command(self, command_name: str):
        """Ses komutu kaldır"""
        if command_name in self.commands:
            del self.commands[command_name]
            
    def set_wake_word(self, wake_word: str):
        """Uyandırma kelimesini ayarla"""
        self.wake_word = wake_word.lower()
        
    def set_language(self, language: str):
        """Dil ayarını değiştir"""
        self.language = language
        
    def speak(self, text: str):
        """Metni sesli olarak söyle"""
        if self.is_speaking:
            return
            
        self.is_speaking = True
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        finally:
            self.is_speaking = False
            
    def listen(self) -> Optional[str]:
        """Ses dinle ve metne çevir"""
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                
            text = self.recognizer.recognize_google(audio, language=self.language)
            return text.lower()
            
        except sr.WaitTimeoutError:
            return None
        except sr.UnknownValueError:
            return None
        except sr.RequestError as e:
            print(f"Ses tanıma hatası: {e}")
            return None
            
    def process_command(self, text: str) -> bool:
        """Ses komutunu işle"""
        if not text:
            return False
            
        # Uyandırma kelimesi kontrolü
        if self.wake_word not in text:
            return False
            
        # Komut eşleştirme
        best_match = None
        best_score = 0
        
        for command in self.commands.values():
            for keyword in command.keywords:
                if keyword in text:
                    score = len(keyword) / len(text)
                    if score > best_score and score >= self.confidence_threshold:
                        best_score = score
                        best_match = command
                        
        if best_match:
            try:
                # Onay gerekiyorsa sor
                if best_match.requires_confirmation:
                    self.speak(f"{best_match.description} komutunu çalıştırmak istediğinizden emin misiniz?")
                    confirmation = self.listen()
                    if not confirmation or "evet" not in confirmation:
                        self.speak("Komut iptal edildi")
                        return True
                        
                # Komutu çalıştır
                result = best_match.action(text)
                if result:
                    self.speak(result)
                else:
                    self.speak("Komut başarıyla çalıştırıldı")
                    
            except Exception as e:
                self.speak(f"Komut çalıştırılırken hata oluştu: {str(e)}")
                
            return True
            
        return False
        
    def start_listening(self):
        """Sürekli dinleme başlat"""
        self.is_listening = True
        self.speak(f"{self.wake_word} dinlemeye başladı")
        
        while self.is_listening:
            try:
                text = self.listen()
                if text:
                    print(f"🎤 Duyulan: {text}")
                    if self.process_command(text):
                        print("✅ Komut işlendi")
                    else:
                        print("❌ Komut tanınmadı")
                        
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Ses dinleme hatası: {e}")
                
        self.speak("Ses dinleme durduruldu")
        
    def stop_listening(self):
        """Dinlemeyi durdur"""
        self.is_listening = False
        
    def get_commands_by_category(self) -> Dict[str, List[VoiceCommand]]:
        """Komutları kategorilere göre grupla"""
        categories = {}
        for command in self.commands.values():
            if command.category not in categories:
                categories[command.category] = []
            categories[command.category].append(command)
        return categories
        
    # Komut işleyicileri
    def _change_model(self, text: str) -> str:
        """Model değiştirme"""
        try:
            from llm_shell import get_available_models, set_current_model
            models = get_available_models()
            
            # Metinden model adını çıkar
            for model in models:
                if model.lower() in text:
                    set_current_model(model)
                    return f"Model {model} olarak değiştirildi"
                    
            return f"Kullanılabilir modeller: {', '.join(models[:5])}"
            
        except Exception as e:
            return f"Model değiştirme hatası: {str(e)}"
            
    def _list_models(self, text: str) -> str:
        """Modelleri listele"""
        try:
            from llm_shell import get_available_models
            models = get_available_models()
            return f"Kullanılabilir modeller: {', '.join(models[:10])}"
        except Exception as e:
            return f"Model listesi alınamadı: {str(e)}"
            
    def _start_new_chat(self, text: str) -> str:
        """Yeni sohbet başlat"""
        try:
            from llm_shell import clear_chat_history
            clear_chat_history()
            return "Yeni sohbet başlatıldı"
        except Exception as e:
            return f"Sohbet temizleme hatası: {str(e)}"
            
    def _show_history(self, text: str) -> str:
        """Geçmişi göster"""
        try:
            from llm_shell import get_chat_history
            history = get_chat_history()
            if history:
                return f"Son {len(history)} mesaj var"
            else:
                return "Sohbet geçmişi boş"
        except Exception as e:
            return f"Geçmiş görüntüleme hatası: {str(e)}"
            
    def _list_files(self, text: str) -> str:
        """Dosyaları listele"""
        try:
            files = list(Path('.').iterdir())
            file_names = [f.name for f in files[:10]]
            return f"Dosyalar: {', '.join(file_names)}"
        except Exception as e:
            return f"Dosya listesi alınamadı: {str(e)}"
            
    def _read_file(self, text: str) -> str:
        """Dosya oku"""
        try:
            # Metinden dosya adını çıkar
            words = text.split()
            for word in words:
                if '.' in word and Path(word).exists():
                    with open(word, 'r', encoding='utf-8') as f:
                        content = f.read(200)  # İlk 200 karakter
                    return f"{word} dosyasının başlangıcı: {content}"
            return "Dosya adı belirtilmedi"
        except Exception as e:
            return f"Dosya okuma hatası: {str(e)}"
            
    def _execute_code(self, text: str) -> str:
        """Kod çalıştır"""
        try:
            # Basit kod örnekleri
            if "merhaba" in text:
                return "print('Merhaba Dünya!') kodu çalıştırıldı"
            elif "tarih" in text:
                return f"Bugünün tarihi: {datetime.now().strftime('%d/%m/%Y')}"
            else:
                return "Hangi kodu çalıştırmak istiyorsunuz?"
        except Exception as e:
            return f"Kod çalıştırma hatası: {str(e)}"
            
    def _analyze_code(self, text: str) -> str:
        """Kod analizi"""
        return "Kod analizi özelliği henüz tamamlanmadı"
        
    def _list_plugins(self, text: str) -> str:
        """Plugin'leri listele"""
        try:
            from plugin_system import PluginManager
            plugin_manager = PluginManager()
            plugins = plugin_manager.list_plugins()
            plugin_names = [p['name'] for p in plugins[:5]]
            return f"Yüklü plugin'ler: {', '.join(plugin_names)}"
        except Exception as e:
            return f"Plugin listesi alınamadı: {str(e)}"
            
    def _web_search(self, text: str) -> str:
        """Web arama"""
        try:
            # Metinden arama terimini çıkar
            search_terms = text.split()
            if len(search_terms) > 2:
                query = ' '.join(search_terms[2:])  # "web ara" sonrası
                from plugins.web_search import WebSearchPlugin
                plugin = WebSearchPlugin()
                result = plugin.search(query)
                return f"Arama sonucu: {result[:100]}..."
            else:
                return "Ne aramak istiyorsunuz?"
        except Exception as e:
            return f"Web arama hatası: {str(e)}"
            
    def _show_help(self, text: str) -> str:
        """Yardım göster"""
        categories = self.get_commands_by_category()
        help_text = "Ses komutları: "
        for category, commands in categories.items():
            help_text += f"{category}: {len(commands)} komut, "
        return help_text
        
    def _exit_app(self, text: str) -> str:
        """Uygulamadan çık"""
        self.stop_listening()
        return "CortexCLI kapatılıyor"

# Global ses komut sistemi
voice_system = VoiceCommandSystem()

def start_voice_commands():
    """Ses komutlarını başlat"""
    voice_system.start_listening()
    
def stop_voice_commands():
    """Ses komutlarını durdur"""
    voice_system.stop_listening()
    
def add_voice_command(name: str, description: str, keywords: List[str], action: Callable, 
                     requires_confirmation: bool = False, category: str = "özel"):
    """Yeni ses komutu ekle"""
    command = VoiceCommand(
        name=name,
        description=description,
        keywords=keywords,
        action=action,
        requires_confirmation=requires_confirmation,
        category=category
    )
    voice_system.add_command(command)
    
def remove_voice_command(name: str):
    """Ses komutu kaldır"""
    voice_system.remove_command(name)
    
def get_voice_commands() -> Dict[str, List[VoiceCommand]]:
    """Ses komutlarını al"""
    return voice_system.get_commands_by_category()
    
def speak(text: str):
    """Metni sesli olarak söyle"""
    voice_system.speak(text)
    
def listen_for_command() -> Optional[str]:
    """Tek seferlik komut dinle"""
    return voice_system.listen() 