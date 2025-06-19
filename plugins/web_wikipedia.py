"""
Wikipedia Plugin
Wikipedia'dan bilgi arama ve özetleme
"""

import requests
import json
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class WikipediaResult:
    """Wikipedia sonucu"""
    title: str
    summary: str
    url: str
    page_id: int
    extract: str

class WebWikipediaPlugin:
    """Wikipedia arama plugin'i"""
    
    def __init__(self):
        self.base_url = "https://tr.wikipedia.org/api/rest_v1"
        self.search_url = "https://tr.wikipedia.org/w/api.php"
        
    def search(self, query: str, limit: int = 5) -> List[WikipediaResult]:
        """Wikipedia'da arama yap"""
        try:
            # Önce arama yap
            search_params = {
                'action': 'query',
                'format': 'json',
                'list': 'search',
                'srsearch': query,
                'srlimit': limit,
                'utf8': 1
            }
            
            response = requests.get(self.search_url, params=search_params)
            response.raise_for_status()
            data = response.json()
            
            results = []
            for item in data['query']['search']:
                # Her sonuç için detay al
                detail = self.get_page_detail(item['pageid'])
                if detail:
                    results.append(detail)
                    
            return results
            
        except Exception as e:
            print(f"Wikipedia arama hatası: {e}")
            return []
            
    def get_page_detail(self, page_id: int) -> Optional[WikipediaResult]:
        """Sayfa detaylarını al"""
        try:
            params = {
                'action': 'query',
                'format': 'json',
                'prop': 'extracts|info',
                'pageids': page_id,
                'exintro': 1,
                'explaintext': 1,
                'inprop': 'url'
            }
            
            response = requests.get(self.search_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            page = data['query']['pages'][str(page_id)]
            
            return WikipediaResult(
                title=page['title'],
                summary=page.get('extract', '')[:500] + '...' if len(page.get('extract', '')) > 500 else page.get('extract', ''),
                url=page['fullurl'],
                page_id=page_id,
                extract=page.get('extract', '')
            )
            
        except Exception as e:
            print(f"Sayfa detay hatası: {e}")
            return None
            
    def get_random_article(self) -> Optional[WikipediaResult]:
        """Rastgele makale al"""
        try:
            params = {
                'action': 'query',
                'format': 'json',
                'list': 'random',
                'rnlimit': 1,
                'rnnamespace': 0
            }
            
            response = requests.get(self.search_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data['query']['random']:
                page_id = data['query']['random'][0]['id']
                return self.get_page_detail(page_id)
                
        except Exception as e:
            print(f"Rastgele makale hatası: {e}")
            
        return None
        
    def get_today_featured_article(self) -> Optional[WikipediaResult]:
        """Günün öne çıkan makalesi"""
        try:
            # Günün öne çıkan makalesi için özel endpoint
            response = requests.get(f"{self.base_url}/page/featured/2024/01/01")
            response.raise_for_status()
            data = response.json()
            
            if 'titles' in data:
                title = data['titles']['normalized']
                # Başlıktan sayfa ID'si al
                page_id = self.get_page_id_by_title(title)
                if page_id:
                    return self.get_page_detail(page_id)
                    
        except Exception as e:
            print(f"Günün makalesi hatası: {e}")
            
        return None
        
    def get_page_id_by_title(self, title: str) -> Optional[int]:
        """Başlıktan sayfa ID'si al"""
        try:
            params = {
                'action': 'query',
                'format': 'json',
                'titles': title
            }
            
            response = requests.get(self.search_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            pages = data['query']['pages']
            for page_id in pages:
                if pages[page_id].get('pageid'):
                    return pages[page_id]['pageid']
                    
        except Exception as e:
            print(f"Sayfa ID hatası: {e}")
            
        return None
        
    def get_categories(self, page_id: int) -> List[str]:
        """Sayfanın kategorilerini al"""
        try:
            params = {
                'action': 'query',
                'format': 'json',
                'prop': 'categories',
                'pageids': page_id,
                'cllimit': 10
            }
            
            response = requests.get(self.search_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            categories = []
            page = data['query']['pages'][str(page_id)]
            if 'categories' in page:
                for cat in page['categories']:
                    categories.append(cat['title'].replace('Kategori:', ''))
                    
            return categories
            
        except Exception as e:
            print(f"Kategori hatası: {e}")
            return []
            
    def get_related_pages(self, page_id: int, limit: int = 5) -> List[WikipediaResult]:
        """İlgili sayfaları al"""
        try:
            params = {
                'action': 'query',
                'format': 'json',
                'prop': 'links',
                'pageids': page_id,
                'pllimit': limit,
                'plnamespace': 0
            }
            
            response = requests.get(self.search_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            related = []
            page = data['query']['pages'][str(page_id)]
            if 'links' in page:
                for link in page['links'][:limit]:
                    page_id = self.get_page_id_by_title(link['title'])
                    if page_id:
                        detail = self.get_page_detail(page_id)
                        if detail:
                            related.append(detail)
                            
            return related
            
        except Exception as e:
            print(f"İlgili sayfa hatası: {e}")
            return []

# Plugin bilgileri
PLUGIN_INFO = {
    "name": "Wikipedia",
    "description": "Wikipedia'dan bilgi arama ve özetleme",
    "version": "1.0.0",
    "author": "CortexCLI",
    "commands": {
        "wikipedia": "Wikipedia'da arama yap",
        "wiki": "Wikipedia'da arama yap (kısa)",
        "random-wiki": "Rastgele Wikipedia makalesi",
        "today-wiki": "Günün öne çıkan makalesi"
    }
}

def get_plugin_info():
    """Plugin bilgilerini döndür"""
    return PLUGIN_INFO

def create_plugin():
    """Plugin instance'ı oluştur"""
    return WebWikipediaPlugin() 