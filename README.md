# DQai - CLI LLM Shell 🚀

Claude Code tarzında, terminal üzerinden kullanılabilen hafif ve özelleştirilebilir LLM sohbet uygulaması.

## ✨ Özellikler

- 🎯 **Hafif ve Hızlı**: Minimal bağımlılık, hızlı başlatma
- 🤖 **Çoklu Model Desteği**: Qwen, DeepSeek, CodeLlama, Llama2, Mistral
- 💾 **Geçmiş Kaydetme**: İsteğe bağlı sohbet geçmişi kaydetme
- 🔧 **Özelleştirilebilir**: Sistem prompt, çok satırlı giriş desteği
- 🎨 **Güzel Arayüz**: Rich kütüphanesi ile renkli terminal arayüzü
- 📦 **Kolay Kurulum**: Tek komutla model yükleme

## 🛠️ Kurulum

### 1. Ollama Kurulumu

```bash
# macOS
brew install ollama

# Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Windows
# https://ollama.ai/download adresinden indirin
```

### 2. Python Bağımlılıkları

```bash
pip install -r requirements.txt
```

### 3. Modelleri Yükleme

```bash
# Temel modeller
ollama pull qwen:7b
ollama pull deepseek-coder:6.7b

# Ek modeller (isteğe bağlı)
ollama pull codellama:7b
ollama pull llama2:7b
ollama pull mistral:7b
```

## 🚀 Kullanım

### Temel Kullanım

```bash
# Qwen modeli ile başlat
python llm_shell.py shell --model qwen

# DeepSeek modeli ile başlat
python llm_shell.py shell --model deepseek

# Geçmişi kaydet
python llm_shell.py shell --model qwen --save-history
```

### Gelişmiş Seçenekler

```bash
# Çok satırlı giriş desteği
python llm_shell.py shell --model qwen --multi-line

# Özel sistem prompt
python llm_shell.py shell --model deepseek --system-prompt "Sen bir Python uzmanısın"

# Özel geçmiş dosyası
python llm_shell.py shell --model qwen --save-history --history-file my_chat.txt
```

### Yardımcı Komutlar

```bash
# Mevcut modelleri listele
python llm_shell.py list-models

# Model yükle
python llm_shell.py install-model qwen
```

## 📋 Komut Referansı

### `shell` Komutu

```bash
python llm_shell.py shell [OPTIONS]
```

**Seçenekler:**
- `--model TEXT`: Model seç (qwen, deepseek, codellama, llama2, mistral)
- `--save-history`: Geçmişi kaydet
- `--history-file TEXT`: Geçmiş dosyası adı (varsayılan: chat_history.txt)
- `--system-prompt TEXT`: Sistem prompt'u
- `--multi-line`: Çok satırlı giriş desteği

### `list-models` Komutu

```bash
python llm_shell.py list-models
```

Desteklenen ve yüklü modelleri listeler.

### `install-model` Komutu

```bash
python llm_shell.py install-model <MODEL_NAME>
```

Belirtilen modeli Ollama üzerinden yükler.

## 🎯 Desteklenen Modeller

| Model | Ollama Adı | Açıklama |
|-------|------------|----------|
| qwen | qwen:7b | Alibaba'nın Qwen modeli |
| deepseek | deepseek-coder:6.7b | DeepSeek'in kod odaklı modeli |
| codellama | codellama:7b | Meta'nın kod odaklı modeli |
| llama2 | llama2:7b | Meta'nın Llama2 modeli |
| mistral | mistral:7b | Mistral AI'nin modeli |

## 💡 Kullanım Örnekleri

### Kod Yazma
```
🧠 Sen: Python'da bir web scraper yaz
🤖 Yanıt: [Kod örneği...]
```

### Çok Satırlı Kod
```
🧠 Sen (çok satırlı, 'END' ile bitir):
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
END
```

### Sistem Prompt ile
```bash
python llm_shell.py shell --model deepseek --system-prompt "Sen bir güvenlik uzmanısın"
```

## 🔧 Özelleştirme

### Yeni Model Ekleme

`llm_shell.py` dosyasındaki `MODELS` sözlüğüne yeni model ekleyebilirsiniz:

```python
MODELS = {
    "qwen": "qwen:7b",
    "deepseek": "deepseek-coder:6.7b",
    "yeni-model": "yeni-model:versiyon"  # Yeni model
}
```

### Özel Sistem Prompt'ları

```bash
# Python uzmanı
--system-prompt "Sen deneyimli bir Python geliştiricisisin"

# Güvenlik uzmanı
--system-prompt "Sen bir siber güvenlik uzmanısın"

# Çevirmen
--system-prompt "Sen profesyonel bir çevirmensin"
```

## 📁 Dosya Yapısı

```
DQai/
├── llm_shell.py          # Ana uygulama
├── requirements.txt      # Python bağımlılıkları
├── README.md            # Bu dosya
└── chat_history.txt     # Geçmiş dosyası (otomatik oluşur)
```

## 🐛 Sorun Giderme

### Ollama Bağlantı Hatası
```bash
# Ollama servisini başlat
ollama serve

# Servisin çalıştığını kontrol et
curl http://localhost:11434/api/tags
```

### Model Bulunamadı
```bash
# Modeli yükle
ollama pull qwen:7b

# Yüklü modelleri listele
ollama list
```

### Python Bağımlılık Hatası
```bash
# Bağımlılıkları yeniden yükle
pip install -r requirements.txt --upgrade
```

## 🤝 Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit yapın (`git commit -m 'Add amazing feature'`)
4. Push yapın (`git push origin feature/amazing-feature`)
5. Pull Request açın

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

## 🙏 Teşekkürler

- [Ollama](https://ollama.ai) - Yerel LLM çalıştırma
- [Typer](https://typer.tiangolo.com) - CLI framework
- [Rich](https://rich.readthedocs.io) - Terminal formatlaması
- [Requests](https://requests.readthedocs.io) - HTTP istekleri

---

**DQai** - Terminal üzerinden AI deneyimi! 🚀 