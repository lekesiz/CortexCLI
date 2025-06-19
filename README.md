# CortexCLI - Cloud Code Benzeri CLI LLM Shell

CortexCLI, Claude Code tarzında çalışan, terminal üzerinden kullanılabilen güçlü bir LLM sohbet uygulamasıdır. Ollama modelleri ile entegre çalışır ve Cloud Code benzeri context-aware özellikler sunar.

## 🌟 Yeni Özellikler (Cloud Code Benzeri)

### Context-Aware AI
- **Proje Context'i**: LLM tüm proje yapısını görür ve anlar
- **Dosya Context'i**: Belirli dosyaları analiz eder ve kod yapısını anlar
- **Akıllı Yanıtlar**: Mevcut kod yapısına göre öneriler verir

### Gelişmiş Dosya Sistemi
- **Akıllı Navigasyon**: `/find` komutu ile dosya arama
- **Kod Analizi**: `/context analyze` ile dosya yapısı analizi
- **Dosya Ağacı**: `/tree` komutu ile görsel dosya yapısı
- **İçerik Arama**: `/search` ve `/grep` ile dosya içeriğinde arama
- **Dosya Karşılaştırma**: `/diff` ile dosya farklarını görme

### Context Komutları
```bash
/context                    # Context durumunu göster
/context on                 # Context-aware modu aç
/context off                # Context-aware modu kapat
/context file main.py       # Belirli dosyayı context'e ekle
/context clear              # Context dosyasını temizle
/context project            # Proje context'ini göster
/context analyze app.py     # Dosya kod analizi yap
/find main.py               # Akıllı dosya arama
```

### Gelişmiş Dosya Komutları
```bash
/tree                       # Dosya ağacını göster
/search "function" app.py   # Dosya içeriğinde arama
/grep "import.*requests"    # Regex ile arama
/diff file1.py file2.py     # Dosya farklarını göster
/stats main.py              # Dosya istatistikleri
```

## 🚀 Kurulum

### Gereksinimler
- Python 3.8+
- Ollama (yerel LLM modelleri için)

### Hızlı Kurulum
```bash
# Projeyi klonla
git clone https://github.com/yourusername/cortexcli.git
cd cortexcli

# Bağımlılıkları yükle
pip install -r requirements.txt

# Ollama'yı başlat
ollama serve

# CortexCLI'yi başlat
./cortexai start
```

## 📖 Kullanım

### Temel Kullanım
```bash
# CLI'yi başlat
./cortexai start

# Web arayüzünü başlat
./cortexai web

# Hızlı soru
./cortexai quick "Python'da dosya nasıl okunur?"
```

### Context-Aware Kullanım
```bash
# Proje context'ini göster
/context project

# Belirli dosyayı analiz et
/context analyze main.py

# Dosyayı context'e ekle ve soru sor
/context file app.py
"Bu dosyada hangi fonksiyonlar var?"

# Akıllı dosya arama
/find "config"
```

### Dosya Sistemi
```bash
# Dosya ağacını göster
/tree

# Dosya içeriğinde arama
/search "def main" *.py

# Regex ile arama
/grep "import.*requests" *.py

# Dosya istatistikleri
/stats main.py
```

## 🔧 Özellikler

### 🤖 Model Yönetimi
- **Çoklu Model Desteği**: Qwen, DeepSeek, CodeLlama, Llama2
- **Model Karşılaştırma**: Aynı soruyu farklı modellerle test et
- **Otomatik Model Kurulumu**: Eksik modelleri otomatik indir

### 📁 Dosya Sistemi
- **Context-Aware Dosya İşlemleri**: LLM dosya yapısını anlar
- **Akıllı Navigasyon**: Dosya arama ve analiz
- **Kod Analizi**: AST tabanlı kod yapısı analizi
- **Dosya Karşılaştırma**: Diff görüntüleme

### 🔌 Plugin Sistemi
- **Web Arama**: Google, Wikipedia entegrasyonu
- **Hava Durumu**: Gerçek zamanlı hava durumu
- **Hesap Makinesi**: Matematik hesaplamaları
- **Takvim**: Etkinlik yönetimi
- **Notlar**: Not alma ve yönetimi
- **Veri Analizi**: CSV dosyaları analizi

