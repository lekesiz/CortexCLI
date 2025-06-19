"""
Data Analyzer Plugin - Veri analizi ve görselleştirme
Kullanım:
  /analyze <csv_dosyası>
  /describe <csv_dosyası>
  /plot <csv_dosyası> <kolon1> <kolon2>
  /histogram <csv_dosyası> <kolon>
  /scatter <csv_dosyası> <kolon1> <kolon2>
  /boxplot <csv_dosyası> <kolon>
  /heatmap <csv_dosyası>
  /clean <csv_dosyası>
"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
from pathlib import Path
import numpy as np

def analyze(csv_file: str) -> str:
    """CSV dosyasını analiz eder ve özetler."""
    try:
        df = pd.read_csv(csv_file)
        info = io.StringIO()
        df.info(buf=info)
        head = df.head().to_string()
        return f"[bold]Özet Bilgi:[/bold]\n{info.getvalue()}\n\n[bold]İlk Satırlar:[/bold]\n{head}"
    except Exception as e:
        return f"[HATA] Analiz hatası: {e}"

def describe(csv_file: str) -> str:
    """CSV dosyasının temel istatistiklerini döndürür."""
    try:
        df = pd.read_csv(csv_file)
        desc = df.describe(include='all').to_string()
        return f"[bold]Temel İstatistikler:[/bold]\n{desc}"
    except Exception as e:
        return f"[HATA] İstatistik hatası: {e}"

def plot(csv_file: str, col1: str, col2: str) -> str:
    """İki kolonu çizdirir ve görseli kaydeder."""
    try:
        df = pd.read_csv(csv_file)
        if col1 not in df.columns or col2 not in df.columns:
            return f"[HATA] Kolon bulunamadı: {col1}, {col2}"
        plt.figure(figsize=(8,5))
        plt.plot(df[col1], df[col2], marker='o')
        plt.xlabel(col1)
        plt.ylabel(col2)
        plt.title(f"{col1} vs {col2}")
        plt.grid(True)
        img_path = Path("output") / f"plot_{col1}_{col2}.png"
        img_path.parent.mkdir(exist_ok=True)
        plt.savefig(img_path)
        plt.close()
        return f"[bold green]Grafik kaydedildi:[/bold green] {img_path}"
    except Exception as e:
        return f"[HATA] Grafik çizim hatası: {e}"

def histogram(csv_file: str, column: str) -> str:
    """Belirtilen kolon için histogram çizer."""
    try:
        df = pd.read_csv(csv_file)
        if column not in df.columns:
            return f"[HATA] Kolon bulunamadı: {column}"
        
        plt.figure(figsize=(10,6))
        plt.hist(df[column].dropna(), bins=30, alpha=0.7, color='skyblue', edgecolor='black')
        plt.xlabel(column)
        plt.ylabel('Frekans')
        plt.title(f'{column} Histogramı')
        plt.grid(True, alpha=0.3)
        
        img_path = Path("output") / f"histogram_{column}.png"
        img_path.parent.mkdir(exist_ok=True)
        plt.savefig(img_path)
        plt.close()
        return f"[bold green]Histogram kaydedildi:[/bold green] {img_path}"
    except Exception as e:
        return f"[HATA] Histogram hatası: {e}"

def scatter(csv_file: str, col1: str, col2: str) -> str:
    """İki kolon için scatter plot çizer."""
    try:
        df = pd.read_csv(csv_file)
        if col1 not in df.columns or col2 not in df.columns:
            return f"[HATA] Kolon bulunamadı: {col1}, {col2}"
        
        plt.figure(figsize=(10,6))
        plt.scatter(df[col1], df[col2], alpha=0.6, s=50)
        plt.xlabel(col1)
        plt.ylabel(col2)
        plt.title(f'{col1} vs {col2} Scatter Plot')
        plt.grid(True, alpha=0.3)
        
        # Trend çizgisi ekle
        z = np.polyfit(df[col1].dropna(), df[col2].dropna(), 1)
        p = np.poly1d(z)
        plt.plot(df[col1], p(df[col1]), "r--", alpha=0.8)
        
        img_path = Path("output") / f"scatter_{col1}_{col2}.png"
        img_path.parent.mkdir(exist_ok=True)
        plt.savefig(img_path)
        plt.close()
        return f"[bold green]Scatter plot kaydedildi:[/bold green] {img_path}"
    except Exception as e:
        return f"[HATA] Scatter plot hatası: {e}"

def boxplot(csv_file: str, column: str) -> str:
    """Belirtilen kolon için box plot çizer."""
    try:
        df = pd.read_csv(csv_file)
        if column not in df.columns:
            return f"[HATA] Kolon bulunamadı: {column}"
        
        plt.figure(figsize=(8,6))
        plt.boxplot(df[column].dropna())
        plt.ylabel(column)
        plt.title(f'{column} Box Plot')
        plt.grid(True, alpha=0.3)
        
        img_path = Path("output") / f"boxplot_{column}.png"
        img_path.parent.mkdir(exist_ok=True)
        plt.savefig(img_path)
        plt.close()
        return f"[bold green]Box plot kaydedildi:[/bold green] {img_path}"
    except Exception as e:
        return f"[HATA] Box plot hatası: {e}"

def heatmap(csv_file: str) -> str:
    """Sayısal kolonlar için correlation heatmap çizer."""
    try:
        df = pd.read_csv(csv_file)
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) < 2:
            return "[HATA] En az 2 sayısal kolon gerekli"
        
        plt.figure(figsize=(10,8))
        correlation_matrix = df[numeric_cols].corr()
        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0, 
                   square=True, linewidths=0.5)
        plt.title('Korelasyon Heatmap')
        
        img_path = Path("output") / f"heatmap_{csv_file.split('/')[-1].replace('.csv', '')}.png"
        img_path.parent.mkdir(exist_ok=True)
        plt.savefig(img_path, bbox_inches='tight')
        plt.close()
        return f"[bold green]Heatmap kaydedildi:[/bold green] {img_path}"
    except Exception as e:
        return f"[HATA] Heatmap hatası: {e}"

def clean(csv_file: str) -> str:
    """CSV dosyasını temizler ve özet rapor verir."""
    try:
        df = pd.read_csv(csv_file)
        original_shape = df.shape
        
        # Eksik değerleri say
        missing_counts = df.isnull().sum()
        missing_percent = (missing_counts / len(df)) * 100
        
        # Duplicate satırları say
        duplicates = df.duplicated().sum()
        
        # Temizleme işlemleri
        df_cleaned = df.copy()
        
        # Duplicate satırları kaldır
        df_cleaned = df_cleaned.drop_duplicates()
        
        # Eksik değerleri doldur (sayısal kolonlar için ortalama, kategorik için mod)
        for col in df_cleaned.columns:
            if df_cleaned[col].dtype in ['int64', 'float64']:
                df_cleaned[col].fillna(df_cleaned[col].mean(), inplace=True)
            else:
                df_cleaned[col].fillna(df_cleaned[col].mode()[0] if len(df_cleaned[col].mode()) > 0 else 'Unknown', inplace=True)
        
        # Temizlenmiş dosyayı kaydet
        cleaned_file = csv_file.replace('.csv', '_cleaned.csv')
        df_cleaned.to_csv(cleaned_file, index=False)
        
        report = f"""
