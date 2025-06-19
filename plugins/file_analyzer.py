"""
Dosya Analiz Plugin'i
Dosya analizi ve işleme özellikleri
"""

import os
import hashlib
import mimetypes
from pathlib import Path
from plugin_system import PluginBase
from typing import Dict, Callable

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
            "stats": self.file_stats,
            "hash": self.file_hash,
            "type": self.file_type,
            "find": self.find_files
        }
        
    def analyze_file(self, file_path: str) -> str:
        """Dosya analizi yapar"""
        try:
            if not os.path.exists(file_path):
                return f"❌ Dosya bulunamadı: {file_path}"
                
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            lines = len(content.split('\n'))
            chars = len(content)
            words = len(content.split())
            
            # Dosya türü analizi
            mime_type, _ = mimetypes.guess_type(file_path)
            file_type = mime_type or "Bilinmeyen"
            
            # Satır türleri
            empty_lines = len([line for line in content.split('\n') if not line.strip()])
            code_lines = len([line for line in content.split('\n') if line.strip() and not line.strip().startswith('#')])
            comment_lines = len([line for line in content.split('\n') if line.strip().startswith('#')])
            
            return f"📊 {file_path} analizi:\n" \
                   f"  Tür: {file_type}\n" \
                   f"  Satır: {lines}\n" \
                   f"  Boş satır: {empty_lines}\n" \
                   f"  Kod satırı: {code_lines}\n" \
                   f"  Yorum satırı: {comment_lines}\n" \
                   f"  Karakter: {chars:,}\n" \
                   f"  Kelime: {words:,}"
                   
        except Exception as e:
            return f"❌ Dosya analiz hatası: {e}"
            
    def file_stats(self, file_path: str) -> str:
        """Dosya istatistikleri"""
        try:
            if not os.path.exists(file_path):
                return f"❌ Dosya bulunamadı: {file_path}"
                
            stat = os.stat(file_path)
            
            # Boyut formatı
            size = stat.st_size
            if size < 1024:
                size_str = f"{size} B"
            elif size < 1024**2:
                size_str = f"{size/1024:.1f} KB"
            elif size < 1024**3:
                size_str = f"{size/1024**2:.1f} MB"
            else:
                size_str = f"{size/1024**3:.1f} GB"
                
            from datetime import datetime
            created = datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
            modified = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            
            return f"📈 {file_path} istatistikleri:\n" \
                   f"  Boyut: {size_str}\n" \
                   f"  Oluşturulma: {created}\n" \
                   f"  Değiştirilme: {modified}\n" \
                   f"  İzinler: {oct(stat.st_mode)[-3:]}"
                   
        except Exception as e:
            return f"❌ İstatistik hatası: {e}"
            
    def file_hash(self, file_path: str) -> str:
        """Dosya hash değerini hesaplar"""
        try:
            if not os.path.exists(file_path):
                return f"❌ Dosya bulunamadı: {file_path}"
                
            hash_md5 = hashlib.md5()
            hash_sha1 = hashlib.sha1()
            hash_sha256 = hashlib.sha256()
            
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
                    hash_sha1.update(chunk)
                    hash_sha256.update(chunk)
                    
            return f"🔐 {file_path} hash değerleri:\n" \
                   f"  MD5: {hash_md5.hexdigest()}\n" \
                   f"  SHA1: {hash_sha1.hexdigest()}\n" \
                   f"  SHA256: {hash_sha256.hexdigest()}"
                   
        except Exception as e:
            return f"❌ Hash hesaplama hatası: {e}"
            
    def file_type(self, file_path: str) -> str:
        """Dosya türünü belirler"""
        try:
            if not os.path.exists(file_path):
                return f"❌ Dosya bulunamadı: {file_path}"
                
            mime_type, encoding = mimetypes.guess_type(file_path)
            
            if mime_type:
                return f"📄 {file_path} türü:\n" \
                       f"  MIME: {mime_type}\n" \
                       f"  Encoding: {encoding or 'Bilinmiyor'}"
            else:
                return f"📄 {file_path} türü: Bilinmeyen"
                
        except Exception as e:
            return f"❌ Dosya türü hatası: {e}"
            
    def find_files(self, pattern: str, directory: str = ".") -> str:
        """Belirtilen dizinde dosya arar"""
        try:
            if not os.path.exists(directory):
                return f"❌ Dizin bulunamadı: {directory}"
                
            found_files = []
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if pattern.lower() in file.lower():
                        full_path = os.path.join(root, file)
                        found_files.append(full_path)
                        
            if found_files:
                result = f"🔍 '{pattern}' için {len(found_files)} dosya bulundu:\n"
                for file_path in found_files[:10]:  # İlk 10 dosyayı göster
                    result += f"  📄 {file_path}\n"
                if len(found_files) > 10:
                    result += f"  ... ve {len(found_files) - 10} dosya daha"
                return result
            else:
                return f"🔍 '{pattern}' için dosya bulunamadı"
                
        except Exception as e:
            return f"❌ Dosya arama hatası: {e}" 