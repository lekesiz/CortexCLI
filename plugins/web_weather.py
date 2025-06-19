"""
Web Weather Plugin - Hava durumu sorgulama
Kullanım: /weather <şehir>
"""
import requests
import json
from typing import Dict, Optional, List
from dataclasses import dataclass
from datetime import datetime

@dataclass
class WeatherInfo:
    """Hava durumu bilgisi"""
    city: str
    temperature: str
    condition: str
    humidity: str
    wind: str
    pressure: str
    visibility: str
    uv_index: str
    sunrise: str
    sunset: str
    forecast: List[Dict]

class WebWeatherPlugin:
    """Hava durumu plugin'i"""
    
    def __init__(self):
        self.base_url = "https://wttr.in"
        self.api_key = None  # OpenWeatherMap API key için
        
    def get_weather(self, city: str = "Istanbul", format_type: str = "3") -> str:
        """Basit hava durumu bilgisi"""
        try:
            url = f"{self.base_url}/{city}?format={format_type}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.text
        except Exception as e:
            return f"[HATA] Hava durumu alınamadı: {e}"
    
    def get_detailed_weather(self, city: str = "Istanbul") -> Optional[WeatherInfo]:
        """Detaylı hava durumu bilgisi"""
        try:
            # JSON formatında detaylı bilgi al
            url = f"{self.base_url}/{city}?format=j1"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            current = data['current_condition'][0]
            weather = data['weather'][0]
            
            return WeatherInfo(
                city=city,
                temperature=f"{current['temp_C']}°C",
                condition=current['weatherDesc'][0]['value'],
                humidity=f"{current['humidity']}%",
                wind=f"{current['windspeedKmph']} km/h",
                pressure=f"{current['pressure']} mb",
                visibility=f"{current['visibility']} km",
                uv_index=current['uvIndex'],
                sunrise=weather['astronomy'][0]['sunrise'],
                sunset=weather['astronomy'][0]['sunset'],
                forecast=self._parse_forecast(data['weather'])
            )
            
        except Exception as e:
            print(f"Hava durumu detay hatası: {e}")
            return None
    
    def _parse_forecast(self, weather_data: List[Dict]) -> List[Dict]:
        """Tahmin verilerini işle"""
        forecast = []
        for day in weather_data[:3]:  # 3 günlük tahmin
            forecast.append({
                'date': day['date'],
                'max_temp': f"{day['maxtempC']}°C",
                'min_temp': f"{day['mintempC']}°C",
                'condition': day['hourly'][4]['weatherDesc'][0]['value'],
                'precipitation': f"{day['hourly'][4]['precipMM']}mm"
            })
        return forecast
    
    def get_weather_ascii(self, city: str = "Istanbul") -> str:
        """ASCII art hava durumu"""
        try:
            url = f"{self.base_url}/{city}?format=v2"
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            return response.text
        except Exception as e:
            return f"[HATA] ASCII hava durumu alınamadı: {e}"
    
    def get_weather_forecast(self, city: str = "Istanbul", days: int = 3) -> str:
        """Hava durumu tahmini"""
        try:
            url = f"{self.base_url}/{city}?format=3&days={days}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.text
        except Exception as e:
            return f"[HATA] Tahmin alınamadı: {e}"
    
    def get_moon_phase(self, city: str = "Istanbul") -> str:
        """Ay fazı bilgisi"""
        try:
            url = f"{self.base_url}/{city}?format=j1"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            moon_phase = data['weather'][0]['astronomy'][0]['moon_phase']
            return f"🌙 Ay Fazı: {moon_phase}"
            
        except Exception as e:
            return f"[HATA] Ay fazı alınamadı: {e}"
    
    def get_air_quality(self, city: str = "Istanbul") -> str:
        """Hava kalitesi bilgisi"""
        try:
            # Hava kalitesi için alternatif API
            url = f"http://api.waqi.info/feed/{city}/?token=demo"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data['status'] == 'ok':
                aqi = data['data']['aqi']
                level = self._get_aqi_level(aqi)
                return f"🌬️ Hava Kalitesi: {aqi} ({level})"
            else:
                return "Hava kalitesi bilgisi alınamadı"
                
        except Exception as e:
            return f"[HATA] Hava kalitesi alınamadı: {e}"
    
    def _get_aqi_level(self, aqi: int) -> str:
        """AQI seviyesini belirle"""
        if aqi <= 50:
            return "İyi"
        elif aqi <= 100:
            return "Orta"
        elif aqi <= 150:
            return "Hassas gruplar için sağlıksız"
        elif aqi <= 200:
            return "Sağlıksız"
        elif aqi <= 300:
            return "Çok sağlıksız"
        else:
            return "Tehlikeli"
    
    def get_weather_alerts(self, city: str = "Istanbul") -> str:
        """Hava durumu uyarıları"""
        try:
            url = f"{self.base_url}/{city}?format=j1"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            alerts = []
            if 'weatherAlert' in data:
                for alert in data['weatherAlert']:
                    alerts.append(f"⚠️ {alert['headline']}: {alert['desc']}")
            
            if alerts:
                return "\n".join(alerts)
            else:
                return "Aktif hava durumu uyarısı yok"
                
        except Exception as e:
            return f"[HATA] Uyarılar alınamadı: {e}"
    
    def get_weather_map(self, city: str = "Istanbul") -> str:
        """Hava durumu haritası linki"""
        return f"🌍 Hava Durumu Haritası: https://wttr.in/{city}?format=v2"

