#!/usr/bin/env python3
"""
CortexCLI Test Script
Tüm modülleri ve özellikleri test eder
"""

import sys
import os
import importlib
import subprocess
from pathlib import Path

def test_imports():
    """Temel modül import'larını test et"""
    print("🔍 Modül import'ları test ediliyor...")
    
    modules = [
        'llm_shell',
        'config',
        'plugin_system',
        'multi_model',
        'advanced_code_execution',
        'web_interface',
        'voice_commands',
        'advanced_features',
        'themes',
        'user_settings',
        'help_system'
    ]
    
    failed_imports = []
    
    for module in modules:
        try:
            importlib.import_module(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {e}")
            failed_imports.append(module)
    
    return len(failed_imports) == 0

def test_plugin_system():
    """Plugin sistemini test et"""
    print("\n🔌 Plugin sistemi test ediliyor...")
    
    try:
        from plugin_system import PluginManager
        pm = PluginManager()
        plugins = pm.list_plugins()
        print(f"✅ Plugin sistemi çalışıyor ({len(plugins)} plugin)")
        return True
    except Exception as e:
        print(f"❌ Plugin sistemi hatası: {e}")
        return False

def test_config():
    """Konfigürasyon dosyasını test et"""
    print("\n⚙️ Konfigürasyon test ediliyor...")
    
    try:
        from config import MODELS, DEFAULT_SETTINGS, get_model_name
        print(f"✅ Konfigürasyon yüklendi ({len(MODELS)} model)")
        print(f"✅ Varsayılan ayarlar: {len(DEFAULT_SETTINGS)} ayar")
        return True
    except Exception as e:
        print(f"❌ Konfigürasyon hatası: {e}")
        return False

def test_ollama_connection():
    """Ollama bağlantısını test et"""
    print("\n🤖 Ollama bağlantısı test ediliyor...")
    
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            print(f"✅ Ollama bağlantısı başarılı ({len(models)} model)")
            return True
        else:
            print(f"❌ Ollama API hatası: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ollama bağlantı hatası: {e}")
        return False

def test_file_operations():
    """Dosya işlemlerini test et"""
    print("\n📁 Dosya işlemleri test ediliyor...")
    
    try:
        # Test dosyası oluştur
        test_file = "test_output.txt"
        test_content = "Bu bir test dosyasıdır."
        
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        # Dosyayı oku
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Dosyayı sil
        os.remove(test_file)
        
        if content == test_content:
            print("✅ Dosya işlemleri başarılı")
            return True
        else:
            print("❌ Dosya içeriği eşleşmiyor")
            return False
            
    except Exception as e:
        print(f"❌ Dosya işlemleri hatası: {e}")
        return False

def test_web_interface():
    """Web arayüzü bağımlılıklarını test et"""
    print("\n🌐 Web arayüzü test ediliyor...")
    
    try:
        import flask
        import flask_socketio
        print("✅ Flask ve SocketIO yüklendi")
        return True
    except ImportError as e:
        print(f"❌ Web arayüzü bağımlılıkları eksik: {e}")
        return False

def test_voice_commands():
    """Ses komutları bağımlılıklarını test et"""
    print("\n🎤 Ses komutları test ediliyor...")
    
    try:
        import speech_recognition
        import pyttsx3
        print("✅ Ses komutları bağımlılıkları yüklendi")
        return True
    except ImportError as e:
        print(f"⚠️ Ses komutları bağımlılıkları eksik: {e}")
        return False

def test_data_analysis():
    """Veri analizi bağımlılıklarını test et"""
    print("\n📊 Veri analizi test ediliyor...")
    
    try:
        import pandas
        import matplotlib
        import numpy
        print("✅ Veri analizi bağımlılıkları yüklendi")
        return True
    except ImportError as e:
        print(f"❌ Veri analizi bağımlılıkları eksik: {e}")
        return False

def test_docker():
    """Docker bağımlılıklarını test et"""
    print("\n🐳 Docker test ediliyor...")
    
    try:
        import docker
        client = docker.from_env()
        print("✅ Docker bağımlılıkları yüklendi")
        return True
    except Exception as e:
        print(f"⚠️ Docker bağımlılıkları eksik veya Docker çalışmıyor: {e}")
        return False

def test_cli_commands():
    """CLI komutlarını test et"""
    print("\n💻 CLI komutları test ediliyor...")
    
    try:
        result = subprocess.run([sys.executable, 'llm_shell.py', '--help'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ CLI komutları çalışıyor")
            return True
        else:
            print(f"❌ CLI komutları hatası: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ CLI komutları test hatası: {e}")
        return False

def run_all_tests():
    """Tüm testleri çalıştır"""
    print("🚀 CortexCLI Test Suite Başlatılıyor...")
    print("=" * 50)
    
    tests = [
        ("Modül Import'ları", test_imports),
        ("Konfigürasyon", test_config),
        ("Plugin Sistemi", test_plugin_system),
        ("Ollama Bağlantısı", test_ollama_connection),
        ("Dosya İşlemleri", test_file_operations),
        ("Web Arayüzü", test_web_interface),
        ("Ses Komutları", test_voice_commands),
        ("Veri Analizi", test_data_analysis),
        ("Docker", test_docker),
        ("CLI Komutları", test_cli_commands)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test hatası: {e}")
            results.append((test_name, False))
    
    # Sonuçları özetle
    print("\n" + "=" * 50)
    print("📋 Test Sonuçları:")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ BAŞARILI" if result else "❌ BAŞARISIZ"
        print(f"{test_name:<25} {status}")
        if result:
            passed += 1
    
    print("=" * 50)
    print(f"📊 Toplam: {total} test, {passed} başarılı, {total - passed} başarısız")
    
    if passed == total:
        print("🎉 Tüm testler başarılı!")
        return True
    else:
        print("⚠️ Bazı testler başarısız oldu.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
