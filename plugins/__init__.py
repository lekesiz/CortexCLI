"""
CortexCLI Plugin Sistemi
"""

from .web_search import WebSearchPlugin
from .web_weather import WebWeatherPlugin
from .web_wikipedia import WebWikipediaPlugin
from .file_analyzer import FileAnalyzerPlugin
from .file_manager import FileManagerPlugin
from .data_analyzer import DataAnalyzerPlugin
from .calculator import CalculatorPlugin
from .notes import NotesPlugin
from .calendar import CalendarPlugin

__all__ = [
    'WebSearchPlugin',
    'WebWeatherPlugin', 
    'WebWikipediaPlugin',
    'FileAnalyzerPlugin',
    'FileManagerPlugin',
    'DataAnalyzerPlugin',
    'CalculatorPlugin',
    'NotesPlugin',
    'CalendarPlugin'
] 