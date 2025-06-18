# DQai - Kullanım Örnekleri 🚀

Bu dosya DQai CLI LLM Shell'in çeşitli kullanım senaryolarını ve örneklerini içerir.

## 🎯 Temel Kullanım Örnekleri

### 1. Basit Sohbet
```bash
# Qwen modeli ile başlat
python llm_shell.py shell --model qwen

# DeepSeek modeli ile başlat
python llm_shell.py shell --model deepseek
```

### 2. Geçmiş Kaydetme
```bash
# Sohbet geçmişini kaydet
python llm_shell.py shell --model qwen --save-history

# Özel geçmiş dosyası
python llm_shell.py shell --model deepseek --save-history --history-file my_chat.txt
```

### 3. Sistem Prompt Şablonları
```bash
# Python uzmanı olarak
python llm_shell.py shell --model deepseek --system-preset python_expert

# Güvenlik uzmanı olarak
python llm_shell.py shell --model qwen --system-preset security_expert

# Öğretmen olarak
python llm_shell.py shell --model mistral --system-preset teacher
```

### 4. Çok Satırlı Giriş
```bash
# Çok satırlı kod yazma
python llm_shell.py shell --model codellama --multi-line
```

### 5. Dosya İçeriği ile Sohbet
```bash
# Bir dosyanın içeriğini analiz et
python llm_shell.py shell --model deepseek --file-input my_script.py
```

## 💻 Kod Geliştirme Senaryoları

### Senaryo 1: Python Web Scraper
```bash
python llm_shell.py shell --model deepseek --system-preset python_expert
```

**Prompt:**
```
Python'da requests ve BeautifulSoup kullanarak bir web scraper yaz. 
Hedef site: https://example.com
Çıkarılacak veriler: başlıklar ve linkler
```

### Senaryo 2: API Entegrasyonu
```bash
python llm_shell.py shell --model codellama --system-preset python_expert
```

**Prompt:**
```
OpenWeatherMap API'sini kullanarak hava durumu uygulaması yaz.
API key'i environment variable'dan al.
JSON response'u parse et ve güzel bir çıktı ver.
```

### Senaryo 3: Veri Analizi
```bash
python llm_shell.py shell --model qwen --system-preset python_expert
```

**Prompt:**
```
Pandas kullanarak CSV dosyasından veri analizi yap.
- Veri temizleme
- İstatistiksel analiz
- Görselleştirme (matplotlib)
```

## 🔒 Güvenlik Senaryoları

### Senaryo 1: Kod Güvenlik Analizi
```bash
python llm_shell.py shell --model deepseek --system-preset security_expert --file-input my_app.py
```

**Prompt:**
```
Bu Python kodundaki güvenlik açıklarını analiz et ve öneriler sun.
```

### Senaryo 2: Şifreleme Uygulaması
```bash
python llm_shell.py shell --model qwen --system-preset security_expert
```

**Prompt:**
```
AES şifreleme kullanarak dosya şifreleme uygulaması yaz.
Güvenli key generation ve salt kullan.
```

## 🌍 Çeviri Senaryoları

### Senaryo 1: Metin Çevirisi
```bash
python llm_shell.py shell --model mistral --system-preset translator
```

**Prompt:**
```
Bu metni İngilizce'den Türkçe'ye çevir:
"Hello, how are you today? I hope you're having a great day."
```

### Senaryo 2: Kod Yorumları Çevirisi
```bash
python llm_shell.py shell --model deepseek --system-preset translator --file-input code_with_comments.py
```

**Prompt:**
```
Bu kod dosyasındaki tüm yorumları Türkçe'ye çevir.
```

## 🐛 Debug Senaryoları

### Senaryo 1: Hata Analizi
```bash
python llm_shell.py shell --model deepseek --system-preset debugger --file-input error_log.txt
```

**Prompt:**
```
Bu hata log'unu analiz et ve çözüm önerileri sun.
```

### Senaryo 2: Performans Optimizasyonu
```bash
python llm_shell.py shell --model codellama --system-preset code_reviewer --file-input slow_script.py
```

**Prompt:**
```
Bu kodun performansını analiz et ve optimizasyon önerileri sun.
```

## 📚 Öğrenme Senaryoları

### Senaryo 1: Konsept Açıklama
```bash
python llm_shell.py shell --model mistral --system-preset teacher
```

**Prompt:**
```
Decorator pattern'i basit bir örnekle açıkla.
Ne zaman kullanılır ve avantajları nelerdir?
```

### Senaryo 2: Algoritma Öğrenme
```bash
python llm_shell.py shell --model deepseek --system-preset teacher
```

**Prompt:**
```
Binary Search algoritmasını adım adım açıkla.
Zaman karmaşıklığı nedir?
Python'da implementasyonu nasıl yapılır?
```

## 🚀 Hızlı Komutlar

### Tek Seferlik Sorular
```bash
# Hızlı soru-cevap
python llm_shell.py quick-chat "Python'da list comprehension nedir?" --model qwen

# Yaratıcılık seviyesi ile
python llm_shell.py quick-chat "Yaratıcı bir hikaye yaz" --model mistral --temperature 0.9
```

### Model Yönetimi
```bash
# Modelleri listele
python llm_shell.py list-models

# Model yükle
python llm_shell.py install-model qwen

# Sistem şablonlarını listele
python llm_shell.py list-presets
```

## 🎨 Özelleştirme Örnekleri

### Özel Sistem Prompt
```bash
python llm_shell.py shell --model deepseek --system-prompt "Sen bir DevOps mühendisisin. Docker ve Kubernetes konularında uzmansın."
```

### Temperature Ayarı
```bash
# Yaratıcı yanıtlar için
python llm_shell.py shell --model mistral --temperature 0.9

# Tutarlı yanıtlar için
python llm_shell.py shell --model deepseek --temperature 0.1
```

## 📝 Geçmiş Dosyası Örneği

```txt
=== 2024-01-15 14:30:25 (Model: qwen:7b) ===
🧠 Sen: Python'da decorator nedir?
🤖 Yanıt: Decorator, Python'da fonksiyonları veya sınıfları değiştirmek için kullanılan bir tasarım desenidir...

--------------------------------------------------

=== 2024-01-15 14:35:12 (Model: qwen:7b) ===
🧠 Sen: Örnek bir decorator yaz
🤖 Yanıt: İşte basit bir decorator örneği:

def timer_decorator(func):
    def wrapper(*args, **kwargs):
        import time
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} {end - start:.2f} saniye sürdü")
        return result
    return wrapper

@timer_decorator
def slow_function():
    import time
    time.sleep(1)
    return "Tamamlandı!"

--------------------------------------------------
```

## 🔧 Gelişmiş Kullanım

### Çoklu Dosya Analizi
```bash
# Birden fazla dosyayı analiz et
python llm_shell.py shell --model deepseek --system-preset code_reviewer --file-input main.py
```

**Prompt:**
```
Bu dosyayı analiz et ve iyileştirme önerileri sun.
Ayrıca test yazılması gereken yerleri belirt.
```

### API Dokümantasyonu
```bash
python llm_shell.py shell --model deepseek --system-preset python_expert --file-input api.py
```

**Prompt:**
```
Bu API fonksiyonları için docstring'ler yaz.
Parametreleri, dönüş değerlerini ve örnekleri içersin.
```

---

Bu örnekler DQai'nin gücünü göstermek için hazırlanmıştır. Kendi senaryolarınızı oluşturmak için bu örnekleri temel alabilirsiniz! 🚀 