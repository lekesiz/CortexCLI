# CortexCLI - AI Assistant CLI

CortexCLI, Ollama modellerini kullanarak güçlü bir AI asistan CLI aracıdır. Qwen, DeepSeek ve diğer popüler modelleri destekler.

## 🌟 Özellikler

### 🔧 Temel Özellikler
- **Çoklu Model Desteği**: Qwen, DeepSeek, Llama ve diğer Ollama modelleri
- **Akıllı Başlatma**: Model kurulum sihirbazı ve otomatik yapılandırma
- **Sohbet Geçmişi**: Otomatik kaydetme ve yükleme
- **Çok Satırlı Giriş**: Shift+Enter ile uzun mesajlar
- **Sistem Prompt Presetleri**: Farklı kullanım senaryoları için hazır promptlar

### 📁 Dosya Sistemi Komutları
- `/read <dosya>` - Dosya okuma
- `/write <dosya> <içerik>` - Dosya yazma
- `/list [dizin]` - Dizin listeleme
- `/save <içerik>` - İçeriği dosyaya kaydetme
- `/delete <dosya>` - Dosya silme
- `/rename <eski> <yeni>` - Dosya yeniden adlandırma
- `/mkdir <dizin>` - Dizin oluşturma

### 🔌 Plugin Sistemi
- **Dinamik Plugin Yükleme**: Çalışma zamanında plugin ekleme/çıkarma
- **Web Arama**: Gerçek zamanlı web arama
- **Dosya Analizi**: Kod ve metin dosyalarını analiz etme
- **Özel Plugin Geliştirme**: Kolay plugin API'si

### 🤖 Çoklu Model Yönetimi
- **Model Ekleme/Çıkarma**: Dinamik model yönetimi
- **Paralel Sorgulama**: Birden fazla modeli aynı anda kullanma
- **Yanıt Karşılaştırma**: Farklı modellerin yanıtlarını karşılaştırma
- **Performans Metrikleri**: Yanıt süreleri ve kalite analizi

### 💻 Gelişmiş Kod Çalıştırma
- **Güvenli Sandbox**: Docker veya yerel çalıştırma
- **Kod Analizi**: Güvenlik ve performans analizi
- **Jupyter Notebook Entegrasyonu**: Notebook oluşturma ve çalıştırma
- **Debugging Araçları**: Hata ayıklama ve izleme

### 🌐 Web Arayüzü
- **Modern Dashboard**: Gerçek zamanlı istatistikler ve hızlı erişim
- **Canlı Sohbet**: WebSocket tabanlı gerçek zamanlı sohbet
- **Kod Editörü**: Syntax highlighting ve kod çalıştırma
- **Model Yönetimi**: Web üzerinden model ekleme/çıkarma
- **Dosya Yöneticisi**: Web tabanlı dosya yönetimi
- **Plugin Yönetimi**: Plugin'leri web arayüzünden yönetme

### 📦 Packaging & Distribution
- **PyPI Paketi**: `pip install cortexcli` ile kolay kurulum
- **Docker Desteği**: Containerized deployment
- **CI/CD Pipeline**: Otomatik test, build ve yayınlama
- **Multi-Platform**: Windows, macOS, Linux desteği

## 🚀 Kurulum

### Gereksinimler
- Python 3.8+
- Ollama (yerel kurulum)

### Yöntem 1: PyPI'dan Kurulum (Önerilen)
```bash
# Temel kurulum
pip install cortexcli

# Web arayüzü ile
pip install cortexcli[web]

# Tüm özellikler ile
pip install cortexcli[full]
```

### Yöntem 2: Kaynak Koddan Kurulum
```bash
# Projeyi indirin
git clone https://github.com/yourusername/cortexcli.git
cd cortexcli

# Bağımlılıkları yükleyin
pip install -r requirements.txt

# Geliştirici bağımlılıkları (opsiyonel)
pip install -r requirements.txt[dev]
```

