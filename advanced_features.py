"""
Gelişmiş Özellikler Modülü
CortexCLI için AI destekli gelişmiş özellikler
"""

import os
import json
import re
import time
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import sqlite3
from collections import defaultdict
import difflib

@dataclass
class CodeSuggestion:
    """Kod önerisi"""
    code: str
    description: str
    confidence: float
    language: str
    context: str
    tags: List[str]

@dataclass
class SmartFileOperation:
    """Akıllı dosya işlemi"""
    operation: str
    source: str
    destination: Optional[str]
    description: str
    risk_level: str
    estimated_time: float

@dataclass
class ContextInfo:
    """Bağlam bilgisi"""
    current_file: Optional[str]
    current_directory: str
    recent_files: List[str]
    recent_commands: List[str]
    project_type: Optional[str]
    dependencies: List[str]
    git_status: Optional[str]

class AdvancedFeatures:
    """Gelişmiş özellikler sınıfı"""
    
    def __init__(self):
        self.db_path = Path("cortex_advanced.db")
        self.suggestions_db = Path("code_suggestions.json")
        self.context_history = []
        self.max_history = 100
        
        # Veritabanını başlat
        self._init_database()
        
        # Kod önerileri veritabanını yükle
        self._load_suggestions()
        
    def _init_database(self):
        """Veritabanını başlat"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Kullanım istatistikleri tablosu
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usage_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                feature TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                details TEXT,
                success BOOLEAN
            )
        ''')
        
        # Dosya işlemleri geçmişi
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS file_operations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                operation TEXT NOT NULL,
                source TEXT,
                destination TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                success BOOLEAN,
                error_message TEXT
            )
        ''')
        
        # Bağlam geçmişi
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS context_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                current_file TEXT,
                current_directory TEXT,
                recent_files TEXT,
                recent_commands TEXT,
                project_type TEXT,
                dependencies TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def _load_suggestions(self):
        """Kod önerilerini yükle"""
        if self.suggestions_db.exists():
            with open(self.suggestions_db, 'r', encoding='utf-8') as f:
                self.code_suggestions = json.load(f)
        else:
            self.code_suggestions = self._create_default_suggestions()
            self._save_suggestions()
            
    def _save_suggestions(self):
        """Kod önerilerini kaydet"""
        with open(self.suggestions_db, 'w', encoding='utf-8') as f:
            json.dump(self.code_suggestions, f, indent=2, ensure_ascii=False)
            
    def _create_default_suggestions(self) -> Dict:
        """Varsayılan kod önerilerini oluştur"""
        return {
            "python": {
                "file_operations": [
                    {
                        "code": "import os\nfrom pathlib import Path\n\n# Dosya işlemleri\npath = Path('file.txt')\nif path.exists():\n    content = path.read_text(encoding='utf-8')",
                        "description": "Güvenli dosya okuma",
                        "confidence": 0.9,
                        "tags": ["file", "io", "safe"]
                    }
                ],
                "data_processing": [
                    {
                        "code": "import pandas as pd\n\n# CSV dosyası okuma\ndf = pd.read_csv('data.csv')\nprint(df.head())",
                        "description": "Pandas ile veri okuma",
                        "confidence": 0.95,
                        "tags": ["pandas", "data", "csv"]
                    }
                ],
                "web_requests": [
                    {
                        "code": "import requests\n\n# HTTP isteği\nresponse = requests.get('https://api.example.com/data')\ndata = response.json()",
                        "description": "HTTP isteği yapma",
                        "confidence": 0.85,
                        "tags": ["requests", "http", "api"]
                    }
                ]
            },
            "javascript": {
                "async_operations": [
                    {
                        "code": "async function fetchData() {\n    const response = await fetch('/api/data');\n    const data = await response.json();\n    return data;\n}",
                        "description": "Async/await ile veri çekme",
                        "confidence": 0.9,
                        "tags": ["async", "fetch", "api"]
                    }
                ]
            }
        }
        
    def get_code_suggestions(self, context: str, language: str = "python", limit: int = 5) -> List[CodeSuggestion]:
        """Kod önerilerini al"""
        suggestions = []
        
        # Dil bazlı öneriler
        if language in self.code_suggestions:
            for category, category_suggestions in self.code_suggestions[language].items():
                for suggestion in category_suggestions:
                    # Bağlam eşleştirme
                    relevance_score = self._calculate_relevance(context, suggestion)
                    if relevance_score > 0.3:  # Minimum eşleşme
                        suggestions.append(CodeSuggestion(
                            code=suggestion["code"],
                            description=suggestion["description"],
                            confidence=suggestion["confidence"] * relevance_score,
                            language=language,
                            context=category,
                            tags=suggestion["tags"]
                        ))
        
        # Güven skoruna göre sırala ve limit uygula
        suggestions.sort(key=lambda x: x.confidence, reverse=True)
        return suggestions[:limit]
        
    def _calculate_relevance(self, context: str, suggestion: Dict) -> float:
        """Bağlam ile öneri arasındaki ilgiyi hesapla"""
        context_words = set(context.lower().split())
        suggestion_words = set()
        
        # Öneri metinlerinden kelimeleri çıkar
        suggestion_words.update(suggestion["description"].lower().split())
        suggestion_words.update(suggestion["tags"])
        
        # Jaccard benzerliği
        intersection = len(context_words.intersection(suggestion_words))
        union = len(context_words.union(suggestion_words))
        
        return intersection / union if union > 0 else 0
        
    def suggest_smart_file_operations(self, current_path: str, intent: str) -> List[SmartFileOperation]:
        """Akıllı dosya işlemi önerileri"""
        operations = []
        current_dir = Path(current_path)
        
        # Mevcut dosyaları analiz et
        files = list(current_dir.iterdir())
        
        if "organize" in intent.lower() or "düzenle" in intent.lower():
            # Dosya organizasyonu önerileri
            extensions = defaultdict(list)
            for file in files:
                if file.is_file():
                    ext = file.suffix.lower()
                    extensions[ext].append(file.name)
            
            # Benzer dosyaları grupla
            for ext, file_list in extensions.items():
                if len(file_list) > 3:
                    operations.append(SmartFileOperation(
                        operation="organize",
                        source=f"{len(file_list)} {ext} dosyası",
                        destination=f"organized/{ext[1:]}",
                        description=f"{ext} dosyalarını organize et",
                        risk_level="low",
                        estimated_time=2.0
                    ))
        
        elif "backup" in intent.lower() or "yedek" in intent.lower():
            # Yedekleme önerileri
            important_files = [f for f in files if f.is_file() and f.suffix in ['.py', '.js', '.json', '.md']]
            if important_files:
                operations.append(SmartFileOperation(
                    operation="backup",
                    source=f"{len(important_files)} önemli dosya",
                    destination="backup/",
                    description="Önemli dosyaları yedekle",
                    risk_level="low",
                    estimated_time=5.0
                ))
        
        elif "clean" in intent.lower() or "temizle" in intent.lower():
            # Temizlik önerileri
            temp_files = [f for f in files if f.is_file() and f.suffix in ['.tmp', '.log', '.cache']]
            if temp_files:
                operations.append(SmartFileOperation(
                    operation="clean",
                    source=f"{len(temp_files)} geçici dosya",
                    destination=None,
                    description="Geçici dosyaları temizle",
                    risk_level="medium",
                    estimated_time=1.0
                ))
        
        return operations
        
    def get_context_info(self, current_path: str = None) -> ContextInfo:
        """Mevcut bağlam bilgisini al"""
        if current_path is None:
            current_path = os.getcwd()
            
        current_dir = Path(current_path)
        
        # Son kullanılan dosyalar
        recent_files = []
        try:
            for file in current_dir.iterdir():
                if file.is_file() and file.stat().st_mtime > time.time() - 86400:  # Son 24 saat
                    recent_files.append(file.name)
        except:
            pass
        
        # Proje tipini belirle
        project_type = self._detect_project_type(current_dir)
        
        # Bağımlılıkları tespit et
        dependencies = self._detect_dependencies(current_dir)
        
        # Git durumu
        git_status = self._get_git_status(current_dir)
        
        return ContextInfo(
            current_file=None,
            current_directory=str(current_dir),
            recent_files=recent_files[:10],
            recent_commands=self.context_history[-10:] if self.context_history else [],
            project_type=project_type,
            dependencies=dependencies,
            git_status=git_status
        )
        
    def _detect_project_type(self, directory: Path) -> Optional[str]:
        """Proje tipini tespit et"""
        indicators = {
            "python": ["requirements.txt", "setup.py", "pyproject.toml", "__init__.py"],
            "javascript": ["package.json", "node_modules", "yarn.lock"],
            "java": ["pom.xml", "build.gradle", ".gradle"],
            "rust": ["Cargo.toml", "Cargo.lock"],
            "go": ["go.mod", "go.sum"],
            "php": ["composer.json", "composer.lock"],
            "ruby": ["Gemfile", "Gemfile.lock"]
        }
        
        for project_type, files in indicators.items():
            for file in files:
                if (directory / file).exists():
                    return project_type
        return None
        
    def _detect_dependencies(self, directory: Path) -> List[str]:
        """Bağımlılıkları tespit et"""
        dependencies = []
        
        # Python
        if (directory / "requirements.txt").exists():
            try:
                with open(directory / "requirements.txt", 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            dependencies.append(line.split('==')[0].split('>=')[0].split('<=')[0])
            except:
                pass
        
        # JavaScript
        if (directory / "package.json").exists():
            try:
                with open(directory / "package.json", 'r') as f:
                    data = json.load(f)
                    if 'dependencies' in data:
                        dependencies.extend(data['dependencies'].keys())
            except:
                pass
        
        return dependencies[:10]  # İlk 10 bağımlılık
        
    def _get_git_status(self, directory: Path) -> Optional[str]:
        """Git durumunu al"""
        try:
            import subprocess
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                  cwd=directory, capture_output=True, text=True)
            if result.returncode == 0:
                if result.stdout.strip():
                    return "modified"
                else:
                    return "clean"
        except:
            pass
        return None
        
    def add_suggestion(self, language: str, category: str, code: str, description: str, tags: List[str]):
        """Yeni kod önerisi ekle"""
        if language not in self.code_suggestions:
            self.code_suggestions[language] = {}
            
        if category not in self.code_suggestions[language]:
            self.code_suggestions[language][category] = []
            
        suggestion = {
            "code": code,
            "description": description,
            "confidence": 0.8,
            "tags": tags
        }
        
        self.code_suggestions[language][category].append(suggestion)
        self._save_suggestions()
        
    def log_usage(self, feature: str, details: str = None, success: bool = True):
        """Kullanım istatistiği kaydet"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO usage_stats (feature, details, success)
            VALUES (?, ?, ?)
        ''', (feature, details, success))
        
        conn.commit()
        conn.close()
        
    def log_file_operation(self, operation: str, source: str, destination: str = None, 
                          success: bool = True, error_message: str = None):
        """Dosya işlemi kaydet"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO file_operations (operation, source, destination, success, error_message)
            VALUES (?, ?, ?, ?, ?)
        ''', (operation, source, destination, success, error_message))
        
        conn.commit()
        conn.close()
        
    def update_context(self, command: str):
        """Bağlam geçmişini güncelle"""
        self.context_history.append(command)
        if len(self.context_history) > self.max_history:
            self.context_history.pop(0)
            
    def get_usage_stats(self, days: int = 7) -> Dict[str, Any]:
        """Kullanım istatistiklerini al"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Son N günün istatistikleri
        cursor.execute('''
            SELECT feature, COUNT(*) as count, AVG(CASE WHEN success THEN 1 ELSE 0 END) as success_rate
            FROM usage_stats
            WHERE timestamp >= datetime('now', '-{} days')
            GROUP BY feature
            ORDER BY count DESC
        '''.format(days))
        
        feature_stats = {}
        for row in cursor.fetchall():
            feature_stats[row[0]] = {
                "count": row[1],
                "success_rate": row[2]
            }
        
        # En çok kullanılan dosya işlemleri
        cursor.execute('''
            SELECT operation, COUNT(*) as count
            FROM file_operations
            WHERE timestamp >= datetime('now', '-{} days')
            GROUP BY operation
            ORDER BY count DESC
            LIMIT 10
        '''.format(days))
        
        file_ops = {row[0]: row[1] for row in cursor.fetchall()}
        
        conn.close()
        
        return {
            "feature_stats": feature_stats,
            "file_operations": file_ops,
            "period_days": days
        }
        
    def suggest_improvements(self, context: ContextInfo) -> List[str]:
        """İyileştirme önerileri"""
        suggestions = []
        
        # Proje tipine göre öneriler
        if context.project_type == "python":
            if not any("requirements.txt" in f for f in context.recent_files):
                suggestions.append("requirements.txt dosyası oluşturmayı düşünün")
            
            if not any("README.md" in f for f in context.recent_files):
                suggestions.append("README.md dosyası ekleyin")
                
        elif context.project_type == "javascript":
            if not any("package.json" in f for f in context.recent_files):
                suggestions.append("package.json dosyası oluşturun")
                
        # Git durumuna göre öneriler
        if context.git_status == "modified":
            suggestions.append("Değişiklikleri commit edin")
            
        # Dosya organizasyonu önerileri
        if len(context.recent_files) > 20:
            suggestions.append("Dosyaları klasörlere organize edin")
            
        return suggestions

# Global gelişmiş özellikler instance'ı
advanced_features = AdvancedFeatures()

def get_code_suggestions(context: str, language: str = "python", limit: int = 5) -> List[CodeSuggestion]:
    """Kod önerilerini al"""
    return advanced_features.get_code_suggestions(context, language, limit)

def suggest_smart_file_operations(current_path: str, intent: str) -> List[SmartFileOperation]:
    """Akıllı dosya işlemi önerileri"""
    return advanced_features.suggest_smart_file_operations(current_path, intent)

def get_context_info(current_path: str = None) -> ContextInfo:
    """Mevcut bağlam bilgisini al"""
    return advanced_features.get_context_info(current_path)

def add_code_suggestion(language: str, category: str, code: str, description: str, tags: List[str]):
    """Yeni kod önerisi ekle"""
    advanced_features.add_suggestion(language, category, code, description, tags)

def log_usage(feature: str, details: str = None, success: bool = True):
    """Kullanım istatistiği kaydet"""
    advanced_features.log_usage(feature, details, success)

def log_file_operation(operation: str, source: str, destination: str = None, 
                      success: bool = True, error_message: str = None):
    """Dosya işlemi kaydet"""
    advanced_features.log_file_operation(operation, source, destination, success, error_message)

def update_context(command: str):
    """Bağlam geçmişini güncelle"""
    advanced_features.update_context(command)

def get_usage_stats(days: int = 7) -> Dict[str, Any]:
    """Kullanım istatistiklerini al"""
    return advanced_features.get_usage_stats(days)

def suggest_improvements(context: ContextInfo) -> List[str]:
    """İyileştirme önerileri"""
    return advanced_features.suggest_improvements(context) 