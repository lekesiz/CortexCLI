"""
Kullanıcı Ayarları ve Profil Sistemi
Kullanıcı tercihlerini, varsayılan ayarları ve kullanım istatistiklerini yönetir
"""

import json
import os
from datetime import datetime, date
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
import config

@dataclass
class UserProfile:
    """Kullanıcı profil bilgileri"""
    username: str = "cortex_user"
    email: str = ""
    created_date: str = ""
    last_login: str = ""
    total_sessions: int = 0
    total_queries: int = 0
    favorite_model: str = "qwen2.5:7b"
    preferred_theme: str = "default"

@dataclass
class UserPreferences:
    """Kullanıcı tercihleri"""
    default_model: str = "qwen2.5:7b"
    default_temperature: float = 0.7
    default_system_prompt: str = "Sen yardımcı bir AI asistanısın."
    auto_save_code: bool = True
    auto_save_history: bool = True
    multi_line_input: bool = True
    output_directory: str = "output"
    max_history_size: int = 100
    enable_notifications: bool = True
    language: str = "tr"

@dataclass
class UsageStats:
    """Kullanım istatistikleri"""
    total_queries: int = 0
    total_code_executions: int = 0
    total_files_processed: int = 0
    total_plugins_used: int = 0
    models_used: Dict[str, int] = None
    commands_used: Dict[str, int] = None
    daily_usage: Dict[str, int] = None
    
    def __post_init__(self):
        if self.models_used is None:
            self.models_used = {}
        if self.commands_used is None:
            self.commands_used = {}
        if self.daily_usage is None:
            self.daily_usage = {}

