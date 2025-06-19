"""
Calculator Plugin - Matematik hesaplamaları ve birim dönüşümleri
Kullanım:
  /calc <ifade>
  /convert <miktar> <birim> to <hedef_birim>
  /solve <denklem>
  /units
"""
import math
import re
from typing import Dict, Any

# Birim dönüşüm tabloları
LENGTH_UNITS = {
    'm': 1.0, 'meter': 1.0, 'metre': 1.0,
    'km': 1000.0, 'kilometer': 1000.0, 'kilometre': 1000.0,
    'cm': 0.01, 'centimeter': 0.01, 'santimetre': 0.01,
    'mm': 0.001, 'millimeter': 0.001, 'milimetre': 0.001,
    'mi': 1609.344, 'mile': 1609.344, 'mil': 1609.344,
    'yd': 0.9144, 'yard': 0.9144,
    'ft': 0.3048, 'foot': 0.3048, 'feet': 0.3048,
    'in': 0.0254, 'inch': 0.0254, 'inç': 0.0254
}

WEIGHT_UNITS = {
    'kg': 1.0, 'kilogram': 1.0,
    'g': 0.001, 'gram': 0.001,
    'mg': 0.000001, 'milligram': 0.000001,
    'lb': 0.453592, 'pound': 0.453592,
    'oz': 0.0283495, 'ounce': 0.0283495
}

TEMPERATURE_UNITS = {
    'c': 'celsius', 'celsius': 'celsius',
    'f': 'fahrenheit', 'fahrenheit': 'fahrenheit',
    'k': 'kelvin', 'kelvin': 'kelvin'
}

def calc(expression: str) -> str:
    """Matematik ifadesini hesaplar."""
    try:
        # Güvenli matematik ifadeleri için
        allowed_chars = set('0123456789+-*/()., ')
        if not all(c in allowed_chars for c in expression):
            return "[HATA] Sadece temel matematik işlemleri desteklenir"
        
        # Virgülü nokta ile değiştir
        expression = expression.replace(',', '.')
        
        # Güvenli eval için sadece matematik modüllerini kullan
        safe_dict = {
            '__builtins__': {},
            'abs': abs, 'round': round, 'min': min, 'max': max,
            'pow': pow, 'sum': sum
        }
        
        result = eval(expression, safe_dict)
        return f"[bold green]Sonuç:[/bold green] {result}"
    except Exception as e:
        return f"[HATA] Hesaplama hatası: {e}"

def convert(value: str, from_unit: str, to_unit: str) -> str:
    """Birim dönüşümü yapar."""
    try:
        val = float(value)
        from_unit = from_unit.lower()
        to_unit = to_unit.lower()
        
        # Uzunluk dönüşümü
        if from_unit in LENGTH_UNITS and to_unit in LENGTH_UNITS:
            meters = val * LENGTH_UNITS[from_unit]
            result = meters / LENGTH_UNITS[to_unit]
            return f"[bold green]Sonuç:[/bold green] {val} {from_unit} = {result:.4f} {to_unit}"
        
        # Ağırlık dönüşümü
        elif from_unit in WEIGHT_UNITS and to_unit in WEIGHT_UNITS:
            kg = val * WEIGHT_UNITS[from_unit]
            result = kg / WEIGHT_UNITS[to_unit]
            return f"[bold green]Sonuç:[/bold green] {val} {from_unit} = {result:.4f} {to_unit}"
        
        # Sıcaklık dönüşümü
        elif from_unit in TEMPERATURE_UNITS and to_unit in TEMPERATURE_UNITS:
            result = convert_temperature(val, TEMPERATURE_UNITS[from_unit], TEMPERATURE_UNITS[to_unit])
            return f"[bold green]Sonuç:[/bold green] {val} {from_unit} = {result:.2f} {to_unit}"
        
        else:
            return "[HATA] Desteklenmeyen birim dönüşümü"
            
    except Exception as e:
        return f"[HATA] Dönüşüm hatası: {e}"

def convert_temperature(value: float, from_type: str, to_type: str) -> float:
    """Sıcaklık dönüşümü."""
    # Önce Celsius'a çevir
    if from_type == 'fahrenheit':
        celsius = (value - 32) * 5/9
    elif from_type == 'kelvin':
        celsius = value - 273.15
    else:
        celsius = value
    
    # Celsius'tan hedef birime çevir
    if to_type == 'fahrenheit':
        return celsius * 9/5 + 32
    elif to_type == 'kelvin':
        return celsius + 273.15
    else:
        return celsius

def solve(equation: str) -> str:
    """Basit denklemleri çözer."""
    try:
        # x + 5 = 10 formatındaki denklemler
        if '=' in equation:
            left, right = equation.split('=')
            left = left.strip()
            right = right.strip()
            
            # x'i bul
            if 'x' in left:
                # x + 5 = 10 -> x = 10 - 5
                expr = left.replace('x', '0')
                try:
                    left_val = eval(expr)
                    right_val = eval(right)
                    x_val = right_val - left_val
                    return f"[bold green]x = {x_val}[/bold green]"
                except:
                    pass
            
            elif 'x' in right:
                # 5 = x + 10 -> x = 5 - 10
                expr = right.replace('x', '0')
                try:
                    right_val = eval(expr)
                    left_val = eval(left)
                    x_val = left_val - right_val
                    return f"[bold green]x = {x_val}[/bold green]"
                except:
                    pass
        
        return "[HATA] Desteklenmeyen denklem formatı"
        
    except Exception as e:
        return f"[HATA] Denklem çözme hatası: {e}"

def units() -> str:
    """Desteklenen birimleri listeler."""
    return """
[bold]Desteklenen Birimler:[/bold]

[bold]Uzunluk:[/bold]
- m, km, cm, mm, mi, yd, ft, in
- metre, kilometre, santimetre, milimetre, mil, yard, foot, inch

[bold]Ağırlık:[/bold]
- kg, g, mg, lb, oz
- kilogram, gram, milligram, pound, ounce

[bold]Sıcaklık:[/bold]
- c, f, k
- celsius, fahrenheit, kelvin

[bold]Örnekler:[/bold]
/convert 100 km to mi
/convert 25 c to f
/convert 1 kg to lb
"""

def help():
    return """
/calc <ifade>\n  Matematik ifadesini hesaplar.\n/convert <miktar> <birim> to <hedef_birim>\n  Birim dönüşümü yapar.\n/solve <denklem>\n  Basit denklemleri çözer.\n/units\n  Desteklenen birimleri listeler.\nÖrnek: /calc 2+3*4\nÖrnek: /convert 100 km to mi\nÖrnek: /solve x+5=10\n"""

commands = {
    '/calc': calc,
    '/convert': convert,
    '/solve': solve,
    '/units': units
} 