def weather(city: str = "Istanbul") -> str:
    """Basit hava durumu komutu"""
    plugin = WebWeatherPlugin()
    return plugin.get_weather(city)

def weather_detailed(city: str = "Istanbul") -> str:
    """Detaylı hava durumu komutu"""
    plugin = WebWeatherPlugin()
    weather_info = plugin.get_detailed_weather(city)
    
    if weather_info:
        result = f"""
🌤️ {weather_info.city} Hava Durumu
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌡️ Sıcaklık: {weather_info.temperature}
☁️ Durum: {weather_info.condition}
💧 Nem: {weather_info.humidity}
💨 Rüzgar: {weather_info.wind}
📊 Basınç: {weather_info.pressure}
👁️ Görüş: {weather_info.visibility}
☀️ UV İndeksi: {weather_info.uv_index}
🌅 Gün Doğumu: {weather_info.sunrise}
🌇 Gün Batımı: {weather_info.sunset}

📅 3 Günlük Tahmin:
"""
        for day in weather_info.forecast:
            result += f"• {day['date']}: {day['min_temp']} - {day['max_temp']}, {day['condition']}\n"
        
        return result
    else:
        return f"[HATA] {city} için hava durumu alınamadı"

def weather_ascii(city: str = "Istanbul") -> str:
    """ASCII art hava durumu"""
    plugin = WebWeatherPlugin()
    return plugin.get_weather_ascii(city)

def weather_forecast(city: str = "Istanbul") -> str:
    """Hava durumu tahmini"""
    plugin = WebWeatherPlugin()
    return plugin.get_weather_forecast(city)

def moon_phase(city: str = "Istanbul") -> str:
    """Ay fazı"""
    plugin = WebWeatherPlugin()
    return plugin.get_moon_phase(city)

def air_quality(city: str = "Istanbul") -> str:
    """Hava kalitesi"""
    plugin = WebWeatherPlugin()
    return plugin.get_air_quality(city)

def weather_alerts(city: str = "Istanbul") -> str:
    """Hava durumu uyarıları"""
    plugin = WebWeatherPlugin()
    return plugin.get_weather_alerts(city)

def help():
    return """
🌤️ Hava Durumu Komutları:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
/weather <şehir>          - Basit hava durumu
/weather-detailed <şehir> - Detaylı hava durumu
/weather-ascii <şehir>    - ASCII art hava durumu
/weather-forecast <şehir> - 3 günlük tahmin
/moon-phase <şehir>       - Ay fazı
/air-quality <şehir>      - Hava kalitesi
/weather-alerts <şehir>   - Hava durumu uyarıları

Örnekler:
/weather Istanbul
/weather-detailed Ankara
/weather-ascii Izmir
"""

# Plugin komutları
commands = {
    '/weather': weather,
    '/weather-detailed': weather_detailed,
    '/weather-ascii': weather_ascii,
    '/weather-forecast': weather_forecast,
    '/moon-phase': moon_phase,
    '/air-quality': air_quality,
    '/weather-alerts': weather_alerts
}

# Plugin bilgileri
PLUGIN_INFO = {
    "name": "Weather",
    "description": "Hava durumu sorgulama ve tahmin",
    "version": "2.0.0",
    "author": "CortexCLI",
    "commands": commands
}

def get_plugin_info():
    """Plugin bilgilerini döndür"""
    return PLUGIN_INFO

def create_plugin():
    """Plugin instance'ı oluştur"""
    return WebWeatherPlugin() 