### 🎨 Tema Sistemi
- **Çoklu Tema**: Dark, Light, Custom temalar
- **Dinamik CSS**: Web arayüzü için özel temalar
- **CLI Temaları**: Terminal için renkli temalar

### 🎤 Ses Komutları
- **Ses Tanıma**: Konuşma ile komut verme
- **Text-to-Speech**: Yanıtları sesli okuma
- **Özel Ses Komutları**: Kendi ses komutlarını ekle

### 🌐 Web Arayüzü
- **Real-time Chat**: SocketIO ile gerçek zamanlı sohbet
- **Kod Editörü**: Syntax highlighting ile kod yazma
- **Model Yönetimi**: Web üzerinden model kontrolü
- **Dosya Yönetimi**: Drag & drop dosya yükleme
- **Plugin Yönetimi**: Web üzerinden plugin kontrolü

## 📊 Gelişmiş Özellikler

### Context-Aware AI
CortexCLI, Cloud Code gibi proje yapısını anlar:

```bash
# Proje context'ini göster
/context project

# Belirli dosyayı analiz et
/context analyze main.py

# Context-aware soru sor
"Bu projede hangi import'lar kullanılıyor?"
"main.py dosyasında hangi fonksiyonlar var?"
"Bu kodda güvenlik açığı var mı?"
```

### Kod Analizi
```bash
# Dosya yapısını analiz et
/context analyze app.py

# Kod istatistikleri
/stats main.py

# Güvenlik analizi
/analyze --file app.py
```

### Akıllı Dosya Arama
```bash
# Dosya adı ile arama
/find main.py

# Pattern ile arama
/find "config"

# Klasör arama
/find "src"
```

## 🛠️ Geliştirme

### Plugin Geliştirme
```python
# plugins/my_plugin.py
class MyPlugin:
    def __init__(self):
        self.name = "My Plugin"
        self.description = "Açıklama"
        self.commands = {'/mycmd': self.my_function}
    
    def execute(self, command, args):
        return "Sonuç"
```

### Tema Geliştirme
```json
{
    "name": "Custom Theme",
    "colors": {
        "primary": "#007acc",
        "secondary": "#1e1e1e",
        "accent": "#ff6b6b"
    }
}
```

## 📝 Örnekler

### Context-Aware Kod Yazma
```bash
# Proje context'ini aç
/context project

# Soru sor
"Bu projeye yeni bir API endpoint ekle"

# LLM proje yapısını anlayarak yanıt verir
```

### Dosya Analizi
```bash
# Dosyayı analiz et
/context analyze app.py

# Sonuç:
# === KOD ANALİZİ: app.py ===
# Dil: Python
# Satır sayısı: 150
# Import'lar: flask, requests, json
# Fonksiyonlar: main, api_handler, validate_input
# Sınıflar: App, Database
```

### Akıllı Arama
```bash
# Dosya arama
/find "config"

# Sonuç:
# Bulunan dosya: config.py
# === DOSYA: config.py ===
# Boyut: 45 satır
# [dosya içeriği...]
```

## 🔍 Sorun Giderme

### Ollama Bağlantı Sorunu
```bash
# Ollama servisini kontrol et
ollama list

# Servisi yeniden başlat
ollama serve
```

### Model Kurulum Sorunu
```bash
# Modeli manuel kur
ollama pull qwen2.5:7b

# Kurulum durumunu kontrol et
ollama list
```

### Context Sorunları
```bash
# Context'i temizle
/context clear

# Context modunu kapat
/context off

# Proje context'ini yenile
/context project
```

## 📄 Lisans

MIT License - Detaylar için [LICENSE](LICENSE) dosyasına bakın.

## 🤝 Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit yapın (`git commit -m 'Add amazing feature'`)
4. Push yapın (`git push origin feature/amazing-feature`)
5. Pull Request açın

## 📞 İletişim

- GitHub Issues: [Proje Issues](https://github.com/yourusername/cortexcli/issues)
- Email: your.email@example.com

---

**CortexCLI** - Cloud Code benzeri deneyim, terminal üzerinde! 🚀
