"""
Yardım Sistemi Modülü
CortexCLI için kapsamlı yardım sistemi
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import json
import os

@dataclass
class HelpItem:
    """Yardım öğesi"""
    command: str
    description: str
    usage: str
    examples: List[str]
    category: str
    aliases: List[str] = None

class HelpSystem:
    """Yardım sistemi sınıfı"""
    
    def __init__(self):
        self.help_data = self._load_help_data()
        
    def _load_help_data(self) -> Dict[str, Dict[str, Any]]:
        """Yardım verilerini yükle"""
        return {
            "temel": {
                "desc": "Temel komutlar ve genel kullanım",
                "commands": {
                    "/help": {
                        "desc": "Yardım menüsünü gösterir",
                        "usage": "/help [kategori] [komut]",
                        "examples": ["/help", "/help model", "/help /run"],
                        "aliases": ["/h", "/?"]
                    },
                    "/exit": {
                        "desc": "Uygulamadan çıkış yapar",
                        "usage": "/exit",
                        "examples": ["/exit"],
                        "aliases": ["/quit", "/q"]
                    },
                    "/clear": {
                        "desc": "Ekranı temizler",
                        "usage": "/clear",
                        "examples": ["/clear"],
                        "aliases": ["/cls"]
                    },
                    "/config": {
                        "desc": "Yapılandırmayı gösterir",
                        "usage": "/config",
                        "examples": ["/config"],
                        "aliases": ["/settings"]
                    }
                }
            },
            "model": {
                "desc": "Model yönetimi ve LLM komutları",
                "commands": {
                    "/model": {
                        "desc": "Modeli değiştirir",
                        "usage": "/model <model_adı>",
                        "examples": ["/model qwen2.5:72b", "/model deepseek-coder"],
                        "aliases": ["/m"]
                    },
                    "/models": {
                        "desc": "Kullanılabilir modelleri listeler",
                        "usage": "/models",
                        "examples": ["/models"],
                        "aliases": ["/list-models"]
                    },
                    "/system": {
                        "desc": "Sistem promptunu değiştirir",
                        "usage": "/system <prompt>",
                        "examples": ["/system Sen bir Python uzmanısın"],
                        "aliases": ["/prompt"]
                    },
                    "/install": {
                        "desc": "Modeli indirir ve yükler",
                        "usage": "/install <model>",
                        "examples": ["/install deepseek-coder"],
                        "aliases": ["/download"]
                    },
                    "/troubleshoot": {
                        "desc": "Sorun giderme menüsünü açar",
                        "usage": "/troubleshoot",
                        "examples": ["/troubleshoot"],
                        "aliases": ["/debug"]
                    }
                }
            },
            "multi-model": {
                "desc": "Çoklu model yönetimi ve karşılaştırma",
                "commands": {
                    "/add-model": {
                        "desc": "Yeni bir model ekler",
                        "usage": "/add-model <alias> <model>",
                        "examples": ["/add-model claude claude-3"],
                        "aliases": ["/add"]
                    },
                    "/remove-model": {
                        "desc": "Modeli kaldırır",
                        "usage": "/remove-model <alias>",
                        "examples": ["/remove-model claude"],
                        "aliases": ["/remove"]
                    },
                    "/list-models": {
                        "desc": "Aktif modelleri listeler",
                        "usage": "/list-models",
                        "examples": ["/list-models"],
                        "aliases": ["/models"]
                    },
                    "/compare": {
                        "desc": "Modelleri karşılaştırır",
                        "usage": "/compare <sorgu>",
                        "examples": ["/compare Python'da dosya oku"],
                        "aliases": ["/vs"]
                    },
                    "/query-model": {
                        "desc": "Belirli bir modelle sorgu yapar",
                        "usage": "/query-model <alias> <sorgu>",
                        "examples": ["/query-model claude Merhaba"],
                        "aliases": ["/q"]
                    },
                    "/metrics": {
                        "desc": "Performans metriklerini gösterir",
                        "usage": "/metrics",
                        "examples": ["/metrics"],
                        "aliases": ["/stats"]
                    },
                    "/save-comparison": {
                        "desc": "Karşılaştırmayı kaydeder",
                        "usage": "/save-comparison [dosya]",
                        "examples": ["/save-comparison", "/save-comparison results.txt"],
                        "aliases": ["/save"]
                    },
                    "/clear-models": {
                        "desc": "Model geçmişini temizler",
                        "usage": "/clear-models",
                        "examples": ["/clear-models"],
                        "aliases": ["/clear"]
                    }
                }
            },
            "sohbet": {
                "desc": "Sohbet ve geçmiş yönetimi",
                "commands": {
                    "/history": {
                        "desc": "Sohbet geçmişini gösterir",
                        "usage": "/history [limit]",
                        "examples": ["/history", "/history 10"],
                        "aliases": ["/h"]
                    },
                    "/save": {
                        "desc": "Sohbet geçmişini kaydeder",
                        "usage": "/save <dosya>",
                        "examples": ["/save chat.txt"],
                        "aliases": ["/export"]
                    },
                    "/load": {
                        "desc": "Sohbet geçmişini yükler",
                        "usage": "/load <dosya>",
                        "examples": ["/load chat.txt"],
                        "aliases": ["/import"]
                    },
                    "/reset": {
                        "desc": "Sohbet geçmişini sıfırlar",
                        "usage": "/reset",
                        "examples": ["/reset"],
                        "aliases": ["/clear"]
                    }
                }
            },
            "dosya": {
                "desc": "Dosya sistemi ve yönetimi",
                "commands": {
                    "/read": {
                        "desc": "Dosya okur",
                        "usage": "/read <dosya>",
                        "examples": ["/read README.md"],
                        "aliases": ["/cat"]
                    },
                    "/write": {
                        "desc": "Dosya yazar",
                        "usage": "/write <dosya> <içerik>",
                        "examples": ["/write test.txt Merhaba"],
                        "aliases": ["/echo"]
                    },
                    "/list": {
                        "desc": "Dosyaları listeler",
                        "usage": "/list [dizin]",
                        "examples": ["/list", "/list /home"],
                        "aliases": ["/ls"]
                    },
                    "/delete": {
                        "desc": "Dosya/klasör siler",
                        "usage": "/delete <dosya>",
                        "examples": ["/delete test.txt"],
                        "aliases": ["/rm"]
                    },
                    "/rename": {
                        "desc": "Yeniden adlandırır",
                        "usage": "/rename <eski> <yeni>",
                        "examples": ["/rename old.txt new.txt"],
                        "aliases": ["/mv"]
                    },
                    "/mkdir": {
                        "desc": "Klasör oluşturur",
                        "usage": "/mkdir <klasör>",
                        "examples": ["/mkdir test"],
                        "aliases": ["/md"]
                    },
                    "/cd": {
                        "desc": "Dizin değiştirir",
                        "usage": "/cd <dizin>",
                        "examples": ["/cd /home", "/cd .."],
                        "aliases": ["/chdir"]
                    },
                    "/pwd": {
                        "desc": "Mevcut dizini gösterir",
                        "usage": "/pwd",
                        "examples": ["/pwd"],
                        "aliases": ["/cwd"]
                    }
                }
            },
            "kod": {
                "desc": "Kod çalıştırma ve analiz",
                "commands": {
                    "/run": {
                        "desc": "Kodu çalıştırır",
                        "usage": "/run <kod>",
                        "examples": ["/run print('Merhaba')"],
                        "aliases": ["/execute"]
                    },
                    "/run-file": {
                        "desc": "Dosyadan kod çalıştırır",
                        "usage": "/run --file <dosya>",
                        "examples": ["/run --file script.py"],
                        "aliases": ["/run-f"]
                    },
                    "/run-safe": {
                        "desc": "Güvenli ortamda kod çalıştırır",
                        "usage": "/run-safe <kod>",
                        "examples": ["/run-safe print('test')"],
                        "aliases": ["/safe"]
                    },
                    "/analyze": {
                        "desc": "Kod analizi yapar",
                        "usage": "/analyze <kod>",
                        "examples": ["/analyze print('test')"],
                        "aliases": ["/check"]
                    },
                    "/notebook": {
                        "desc": "Jupyter notebook oluşturur",
                        "usage": "/notebook <ad> <kod>",
                        "examples": ["/notebook test print('hello')"],
                        "aliases": ["/nb"]
                    },
                    "/add-cell": {
                        "desc": "Notebook'a hücre ekler",
                        "usage": "/add-cell <notebook> <kod>",
                        "examples": ["/add-cell test print('world')"],
                        "aliases": ["/cell"]
                    },
                    "/debug": {
                        "desc": "Kod debug bilgisi verir",
                        "usage": "/debug <kod>",
                        "examples": ["/debug x = 1"],
                        "aliases": ["/dbg"]
                    },
                    "/breakpoint": {
                        "desc": "Breakpoint ekler",
                        "usage": "/breakpoint <satır>",
                        "examples": ["/breakpoint 10"],
                        "aliases": ["/bp"]
                    }
                }
            },
            "plugin": {
                "desc": "Plugin yönetimi ve komutları",
                "commands": {
                    "/plugins": {
                        "desc": "Yüklü plugin'leri listeler",
                        "usage": "/plugins",
                        "examples": ["/plugins"],
                        "aliases": ["/list-plugins"]
                    },
                    "/load": {
                        "desc": "Plugin yükler",
                        "usage": "/load <plugin>",
                        "examples": ["/load web_search"],
                        "aliases": ["/enable"]
                    },
                    "/unload": {
                        "desc": "Plugin kaldırır",
                        "usage": "/unload <plugin>",
                        "examples": ["/unload web_search"],
                        "aliases": ["/disable"]
                    },
                    "/search": {
                        "desc": "Web'de arama yapar (web_search plugin)",
                        "usage": "/search <sorgu>",
                        "examples": ["/search Python decorator"],
                        "aliases": ["/web-search"]
                    },
                    "/weather": {
                        "desc": "Hava durumu alır (weather plugin)",
                        "usage": "/weather <şehir>",
                        "examples": ["/weather Istanbul"],
                        "aliases": ["/w"]
                    },
                    "/analyze-file": {
                        "desc": "Dosya analizi yapar (file_analyzer plugin)",
                        "usage": "/analyze-file <dosya>",
                        "examples": ["/analyze-file test.py"],
                        "aliases": ["/af"]
                    },
                    "/stats": {
                        "desc": "Dosya istatistikleri",
                        "usage": "/stats <dosya>",
                        "examples": ["/stats test.py"],
                        "aliases": ["/file-stats"]
                    },
                    "/hash": {
                        "desc": "Dosya hash değeri",
                        "usage": "/hash <dosya>",
                        "examples": ["/hash test.py"],
                        "aliases": ["/md5"]
                    },
                    "/find": {
                        "desc": "Dosya arar",
                        "usage": "/find <pattern>",
                        "examples": ["/find *.py"],
                        "aliases": ["/search-files"]
                    }
                }
            },
            "tema": {
                "desc": "Tema yönetimi",
                "commands": {
                    "/theme": {
                        "desc": "Temaları listeler",
                        "usage": "/theme",
                        "examples": ["/theme"],
                        "aliases": ["/themes"]
                    },
                    "/theme-set": {
                        "desc": "Temayı değiştirir",
                        "usage": "/theme set <ad>",
                        "examples": ["/theme set dark"],
                        "aliases": ["/theme-change"]
                    },
                    "/theme-create": {
                        "desc": "Yeni tema oluşturur",
                        "usage": "/theme create <ad> <açıklama>",
                        "examples": ["/theme create custom Özel tema"],
                        "aliases": ["/theme-new"]
                    },
                    "/theme-delete": {
                        "desc": "Temayı siler",
                        "usage": "/theme delete <ad>",
                        "examples": ["/theme delete custom"],
                        "aliases": ["/theme-remove"]
                    },
                    "/theme-export": {
                        "desc": "Temayı dışa aktarır",
                        "usage": "/theme export <ad> <dosya>",
                        "examples": ["/theme export dark theme.json"],
                        "aliases": ["/theme-save"]
                    },
                    "/theme-import": {
                        "desc": "Temayı içe aktarır",
                        "usage": "/theme import <dosya>",
                        "examples": ["/theme import theme.json"],
                        "aliases": ["/theme-load"]
                    },
                    "/theme-current": {
                        "desc": "Mevcut temayı gösterir",
                        "usage": "/theme current",
                        "examples": ["/theme current"],
                        "aliases": ["/theme-show"]
                    }
                }
            },
            "ses": {
                "desc": "Ses komutları yönetimi",
                "commands": {
                    "/voice": {
                        "desc": "Ses komutları yönetimi",
                        "usage": "/voice",
                        "examples": ["/voice"],
                        "aliases": ["/voice-help"]
                    },
                    "/voice-start": {
                        "desc": "Ses dinlemeyi başlat",
                        "usage": "/voice-start",
                        "examples": ["/voice-start"],
                        "aliases": ["/voice-on"]
                    },
                    "/voice-stop": {
                        "desc": "Ses dinlemeyi durdur",
                        "usage": "/voice-stop",
                        "examples": ["/voice-stop"],
                        "aliases": ["/voice-off"]
                    },
                    "/voice-test": {
                        "desc": "Ses tanıma testi",
                        "usage": "/voice-test",
                        "examples": ["/voice-test"],
                        "aliases": ["/voice-check"]
                    },
                    "/voice-config": {
                        "desc": "Ses ayarlarını değiştir",
                        "usage": "/voice-config",
                        "examples": ["/voice-config"],
                        "aliases": ["/voice-settings"]
                    },
                    "/voice-add": {
                        "desc": "Yeni ses komutu ekle",
                        "usage": "/voice-add",
                        "examples": ["/voice-add"],
                        "aliases": ["/voice-new"]
                    },
                    "/voice-remove": {
                        "desc": "Ses komutu kaldır",
                        "usage": "/voice-remove",
                        "examples": ["/voice-remove"],
                        "aliases": ["/voice-delete"]
                    }
                }
            },
            "gelişmiş": {
                "desc": "Gelişmiş özellikler",
                "commands": {
                    "/suggest": {
                        "desc": "Kod önerileri al",
                        "usage": "/suggest [bağlam]",
                        "examples": ["/suggest", "/suggest dosya okuma"],
                        "aliases": ["/code-suggest"]
                    },
                    "/smart": {
                        "desc": "Akıllı dosya işlemleri",
                        "usage": "/smart [niyet]",
                        "examples": ["/smart", "/smart organize"],
                        "aliases": ["/smart-ops"]
                    },
                    "/context": {
                        "desc": "Bağlam analizi",
                        "usage": "/context",
                        "examples": ["/context"],
                        "aliases": ["/analyze-context"]
                    },
                    "/stats": {
                        "desc": "Kullanım istatistikleri",
                        "usage": "/stats [gün]",
                        "examples": ["/stats", "/stats 30"],
                        "aliases": ["/usage-stats"]
                    },
                    "/add-suggestion": {
                        "desc": "Yeni kod önerisi ekle",
                        "usage": "/add-suggestion",
                        "examples": ["/add-suggestion"],
                        "aliases": ["/new-suggestion"]
                    }
                }
            },
            "kısayol": {
                "desc": "Klavye kısayolları",
                "commands": {
                    "F1": {
                        "desc": "Yardım menüsü",
                        "usage": "F1",
                        "examples": ["F1"],
                        "aliases": []
                    },
                    "F2": {
                        "desc": "Model değiştir",
                        "usage": "F2",
                        "examples": ["F2"],
                        "aliases": []
                    },
                    "F3": {
                        "desc": "Geçmişi göster",
                        "usage": "F3",
                        "examples": ["F3"],
                        "aliases": []
                    },
                    "F4": {
                        "desc": "Dosya listesi",
                        "usage": "F4",
                        "examples": ["F4"],
                        "aliases": []
                    },
                    "F5": {
                        "desc": "Kod çalıştır",
                        "usage": "F5",
                        "examples": ["F5"],
                        "aliases": []
                    },
                    "Ctrl+R": {
                        "desc": "Geçmiş arama",
                        "usage": "Ctrl+R",
                        "examples": ["Ctrl+R"],
                        "aliases": []
                    },
                    "Tab": {
                        "desc": "Komut tamamlama",
                        "usage": "Tab",
                        "examples": ["Tab"],
                        "aliases": []
                    }
                }
            }
        }
        
    def get_all_help(self) -> Dict[str, Dict[str, Any]]:
        """Tüm yardım verilerini döndür"""
        return self.help_data
        
    def get_category_help(self, category: str) -> Optional[Dict[str, Any]]:
        """Kategori yardımını döndür"""
        return self.help_data.get(category)
        
    def get_command_help(self, command: str) -> Optional[Dict[str, Any]]:
        """Komut yardımını döndür"""
        for category_data in self.help_data.values():
            if command in category_data["commands"]:
                return category_data["commands"][command]
        return None
        
    def search_help(self, query: str) -> List[Dict[str, Any]]:
        """Yardım arama"""
        results = []
        query_lower = query.lower()
        
        for category, category_data in self.help_data.items():
            for cmd, cmd_data in category_data["commands"].items():
                if (query_lower in cmd.lower() or 
                    query_lower in cmd_data["desc"].lower() or
                    query_lower in category.lower()):
                    results.append({
                        "category": category,
                        "command": cmd,
                        "data": cmd_data
                    })
                    
        return results
        
    def get_categories(self) -> List[str]:
        """Kategori listesini döndür"""
        return list(self.help_data.keys())
        
    def get_commands_by_category(self, category: str) -> Dict[str, Dict[str, Any]]:
        """Kategoriye göre komutları döndür"""
        category_data = self.help_data.get(category)
        if category_data:
            return category_data["commands"]
        return {}
        
    def get_command_aliases(self, command: str) -> List[str]:
        """Komut alias'larını döndür"""
        cmd_data = self.get_command_help(command)
        if cmd_data and "aliases" in cmd_data:
            return cmd_data["aliases"]
        return []

# Global yardım sistemi instance'ı
help_system = HelpSystem()

def get_all_help() -> Dict[str, Dict[str, Any]]:
    """Tüm yardım verilerini al"""
    return help_system.get_all_help()

def get_category_help(category: str) -> Optional[Dict[str, Any]]:
    """Kategori yardımını al"""
    return help_system.get_category_help(category)

def get_command_help(command: str) -> Optional[Dict[str, Any]]:
    """Komut yardımını al"""
    return help_system.get_command_help(command)

def search_help(query: str) -> List[Dict[str, Any]]:
    """Yardım ara"""
    return help_system.search_help(query)

def get_categories() -> List[str]:
    """Kategori listesini al"""
    return help_system.get_categories()

def get_commands_by_category(category: str) -> Dict[str, Dict[str, Any]]:
    """Kategoriye göre komutları al"""
    return help_system.get_commands_by_category(category)

def get_command_aliases(command: str) -> List[str]:
    """Komut alias'larını al"""
    return help_system.get_command_aliases(command) 