[bold]Veri Temizleme Raporu:[/bold]

Orijinal boyut: {original_shape}
Temizlenmiş boyut: {df_cleaned.shape}
Kaldırılan duplicate satır: {duplicates}

[bold]Eksik Değerler:[/bold]
"""
        for col, count, percent in zip(missing_counts.index, missing_counts.values, missing_percent.values):
            if count > 0:
                report += f"{col}: {count} ({percent:.1f}%)\n"
        
        report += f"\n[bold green]Temizlenmiş dosya kaydedildi:[/bold green] {cleaned_file}"
        
        return report
    except Exception as e:
        return f"[HATA] Veri temizleme hatası: {e}"

def help():
    return """
/analyze <csv_dosyası>\n  CSV dosyasını analiz eder ve özetler.\n/describe <csv_dosyası>\n  Temel istatistikleri gösterir.\n/plot <csv_dosyası> <kolon1> <kolon2>\n  İki kolonu çizdirir.\n/histogram <csv_dosyası> <kolon>\n  Histogram çizer.\n/scatter <csv_dosyası> <kolon1> <kolon2>\n  Scatter plot çizer.\n/boxplot <csv_dosyası> <kolon>\n  Box plot çizer.\n/heatmap <csv_dosyası>\n  Korelasyon heatmap çizer.\n/clean <csv_dosyası>\n  Veriyi temizler.\nÖrnek: /analyze data.csv\nÖrnek: /histogram data.csv fiyat\n"""

commands = {
    '/analyze': analyze,
    '/describe': describe,
    '/plot': plot,
    '/histogram': histogram,
    '/scatter': scatter,
    '/boxplot': boxplot,
    '/heatmap': heatmap,
    '/clean': clean
} 