### Yöntem 3: Docker ile Kurulum
```bash
# Docker image'ı çekin
docker pull yourusername/cortexcli:latest

# Web arayüzü ile çalıştırın
docker run -p 5000:5000 -p 11434:11434 yourusername/cortexcli:latest

# CLI modu ile çalıştırın
docker run -it yourusername/cortexcli:latest python llm_shell.py start
```

### Yöntem 4: Docker Compose ile Kurulum
```bash
# Docker Compose ile başlatın
docker-compose up -d

# Web arayüzü: http://localhost:5000
# Ollama API: http://localhost:11434
```

### Adım 4: İlk Modeli Kurun
```bash
ollama pull qwen2.5:7b
```

## 📖 Kullanım

### CLI Modu
```bash
# CortexCLI'yi başlat
cortexcli start

# Veya
python llm_shell.py start
```

### Web Arayüzü
```bash
# Web arayüzünü başlat
cortexcli web

# Veya
python llm_shell.py web

# Tarayıcınızda http://localhost:5000 adresini açın
```

### Temel Komutlar

#### Sohbet
```
Merhaba! Nasılsın?
```

#### Dosya İşlemleri
```
/list                    # Mevcut dizini listele
/read config.py          # Dosya oku
/write test.txt "Merhaba Dünya"  # Dosya yaz
/save "Bu bir test"      # İçeriği kaydet
```

#### Plugin Kullanımı
```
/plugins                 # Plugin listesi
/plugin web_search "Python nedir?"  # Web arama
/plugin file_analyzer analyze.py    # Dosya analizi
```

#### Model Yönetimi
```
/models                  # Model listesi
/add-model deepseek-coder:6.7b  # Model ekle
/compare "Merhaba"       # Modelleri karşılaştır
```

#### Kod Çalıştırma
```
/run-safe "print('Hello World')"  # Güvenli kod çalıştır
/analyze "import os; os.system('rm -rf /')"  # Kod analizi
/notebook "import pandas as pd"    # Jupyter notebook
```

## 🔧 Yapılandırma

### config.py
```python
# Varsayılan model
DEFAULT_MODEL = "qwen2.5:7b"

# Sistem prompt
DEFAULT_SYSTEM_PROMPT = "Sen yardımcı bir AI asistanısın."

# Çıktı dizini
OUTPUT_DIR = "output"

# Web arayüzü ayarları
WEB_HOST = "0.0.0.0"
WEB_PORT = 5000
```

## 🧩 Plugin Geliştirme

### Basit Plugin Örneği
```python
# plugins/my_plugin.py
class MyPlugin:
    def __init__(self):
        self.name = "my_plugin"
        self.description = "Benim özel plugin'im"
    
    def execute(self, command, args):
        if command == "hello":
            return f"Merhaba {args[0]}!"
        return "Bilinmeyen komut"
```

## 🌐 Web Arayüzü Özellikleri

### Dashboard
- Sistem durumu ve istatistikler
- Hızlı erişim butonları
- Son aktiviteler

### Chat
- Gerçek zamanlı sohbet
- Model seçimi
- Mesaj geçmişi
- Kod vurgulama

### Code Editor
- Syntax highlighting
- Çoklu dil desteği
- Güvenli kod çalıştırma
- Kod analizi

### Model Management
- Model listesi
- Kurulum/çıkarma
- Test ve karşılaştırma

### File Manager
- Dosya gezgini
- Dosya işlemleri
- İçerik önizleme

## 📦 Packaging & Distribution

### PyPI Paketi
```bash
# Paket build et
python build_script.py build

# Paket kontrol et
twine check dist/*

# TestPyPI'ya yükle
python publish.py --test

# PyPI'ya yükle
python publish.py
```

### Docker Image
```bash
# Docker image build et
docker build -t cortexcli:latest .

# Docker Compose ile çalıştır
docker-compose up -d
```

### CI/CD Pipeline
- **GitHub Actions**: Otomatik test, build ve yayınlama
- **Multi-Platform Testing**: Windows, macOS, Linux
- **Code Quality Checks**: Black, Flake8, MyPy
- **Automated Releases**: PyPI ve Docker Hub

