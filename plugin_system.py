"""
CortexCLI Plugin Sistemi
Kullanıcıların kendi eklentilerini yazabilmesi için plugin altyapısı
"""

import os
import sys
import importlib
import importlib.util
from pathlib import Path
from typing import Dict, List, Any, Callable
from abc import ABC, abstractmethod
import json
import logging

# Otomatik yüklenecek pluginler
DEFAULT_PLUGINS = [
    'web_search',
    'web_weather', 
    'web_wikipedia',
    'data_analyzer',
    'calculator',
    'notes',
    'file_manager',
    'calendar'
]

class PluginBase(ABC):
    """Tüm plugin'ler için temel sınıf"""
    
    def __init__(self, name: str, version: str, description: str):
        self.name = name
        self.version = version
        self.description = description
        self.enabled = True
        
    @abstractmethod
    def on_load(self) -> bool:
        """Plugin yüklendiğinde çağrılır"""
        pass
        
    @abstractmethod
    def on_unload(self) -> bool:
        """Plugin kaldırıldığında çağrılır"""
        pass
        
    def get_commands(self) -> Dict[str, Callable]:
        """Plugin'in sağladığı komutları döndürür"""
        return {}
        
    def get_help(self) -> str:
        """Plugin'in yardım metnini döndürür"""
        return f"{self.name} v{self.version}: {self.description}"

class PluginManager:
    """Plugin yöneticisi"""
    
    def __init__(self, plugins_dir: str = "plugins"):
        self.plugins_dir = Path(plugins_dir)
        self.plugins = {}
        self.commands = {}
        self._discover_plugins()
        
    def _discover_plugins(self):
        for file in self.plugins_dir.glob("*.py"):
            if file.name.startswith("_") or file.name == "__init__.py":
                continue
            name = file.stem
            try:
                module = importlib.import_module(f"plugins.{name}")
                self.plugins[name] = module
                # Komutları kaydet
                if hasattr(module, 'commands'):
                    for cmd, func in module.commands.items():
                        self.commands[cmd] = func
            except Exception as e:
                print(f"[PluginManager] Plugin yüklenemedi: {name} - {e}")
        
    def get_plugin_commands(self):
        return self.commands
        
    def list_plugins(self):
        result = {}
        for name, mod in self.plugins.items():
            result[name] = {
                "loaded": True,
                "version": getattr(mod, "__version__", "1.0"),
                "description": getattr(mod, "__doc__", ""),
                "help": mod.help() if hasattr(mod, 'help') else ""
            }
        return result

    def discover_plugins(self) -> List[str]:
        """Plugin dizinindeki tüm plugin'leri keşfeder."""
        discovered = []
        try:
            plugin_dir = Path(__file__).parent / "plugins"
            if plugin_dir.exists():
                for plugin_file in plugin_dir.glob("*.py"):
                    if plugin_file.name != "__init__.py":
                        discovered.append(plugin_file.stem)
            return discovered
        except Exception as e:
            logging.error(f"Plugin keşif hatası: {e}")
            return []

    def load_plugin(self, plugin_name: str) -> bool:
        """Belirtilen plugin'i yükler."""
        try:
            if plugin_name in self.plugins:
                return True  # Zaten yüklü
                
            module = importlib.import_module(f"plugins.{plugin_name}")
            self.plugins[plugin_name] = module
            
            # Komutları kaydet
            if hasattr(module, 'commands'):
                for cmd, func in module.commands.items():
                    self.commands[cmd] = func
                    
            logging.info(f"Plugin yüklendi: {plugin_name}")
            return True
        except Exception as e:
            logging.error(f"Plugin yükleme hatası {plugin_name}: {e}")
            return False

    def load_plugins(self):
        """Pluginleri yükler."""
        try:
            # Varsayılan pluginleri otomatik yükle
            for plugin_name in DEFAULT_PLUGINS:
                if plugin_name not in self.plugins:
                    self.load_plugin(plugin_name)
            
            # Plugin dizinindeki tüm .py dosyalarını tara
            plugin_dir = Path(__file__).parent / "plugins"
            if plugin_dir.exists():
                for plugin_file in plugin_dir.glob("*.py"):
                    if plugin_file.name != "__init__.py":
                        plugin_name = plugin_file.stem
                        if plugin_name not in self.plugins:
                            self.load_plugin(plugin_name)
            
            logging.info(f"{len(self.plugins)} plugin yüklendi")
        except Exception as e:
            logging.error(f"Plugin yükleme hatası: {e}")

# Örnek Plugin'ler
class WebSearchPlugin(PluginBase):
    """Web arama plugin'i"""
    
    def __init__(self):
        super().__init__(
            name="web_search",
            version="1.0.0",
            description="Web'de arama yapma özelliği"
        )
        
    def on_load(self) -> bool:
        print(f"🌐 {self.name} plugin'i yüklendi")
        return True
        
    def on_unload(self) -> bool:
        print(f"🌐 {self.name} plugin'i kaldırıldı")
        return True
        
    def get_commands(self) -> Dict[str, Callable]:
        return {
            "search": self.web_search,
            "weather": self.get_weather
        }
        
    def web_search(self, query: str) -> str:
        """Web'de arama yapar"""
        # Burada gerçek web arama API'si kullanılabilir
        return f"🔍 '{query}' için web arama sonuçları..."
        
    def get_weather(self, city: str) -> str:
        """Hava durumu bilgisi alır"""
        return f"🌤️ {city} için hava durumu bilgisi..."

class FileAnalyzerPlugin(PluginBase):
    """Dosya analiz plugin'i"""
    
    def __init__(self):
        super().__init__(
            name="file_analyzer",
            version="1.0.0",
            description="Dosya analizi ve işleme özellikleri"
        )
        
    def on_load(self) -> bool:
        print(f"📁 {self.name} plugin'i yüklendi")
        return True
        
    def on_unload(self) -> bool:
        print(f"📁 {self.name} plugin'i kaldırıldı")
        return True
        
    def get_commands(self) -> Dict[str, Callable]:
        return {
            "analyze": self.analyze_file,
            "stats": self.file_stats
        }
        
    def analyze_file(self, file_path: str) -> str:
        """Dosya analizi yapar"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            lines = len(content.split('\n'))
            chars = len(content)
            words = len(content.split())
            
            return f"📊 {file_path} analizi:\n" \
                   f"  Satır: {lines}\n" \
                   f"  Karakter: {chars}\n" \
                   f"  Kelime: {words}"
        except Exception as e:
            return f"❌ Dosya analiz hatası: {e}"
            
    def file_stats(self, file_path: str) -> str:
        """Dosya istatistikleri"""
        try:
            stat = os.stat(file_path)
            return f"📈 {file_path} istatistikleri:\n" \
                   f"  Boyut: {stat.st_size:,} B\n" \
                   f"  Oluşturulma: {stat.st_ctime}\n" \
                   f"  Değiştirilme: {stat.st_mtime}"
        except Exception as e:
            return f"❌ İstatistik hatası: {e}" 