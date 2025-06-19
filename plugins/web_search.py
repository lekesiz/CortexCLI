"""
Web Arama Plugin'i
Web'de arama yapma ve hava durumu bilgisi alma özellikleri
"""

import requests
from plugin_system import PluginBase
from typing import Dict, Callable

class WebSearchPlugin(PluginBase):
    """Web arama plugin'i"""
    
    def __init__(self):
        super().__init__(
            name="web_search",
            version="1.0.0",
            description="Web'de arama yapma özelliği"
        )
        
    def on_load(self) -> bool:
        print(f"🌐 {self.name} plugin'i yüklendi")
        return True
        
    def on_unload(self) -> bool:
        print(f"🌐 {self.name} plugin'i kaldırıldı")
        return True
        
    def get_commands(self) -> Dict[str, Callable]:
        return {
            "search": self.web_search,
            "weather": self.get_weather,
            "news": self.get_news
        }
        
    def web_search(self, query: str) -> str:
        """Web'de arama yapar"""
        try:
            # DuckDuckGo Instant Answer API kullan
            url = "https://api.duckduckgo.com/"
            params = {
                "q": query,
                "format": "json",
                "no_html": "1",
                "skip_disambig": "1"
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if data.get("Abstract"):
                return f"🔍 {query} için sonuç:\n{data['Abstract']}"
            elif data.get("RelatedTopics"):
                return f"🔍 {query} için ilgili konular bulundu"
            else:
                return f"🔍 '{query}' için web arama yapıldı"
                
        except Exception as e:
            return f"❌ Web arama hatası: {e}"
        
    def get_weather(self, city: str) -> str:
        """Hava durumu bilgisi alır"""
        try:
            # OpenWeatherMap API (ücretsiz tier)
            api_key = "demo"  # Gerçek API key gerekli
            url = f"http://api.openweathermap.org/data/2.5/weather"
            params = {
                "q": city,
                "appid": api_key,
                "units": "metric"
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                temp = data["main"]["temp"]
                desc = data["weather"][0]["description"]
                return f"🌤️ {city}: {temp}°C, {desc}"
            else:
                return f"🌤️ {city} için hava durumu bilgisi alınamadı"
                
        except Exception as e:
            return f"❌ Hava durumu hatası: {e}"
            
    def get_news(self, topic: str = "technology") -> str:
        """Haber bilgisi alır"""
        try:
            # NewsAPI kullan (ücretsiz tier)
            api_key = "demo"  # Gerçek API key gerekli
            url = "https://newsapi.org/v2/top-headlines"
            params = {
                "country": "tr",
                "category": topic,
                "apiKey": api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                articles = data.get("articles", [])
                if articles:
                    return f"📰 {topic} kategorisinde {len(articles)} haber bulundu"
                else:
                    return f"📰 {topic} kategorisinde haber bulunamadı"
            else:
                return f"📰 Haber bilgisi alınamadı"
                
        except Exception as e:
            return f"❌ Haber hatası: {e}" 