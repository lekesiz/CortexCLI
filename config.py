"""
DQai - Konfigürasyon Dosyası
Uygulama ayarları ve varsayılan değerler
"""

import os
from typing import Dict, List

# Desteklenen modeller
MODELS: Dict[str, str] = {
    "qwen": "qwen:7b",
    "deepseek": "deepseek-coder:6.7b",
    "codellama": "codellama:7b",
    "llama2": "llama2:7b",
    "mistral": "mistral:7b",
    "neural-chat": "neural-chat:7b",
    "phi": "phi:2.7b",
    "gemma": "gemma:2b"
}

# Varsayılan ayarlar
DEFAULT_SETTINGS = {
    "model": "qwen",
    "save_history": False,
    "history_file": "chat_history.txt",
    "system_prompt": None,
    "multi_line": False,
    "timeout": 60,
    "max_tokens": 2048,
    "temperature": 0.7
}

# Sistem prompt şablonları
SYSTEM_PROMPTS = {
    "python_expert": "Sen deneyimli bir Python geliştiricisisin. Kod örnekleri verirken açıklayıcı ol ve best practice'leri takip et.",
    "security_expert": "Sen bir siber güvenlik uzmanısın. Güvenlik açıklarını analiz et ve güvenli çözümler öner.",
    "translator": "Sen profesyonel bir çevirmensin. Verilen metni doğru ve anlamlı bir şekilde çevir.",
    "code_reviewer": "Sen deneyimli bir kod inceleme uzmanısın. Kod kalitesini, güvenliği ve performansı değerlendir.",
    "teacher": "Sen sabırlı bir öğretmensin. Karmaşık konuları basit ve anlaşılır şekilde açıkla.",
    "debugger": "Sen bir debug uzmanısın. Hataları analiz et ve çözüm önerileri sun."
}

# Renk şemaları
COLORS = {
    "primary": "green",
    "secondary": "cyan",
    "warning": "yellow",
    "error": "red",
    "info": "blue",
    "dim": "dim"
}

# Dosya uzantıları
SUPPORTED_FILE_EXTENSIONS = [".txt", ".md", ".py", ".js", ".html", ".css", ".json", ".yaml", ".yml"]

# Ollama API ayarları
OLLAMA_CONFIG = {
    "base_url": "http://localhost:11434",
    "api_endpoint": "/api/generate",
    "tags_endpoint": "/api/tags",
    "timeout": 60
}

def get_model_name(alias: str) -> str:
    """Model alias'ını tam adına çevirir"""
    return MODELS.get(alias.lower(), alias)

def get_available_models() -> List[str]:
    """Desteklenen model listesini döndürür"""
    return list(MODELS.keys())

def get_system_prompt(prompt_type: str) -> str:
    """Sistem prompt şablonunu döndürür"""
    return SYSTEM_PROMPTS.get(prompt_type, "")

def get_setting(key: str, default=None):
    """Ayar değerini döndürür"""
    return DEFAULT_SETTINGS.get(key, default)

def get_history_file_path() -> str:
    """Geçmiş dosyası yolunu döndürür"""
    return os.path.join(os.getcwd(), DEFAULT_SETTINGS["history_file"]) 