class UserSettings:
    """Kullanıcı ayarları yöneticisi"""
    
    def __init__(self, settings_file: str = "user_settings.json"):
        self.settings_file = Path(settings_file)
        self.profile = UserProfile()
        self.preferences = UserPreferences()
        self.stats = UsageStats()
        
        # Varsayılan değerleri config'den al
        self._load_defaults_from_config()
        
        # Mevcut ayarları yükle
        self.load_settings()
        
        # Profil oluşturma tarihini ayarla
        if not self.profile.created_date:
            self.profile.created_date = datetime.now().isoformat()
            self.save_settings()
    
    def _load_defaults_from_config(self):
        """Config dosyasından varsayılan değerleri yükle"""
        try:
            self.preferences.default_model = config.get_setting("model")
            self.preferences.default_temperature = config.get_setting("temperature")
            self.preferences.default_system_prompt = config.get_setting("system_prompt")
            self.preferences.auto_save_history = config.get_setting("save_history")
            self.preferences.multi_line_input = config.get_setting("multi_line")
        except:
            pass  # Config yoksa varsayılan değerler kullanılır
    
    def load_settings(self):
        """Ayarları dosyadan yükle"""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # Profil bilgilerini yükle
                    if 'profile' in data:
                        profile_data = data['profile']
                        for field in asdict(self.profile).keys():
                            if field in profile_data:
                                setattr(self.profile, field, profile_data[field])
                    
                    # Tercihleri yükle
                    if 'preferences' in data:
                        pref_data = data['preferences']
                        for field in asdict(self.preferences).keys():
                            if field in pref_data:
                                setattr(self.preferences, field, pref_data[field])
                    
                    # İstatistikleri yükle
                    if 'stats' in data:
                        stats_data = data['stats']
                        for field in asdict(self.stats).keys():
                            if field in stats_data:
                                setattr(self.stats, field, stats_data[field])
        except Exception as e:
            print(f"Ayarlar yüklenirken hata: {e}")
    
    def save_settings(self):
        """Ayarları dosyaya kaydet"""
        try:
            data = {
                'profile': asdict(self.profile),
                'preferences': asdict(self.preferences),
                'stats': asdict(self.stats),
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Ayarlar kaydedilirken hata: {e}")
    
    def update_profile(self, **kwargs):
        """Profil bilgilerini güncelle"""
        for key, value in kwargs.items():
            if hasattr(self.profile, key):
                setattr(self.profile, key, value)
        self.save_settings()
    
    def update_preferences(self, **kwargs):
        """Kullanıcı tercihlerini güncelle"""
        for key, value in kwargs.items():
            if hasattr(self.preferences, key):
                setattr(self.preferences, key, value)
        self.save_settings()
    
    def record_query(self, model: str = None):
        """Sorgu istatistiğini kaydet"""
        self.stats.total_queries += 1
        if model:
            self.stats.models_used[model] = self.stats.models_used.get(model, 0) + 1
        
        # Günlük kullanımı kaydet
        today = date.today().isoformat()
        self.stats.daily_usage[today] = self.stats.daily_usage.get(today, 0) + 1
        
        self.save_settings()
    
    def record_command(self, command: str):
        """Komut kullanımını kaydet"""
        self.stats.commands_used[command] = self.stats.commands_used.get(command, 0) + 1
        self.save_settings()
    
    def record_code_execution(self):
        """Kod çalıştırma istatistiğini kaydet"""
        self.stats.total_code_executions += 1
        self.save_settings()
    
    def record_file_processed(self):
        """Dosya işleme istatistiğini kaydet"""
        self.stats.total_files_processed += 1
        self.save_settings()
    
    def record_plugin_used(self):
        """Plugin kullanım istatistiğini kaydet"""
        self.stats.total_plugins_used += 1
        self.save_settings()
    
    def get_stats_summary(self) -> Dict[str, Any]:
        """İstatistik özetini döndür"""
        return {
            'total_queries': self.stats.total_queries,
            'total_code_executions': self.stats.total_code_executions,
            'total_files_processed': self.stats.total_files_processed,
            'total_plugins_used': self.stats.total_plugins_used,
            'most_used_model': max(self.stats.models_used.items(), key=lambda x: x[1])[0] if self.stats.models_used else "Yok",
            'most_used_command': max(self.stats.commands_used.items(), key=lambda x: x[1])[0] if self.stats.commands_used else "Yok",
            'sessions_this_week': sum(1 for d, count in self.stats.daily_usage.items() 
                                    if (date.today() - date.fromisoformat(d)).days <= 7)
        }
    
    def reset_stats(self):
        """İstatistikleri sıfırla"""
        self.stats = UsageStats()
        self.save_settings()
    
    def export_settings(self, filepath: str) -> bool:
        """Ayarları dışa aktar"""
        try:
            data = {
                'profile': asdict(self.profile),
                'preferences': asdict(self.preferences),
                'stats': asdict(self.stats),
                'export_date': datetime.now().isoformat()
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Ayarlar dışa aktarılırken hata: {e}")
            return False
    
    def import_settings(self, filepath: str) -> bool:
        """Ayarları içe aktar"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Mevcut ayarları yedekle
            backup_file = f"user_settings_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            self.export_settings(backup_file)
            
            # Yeni ayarları yükle
            if 'profile' in data:
                for key, value in data['profile'].items():
                    if hasattr(self.profile, key):
                        setattr(self.profile, key, value)
            
            if 'preferences' in data:
                for key, value in data['preferences'].items():
                    if hasattr(self.preferences, key):
                        setattr(self.preferences, key, value)
            
            if 'stats' in data:
                for key, value in data['stats'].items():
                    if hasattr(self.stats, key):
                        setattr(self.stats, key, value)
            
            self.save_settings()
            return True
        except Exception as e:
            print(f"Ayarlar içe aktarılırken hata: {e}")
            return False

# Global kullanıcı ayarları instance'ı
user_settings = UserSettings()

def get_user_preferences() -> UserPreferences:
    """Kullanıcı tercihlerini döndür"""
    return user_settings.preferences

def get_user_profile() -> UserProfile:
    """Kullanıcı profilini döndür"""
    return user_settings.profile

def get_user_stats() -> UsageStats:
    """Kullanıcı istatistiklerini döndür"""
    return user_settings.stats 