## 🔒 Güvenlik

- **Sandbox Çalıştırma**: Kod güvenli ortamda çalıştırılır
- **Kod Analizi**: Güvenlik riskleri otomatik tespit edilir
- **Dosya İzolasyonu**: Sadece belirlenen dizinlere erişim
- **Timeout Koruması**: Sonsuz döngülere karşı koruma

## 🐛 Sorun Giderme

### Ollama Bağlantı Hatası
```bash
# Ollama servisini kontrol edin
ollama list

# Servisi yeniden başlatın
ollama serve
```

### Model Kurulum Hatası
```bash
# Modeli manuel olarak kurun
ollama pull qwen2.5:7b

# Disk alanını kontrol edin
df -h
```

### Web Arayüzü Hatası
```bash
# Port kullanımını kontrol edin
lsof -i :5000

# Flask bağımlılıklarını kontrol edin
pip install flask flask-socketio
```

### Docker Hatası
```bash
# Docker daemon'u başlatın
sudo systemctl start docker

# Docker Compose ile test edin
docker-compose up --build
```

## 🧪 Test

### Test Çalıştırma
```bash
# Tüm testleri çalıştır
python -m pytest tests/ -v

# Coverage ile test
python -m pytest tests/ --cov=. --cov-report=html

# Belirli test dosyası
python -m pytest tests/test_llm_shell.py -v
```

### Code Quality
```bash
# Code formatting
black .

# Linting
flake8 .

# Type checking
mypy .
```

## 🤝 Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit yapın (`git commit -m 'Add amazing feature'`)
4. Push yapın (`git push origin feature/amazing-feature`)
5. Pull Request oluşturun

### Geliştirme Kurulumu
```bash
# Geliştirici bağımlılıklarını yükleyin
pip install -e .[dev]

# Pre-commit hooks kurun
pre-commit install

# Testleri çalıştırın
python -m pytest tests/ -v
```

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için `LICENSE` dosyasına bakın.

## 🙏 Teşekkürler

