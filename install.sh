#!/bin/bash

# DQai - CLI LLM Shell Kurulum Scripti
# Bu script DQai uygulamasını ve gerekli bağımlılıkları kurar

set -e

echo "🚀 DQai CLI LLM Shell Kurulumu Başlıyor..."
echo "=========================================="

# Renk kodları
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Python versiyonunu kontrol et
echo -e "${BLUE}📋 Python versiyonu kontrol ediliyor...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    echo -e "${GREEN}✅ Python $PYTHON_VERSION bulundu${NC}"
else
    echo -e "${RED}❌ Python3 bulunamadı! Lütfen Python 3.10+ yükleyin.${NC}"
    exit 1
fi

# Python versiyonunu kontrol et (3.10+)
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 10 ]); then
    echo -e "${RED}❌ Python 3.10+ gerekli! Mevcut versiyon: $PYTHON_VERSION${NC}"
    exit 1
fi

# Ollama kontrolü
echo -e "${BLUE}📋 Ollama kontrol ediliyor...${NC}"
if command -v ollama &> /dev/null; then
    echo -e "${GREEN}✅ Ollama bulundu${NC}"
else
    echo -e "${YELLOW}⚠️  Ollama bulunamadı. Kuruluyor...${NC}"
    
    # İşletim sistemine göre Ollama kurulumu
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        echo -e "${BLUE}🍎 macOS için Ollama kuruluyor...${NC}"
        if command -v brew &> /dev/null; then
            brew install ollama
        else
            echo -e "${RED}❌ Homebrew bulunamadı! Lütfen önce Homebrew yükleyin.${NC}"
            echo "https://brew.sh adresinden Homebrew kurulumu yapabilirsiniz."
            exit 1
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        echo -e "${BLUE}🐧 Linux için Ollama kuruluyor...${NC}"
        curl -fsSL https://ollama.ai/install.sh | sh
    else
        echo -e "${RED}❌ Desteklenmeyen işletim sistemi: $OSTYPE${NC}"
        echo "Lütfen manuel olarak Ollama kurun: https://ollama.ai"
        exit 1
    fi
fi

# Python bağımlılıklarını kur
echo -e "${BLUE}📦 Python bağımlılıkları kuruluyor...${NC}"
if [ -f "requirements.txt" ]; then
    pip3 install -r requirements.txt
    echo -e "${GREEN}✅ Python bağımlılıkları kuruldu${NC}"
else
    echo -e "${RED}❌ requirements.txt dosyası bulunamadı!${NC}"
    exit 1
fi

# Script'i çalıştırılabilir yap
echo -e "${BLUE}🔧 Script çalıştırılabilir yapılıyor...${NC}"
chmod +x llm_shell.py
echo -e "${GREEN}✅ Script çalıştırılabilir yapıldı${NC}"

# Ollama servisini başlat
echo -e "${BLUE}🚀 Ollama servisi başlatılıyor...${NC}"
if ! pgrep -x "ollama" > /dev/null; then
    echo -e "${YELLOW}⚠️  Ollama servisi başlatılıyor...${NC}"
    ollama serve &
    sleep 3
fi

# Test modellerini kontrol et
echo -e "${BLUE}📋 Mevcut modeller kontrol ediliyor...${NC}"
python3 llm_shell.py list-models

echo ""
echo -e "${GREEN}🎉 Kurulum tamamlandı!${NC}"
echo "=========================================="
echo ""
echo -e "${BLUE}🚀 Kullanmaya başlamak için:${NC}"
echo -e "${GREEN}python3 llm_shell.py shell --model qwen${NC}"
echo ""
echo -e "${BLUE}📚 Yardım için:${NC}"
echo -e "${GREEN}python3 llm_shell.py --help${NC}"
echo ""
echo -e "${BLUE}📖 Detaylı dokümantasyon için README.md dosyasını okuyun.${NC}"
echo ""
echo -e "${YELLOW}💡 İpucu: Modelleri yüklemek için:${NC}"
echo -e "${GREEN}python3 llm_shell.py install-model qwen${NC}"
echo "" 