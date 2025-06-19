"""
CortexCLI Çoklu Model Desteği
Aynı anda birden fazla modelle sohbet ve karşılaştırma özellikleri
"""

import asyncio
import threading
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import json
from rich.table import Table
from rich.panel import Panel
from rich.console import Console

console = Console()

@dataclass
class ModelResponse:
    """Model yanıtı için veri yapısı"""
    model_name: str
    response: str
    response_time: float
    token_count: Optional[int] = None
    error: Optional[str] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

class MultiModelManager:
    """Çoklu model yöneticisi"""
    
    def __init__(self):
        self.active_models: Dict[str, str] = {}  # model_alias -> model_name
        self.model_responses: Dict[str, List[ModelResponse]] = {}
        self.comparison_mode = False
        self.performance_metrics: Dict[str, Dict[str, float]] = {}
        
    def add_model(self, alias: str, model_name: str) -> bool:
        """Yeni model ekle"""
        try:
            # Model'in mevcut olup olmadığını kontrol et
            from llm_shell import get_available_models
            available_models = get_available_models()
            
            if model_name not in available_models:
                console.print(f"[red]❌ Model bulunamadı: {model_name}[/red]")
                return False
                
            self.active_models[alias] = model_name
            self.model_responses[alias] = []
            console.print(f"[green]✅ Model eklendi: {alias} -> {model_name}[/green]")
            return True
            
        except Exception as e:
            console.print(f"[red]❌ Model ekleme hatası: {e}[/red]")
            return False
            
    def remove_model(self, alias: str) -> bool:
        """Model kaldır"""
        if alias in self.active_models:
            del self.active_models[alias]
            if alias in self.model_responses:
                del self.model_responses[alias]
            console.print(f"[green]✅ Model kaldırıldı: {alias}[/green]")
            return True
        return False
        
    def list_models(self) -> Dict[str, str]:
        """Aktif modelleri listele"""
        return self.active_models.copy()
        
    def query_single_model(self, alias: str, prompt: str, system_prompt: str = None) -> ModelResponse:
        """Tek modelle sorgu yap"""
        if alias not in self.active_models:
            return ModelResponse(
                model_name=alias,
                response="",
                response_time=0,
                error=f"Model bulunamadı: {alias}"
            )
            
        model_name = self.active_models[alias]
        start_time = time.time()
        
        try:
            from llm_shell import query_ollama
            response = query_ollama(prompt, model_name, system_prompt)
            response_time = time.time() - start_time
            
            # Token sayısını tahmin et (yaklaşık)
            token_count = len(response.split()) * 1.3  # Yaklaşık hesaplama
            
            model_response = ModelResponse(
                model_name=model_name,
                response=response,
                response_time=response_time,
                token_count=int(token_count)
            )
            
            # Yanıtı kaydet
            self.model_responses[alias].append(model_response)
            
            # Performans metriklerini güncelle
            self._update_performance_metrics(alias, response_time, token_count)
            
            return model_response
            
        except Exception as e:
            response_time = time.time() - start_time
            return ModelResponse(
                model_name=model_name,
                response="",
                response_time=response_time,
                error=str(e)
            )
            
    def query_all_models(self, prompt: str, system_prompt: str = None) -> Dict[str, ModelResponse]:
        """Tüm aktif modellerle paralel sorgu yap"""
        results = {}
        threads = []
        
        def query_model(alias):
            results[alias] = self.query_single_model(alias, prompt, system_prompt)
            
        # Her model için ayrı thread başlat
        for alias in self.active_models:
            thread = threading.Thread(target=query_model, args=(alias,))
            threads.append(thread)
            thread.start()
            
        # Tüm thread'lerin bitmesini bekle
        for thread in threads:
            thread.join()
            
        return results
        
    def compare_models(self, prompt: str, system_prompt: str = None) -> None:
        """Model karşılaştırması yap"""
        if len(self.active_models) < 2:
            console.print("[red]❌ Karşılaştırma için en az 2 model gerekli[/red]")
            return
            
        console.print(f"[yellow]🔄 {len(self.active_models)} model ile karşılaştırma yapılıyor...[/yellow]")
        
        results = self.query_all_models(prompt, system_prompt)
        
        # Sonuçları tablo halinde göster
        table = Table(title="🤖 Model Karşılaştırması")
        table.add_column("Model", style="cyan")
        table.add_column("Yanıt Süresi", style="green")
        table.add_column("Token Sayısı", style="magenta")
        table.add_column("Durum", style="yellow")
        
        for alias, result in results.items():
            if result.error:
                status = f"❌ {result.error}"
            else:
                status = "✅ Başarılı"
                
            table.add_row(
                f"{alias} ({result.model_name})",
                f"{result.response_time:.2f}s",
                str(result.token_count or "N/A"),
                status
            )
            
        console.print(table)
        
        # Yanıtları göster
        for alias, result in results.items():
            if not result.error:
                console.print(Panel(
                    result.response,
                    title=f"🤖 {alias} ({result.model_name})",
                    border_style="blue"
                ))
                
    def show_performance_metrics(self) -> None:
        """Performans metriklerini göster"""
        if not self.performance_metrics:
            console.print("[dim]Henüz performans verisi yok[/dim]")
            return
            
        table = Table(title="📊 Model Performans Metrikleri")
        table.add_column("Model", style="cyan")
        table.add_column("Ortalama Süre", style="green")
        table.add_column("Ortalama Token", style="magenta")
        table.add_column("Toplam Sorgu", style="yellow")
        
        for alias, metrics in self.performance_metrics.items():
            avg_time = metrics.get('avg_response_time', 0)
            avg_tokens = metrics.get('avg_token_count', 0)
            total_queries = metrics.get('total_queries', 0)
            
            table.add_row(
                alias,
                f"{avg_time:.2f}s",
                f"{avg_tokens:.0f}",
                str(total_queries)
            )
            
        console.print(table)
        
    def _update_performance_metrics(self, alias: str, response_time: float, token_count: int) -> None:
        """Performans metriklerini güncelle"""
        if alias not in self.performance_metrics:
            self.performance_metrics[alias] = {
                'total_response_time': 0,
                'total_token_count': 0,
                'total_queries': 0,
                'avg_response_time': 0,
                'avg_token_count': 0
            }
            
        metrics = self.performance_metrics[alias]
        metrics['total_response_time'] += response_time
        metrics['total_token_count'] += token_count
        metrics['total_queries'] += 1
        
        # Ortalamaları hesapla
        metrics['avg_response_time'] = metrics['total_response_time'] / metrics['total_queries']
        metrics['avg_token_count'] = metrics['total_token_count'] / metrics['total_queries']
        
    def save_comparison(self, filename: str = None) -> None:
        """Karşılaştırma sonuçlarını kaydet"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"model_comparison_{timestamp}.json"
            
        data = {
            'timestamp': datetime.now().isoformat(),
            'active_models': self.active_models,
            'performance_metrics': self.performance_metrics,
            'recent_responses': {}
        }
        
        # Son yanıtları kaydet
        for alias, responses in self.model_responses.items():
            if responses:
                last_response = responses[-1]
                data['recent_responses'][alias] = {
                    'model_name': last_response.model_name,
                    'response': last_response.response,
                    'response_time': last_response.response_time,
                    'token_count': last_response.token_count,
                    'timestamp': last_response.timestamp.isoformat()
                }
                
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            console.print(f"[green]✅ Karşılaştırma kaydedildi: {filename}[/green]")
        except Exception as e:
            console.print(f"[red]❌ Kaydetme hatası: {e}[/red]")
            
    def clear_history(self) -> None:
        """Model geçmişini temizle"""
        for alias in self.model_responses:
            self.model_responses[alias].clear()
        self.performance_metrics.clear()
        console.print("[green]✅ Model geçmişi temizlendi[/green]")

# Global multi-model manager
multi_model_manager = MultiModelManager() 