- [Ollama](https://ollama.ai) - Yerel LLM çalıştırma
- [Qwen](https://qwen.ai) - AI modeli
- [DeepSeek](https://deepseek.com) - AI modeli
- [Rich](https://rich.readthedocs.io) - Terminal UI
- [Flask](https://flask.palletsprojects.com) - Web framework
- [Docker](https://docker.com) - Container platform

## 📞 İletişim

- GitHub: [@yourusername](https://github.com/yourusername)
- Email: your.email@example.com

---

**CortexCLI** - AI gücünü terminalinize getirin! 🚀 

## 🆕 Yeni Özellikler

### 📊 Gelişmiş Veri Analizi ve Görselleştirme
- **Histogram**: Veri dağılımını görselleştirme
- **Scatter Plot**: İki değişken arasındaki ilişkiyi analiz etme
- **Box Plot**: Veri istatistiklerini görselleştirme
- **Heatmap**: Korelasyon matrisini görselleştirme
- **Veri Temizleme**: Eksik değerleri doldurma, duplicate satırları kaldırma

```bash
# Veri analizi komutları
/analyze data.csv                    # CSV dosyasını analiz et
/describe data.csv                   # Temel istatistikleri göster
/histogram data.csv fiyat           # Histogram çiz
/scatter data.csv fiyat miktar      # Scatter plot çiz
/boxplot data.csv rating            # Box plot çiz
/heatmap data.csv                   # Korelasyon heatmap çiz
/clean data.csv                     # Veriyi temizle
```

### 🧮 Hesap Makinesi Plugin
- Matematik hesaplamaları
- Birim dönüşümleri (uzunluk, ağırlık, sıcaklık)
- Basit denklem çözme

```bash
# Hesap makinesi komutları
/calc 2+3*4                         # Matematik hesaplama
/convert 100 km to mi               # Birim dönüşümü
/convert 25 c to f                  # Sıcaklık dönüşümü
/solve x+5=10                       # Denklem çözme
/units                              # Desteklenen birimleri listele
```

### 📝 Not Alma Plugin
- Not ekleme, listeleme, arama
- Kategori bazlı organizasyon
- JSON formatında kalıcı depolama

```bash
# Not alma komutları
/note add Alışveriş | Süt, ekmek, yumurta al
/note list                          # Tüm notları listele
/note list alışveriş                # Kategori bazlı listeleme
/note search ekmek                  # Notlarda arama
/note show 1                        # Belirtilen notu göster
/note delete 1                      # Notu sil
/note categories                    # Kategorileri listele
```

### 📁 Gelişmiş Dosya Yönetimi
- Dosya listeleme ve filtreleme
- Dosya önizleme ve içerik arama
- Dizin ağacı görünümü
- Detaylı dosya bilgileri
- Dosya işlemleri (kopyala, taşı, sil, yeniden adlandır)

```bash
# Dosya yönetimi komutları
/files list [dizin] [--pattern <pattern>] [--type <type>]  # Dosyaları listele
/files preview <dosya>                                      # Dosya önizlemesi
/files search <anahtar_kelime> [dizin]                     # İçerik arama
/files find <dosya_adı> [dizin]                           # Dosya adı arama
/files info <dosya>                                        # Detaylı bilgi
/files tree [dizin] [--depth <depth>]                     # Ağaç görünümü
/files copy <kaynak> <hedef>                               # Dosya kopyala
/files move <kaynak> <hedef>                               # Dosya taşı
/files rename <eski_ad> <yeni_ad>                         # Yeniden adlandır
/files delete <dosya> [--force]                           # Dosya sil
/files mkdir <dizin>                                       # Dizin oluştur
```

### 📅 Takvim Plugin
- Etkinlik ekleme, listeleme, arama
- Günlük, haftalık, aylık görünüm
- Hatırlatıcı ayarlama
- Yaklaşan etkinlikleri görme

```bash
# Takvim komutları
/calendar add Toplantı | 2024-01-15 14:30 | Proje toplantısı
/calendar today                                        # Bugünkü etkinlikler
/calendar week                                         # Bu haftaki etkinlikler
/calendar month                                        # Bu ayki etkinlikler
/calendar list 2024-01-15                             # Belirli tarih
/calendar search toplantı                              # Etkinlik arama
/calendar delete 1                                     # Etkinlik silme
/calendar reminder 1 30                                # 30 dk önce hatırlat
/calendar upcoming                                     # Yaklaşan etkinlikler
```

### 💻 Gelişmiş Kod Editörü (Web)
- Jupyter notebook benzeri hücre sistemi
- Gerçek zamanlı kod çalıştırma
- Çoklu dil desteği (Python, JavaScript, Bash, HTML, CSS, SQL, JSON)
- Kod analizi ve güvenlik kontrolü
- Klavye kısayolları
- Hızlı örnekler ve şablonlar
- Otomatik kaydetme ve indirme

**Klavye Kısayolları:**
- `Ctrl+Enter` - Hücreyi çalıştır
- `Shift+Enter` - Yeni hücre ekle
- `Ctrl+Shift+Enter` - Tümünü çalıştır
- `Ctrl+S` - Kaydet
- `Ctrl+Z` - Geri al

**Özellikler:**
- Hücre bazlı kod yazma
- Gerçek zamanlı çıktı gösterimi
- Kod analizi (güvenlik, performans, kalite)
- Hızlı örnekler (Merhaba Dünya, Matematik, Liste İşlemleri, Dosya İşlemleri, Grafik Çizimi, API Çağrısı)
- Çoklu dil desteği
- Otomatik dosya kaydetme

```bash
# Hesap makinesi komutları
/calc 2+3*4                         # Matematik hesaplama
/convert 100 km to mi               # Birim dönüşümü
/convert 25 c to f                  # Sıcaklık dönüşümü
/solve x+5=10                       # Denklem çözme
/units                              # Desteklenen birimleri listele
```

```