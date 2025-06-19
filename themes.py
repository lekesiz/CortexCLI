"""
Theme system for CortexCLI
Supports both CLI and web UI themes with customizable color schemes and styling
"""

import json
import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from pathlib import Path
import colorama
from colorama import Fore, Back, Style

# Initialize colorama for cross-platform color support
colorama.init()

@dataclass
class CLIColors:
    """CLI color scheme configuration"""
    primary: str = Fore.CYAN
    secondary: str = Fore.YELLOW
    success: str = Fore.GREEN
    error: str = Fore.RED
    warning: str = Fore.MAGENTA
    info: str = Fore.BLUE
    muted: str = Fore.WHITE
    reset: str = Style.RESET_ALL
    bold: str = Style.BRIGHT
    dim: str = Style.DIM

@dataclass
class WebColors:
    """Web UI color scheme configuration"""
    primary: str = "#007bff"
    secondary: str = "#6c757d"
    success: str = "#28a745"
    error: str = "#dc3545"
    warning: str = "#ffc107"
    info: str = "#17a2b8"
    light: str = "#f8f9fa"
    dark: str = "#343a40"
    background: str = "#ffffff"
    text: str = "#212529"
    border: str = "#dee2e6"

@dataclass
class Theme:
    """Complete theme configuration"""
    name: str
    description: str
    cli_colors: CLIColors
    web_colors: WebColors
    font_family: str = "monospace"
    font_size: str = "14px"
    border_radius: str = "4px"
    animation_speed: str = "0.2s"

class ThemeManager:
    """Manages theme loading, saving, and application"""
    
    def __init__(self, themes_dir: str = "themes"):
        self.themes_dir = Path(themes_dir)
        self.themes_dir.mkdir(exist_ok=True)
        self.current_theme = "default"
        self.themes: Dict[str, Theme] = {}
        self._load_builtin_themes()
        self._load_custom_themes()
    
    def _load_builtin_themes(self):
        """Load built-in themes"""
        builtin_themes = {
            "default": Theme(
                name="Default",
                description="Clean and professional default theme",
                cli_colors=CLIColors(),
                web_colors=WebColors()
            ),
            "dark": Theme(
                name="Dark",
                description="Dark theme for low-light environments",
                cli_colors=CLIColors(
                    primary=Fore.CYAN,
                    secondary=Fore.YELLOW,
                    success=Fore.GREEN,
                    error=Fore.RED,
                    warning=Fore.MAGENTA,
                    info=Fore.BLUE,
                    muted=Fore.WHITE
                ),
                web_colors=WebColors(
                    primary="#00d4ff",
                    secondary="#6c757d",
                    success="#00ff88",
                    error="#ff4757",
                    warning="#ffa502",
                    info="#3742fa",
                    light="#2f3542",
                    dark="#ffffff",
                    background="#1e272e",
                    text="#ffffff",
                    border="#535c68"
                ),
                font_family="'Courier New', monospace"
            ),
            "ocean": Theme(
                name="Ocean",
                description="Ocean-inspired blue theme",
                cli_colors=CLIColors(
                    primary=Fore.BLUE,
                    secondary=Fore.CYAN,
                    success=Fore.GREEN,
                    error=Fore.RED,
                    warning=Fore.YELLOW,
                    info=Fore.MAGENTA,
                    muted=Fore.WHITE
                ),
                web_colors=WebColors(
                    primary="#006994",
                    secondary="#4a90e2",
                    success="#00b894",
                    error="#e17055",
                    warning="#fdcb6e",
                    info="#74b9ff",
                    light="#f5f6fa",
                    dark="#2d3436",
                    background="#ffffff",
                    text="#2d3436",
                    border="#ddd"
                )
            ),
            "sunset": Theme(
                name="Sunset",
                description="Warm sunset-inspired theme",
                cli_colors=CLIColors(
                    primary=Fore.MAGENTA,
                    secondary=Fore.YELLOW,
                    success=Fore.GREEN,
                    error=Fore.RED,
                    warning=Fore.CYAN,
                    info=Fore.BLUE,
                    muted=Fore.WHITE
                ),
                web_colors=WebColors(
                    primary="#e17055",
                    secondary="#fdcb6e",
                    success="#00b894",
                    error="#d63031",
                    warning="#fdcb6e",
                    info="#74b9ff",
                    light="#fff8f0",
                    dark="#2d3436",
                    background="#fff8f0",
                    text="#2d3436",
                    border="#ffeaa7"
                )
            ),
            "matrix": Theme(
                name="Matrix",
                description="Matrix-inspired green theme",
                cli_colors=CLIColors(
                    primary=Fore.GREEN,
                    secondary=Fore.GREEN,
                    success=Fore.GREEN,
                    error=Fore.RED,
                    warning=Fore.YELLOW,
                    info=Fore.CYAN,
                    muted=Fore.GREEN
                ),
                web_colors=WebColors(
                    primary="#00ff41",
                    secondary="#00ff88",
                    success="#00ff41",
                    error="#ff0040",
                    warning="#ffff00",
                    info="#00ffff",
                    light="#0a0a0a",
                    dark="#00ff41",
                    background="#000000",
                    text="#00ff41",
                    border="#00ff41"
                ),
                font_family="'Courier New', monospace"
            )
        }
        
        for theme_id, theme in builtin_themes.items():
            self.themes[theme_id] = theme
    
    def _load_custom_themes(self):
        """Load custom themes from themes directory"""
        for theme_file in self.themes_dir.glob("*.json"):
            try:
                with open(theme_file, 'r', encoding='utf-8') as f:
                    theme_data = json.load(f)
                    theme = self._dict_to_theme(theme_data)
                    self.themes[theme.name.lower().replace(' ', '_')] = theme
            except Exception as e:
                print(f"Error loading theme {theme_file}: {e}")
    
    def _dict_to_theme(self, data: Dict[str, Any]) -> Theme:
        """Convert dictionary to Theme object"""
        cli_colors = CLIColors(**data.get('cli_colors', {}))
        web_colors = WebColors(**data.get('web_colors', {}))
        
        return Theme(
            name=data['name'],
            description=data.get('description', ''),
            cli_colors=cli_colors,
            web_colors=web_colors,
            font_family=data.get('font_family', 'monospace'),
            font_size=data.get('font_size', '14px'),
            border_radius=data.get('border_radius', '4px'),
            animation_speed=data.get('animation_speed', '0.2s')
        )
    
    def _theme_to_dict(self, theme: Theme) -> Dict[str, Any]:
        """Convert Theme object to dictionary"""
        return {
            'name': theme.name,
            'description': theme.description,
            'cli_colors': asdict(theme.cli_colors),
            'web_colors': asdict(theme.web_colors),
            'font_family': theme.font_family,
            'font_size': theme.font_size,
            'border_radius': theme.border_radius,
            'animation_speed': theme.animation_speed
        }
    
    def get_theme(self, theme_name: str) -> Optional[Theme]:
        """Get theme by name"""
        return self.themes.get(theme_name.lower().replace(' ', '_'))
    
    def get_current_theme(self) -> Theme:
        """Get currently active theme"""
        return self.themes.get(self.current_theme, self.themes['default'])
    
    def set_theme(self, theme_name: str) -> bool:
        """Set active theme"""
        theme_id = theme_name.lower().replace(' ', '_')
        if theme_id in self.themes:
            self.current_theme = theme_id
            return True
        return False
    
    def list_themes(self) -> List[Dict[str, str]]:
        """List all available themes"""
        themes_list = []
        for theme_id, theme in self.themes.items():
            themes_list.append({
                'id': theme_id,
                'name': theme.name,
                'description': theme.description,
                'current': theme_id == self.current_theme
            })
        return themes_list
    
    def create_theme(self, name: str, description: str, **kwargs) -> bool:
        """Create a new custom theme"""
        try:
            cli_colors = CLIColors(**kwargs.get('cli_colors', {}))
            web_colors = WebColors(**kwargs.get('web_colors', {}))
            
            theme = Theme(
                name=name,
                description=description,
                cli_colors=cli_colors,
                web_colors=web_colors,
                font_family=kwargs.get('font_family', 'monospace'),
                font_size=kwargs.get('font_size', '14px'),
                border_radius=kwargs.get('border_radius', '4px'),
                animation_speed=kwargs.get('animation_speed', '0.2s')
            )
            
            theme_id = name.lower().replace(' ', '_')
            self.themes[theme_id] = theme
            
            # Save to file
            theme_file = self.themes_dir / f"{theme_id}.json"
            with open(theme_file, 'w', encoding='utf-8') as f:
                json.dump(self._theme_to_dict(theme), f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error creating theme: {e}")
            return False
    
    def delete_theme(self, theme_name: str) -> bool:
        """Delete a custom theme"""
        theme_id = theme_name.lower().replace(' ', '_')
        
        # Don't allow deleting built-in themes
        builtin_themes = ['default', 'dark', 'ocean', 'sunset', 'matrix']
        if theme_id in builtin_themes:
            return False
        
        if theme_id in self.themes:
            del self.themes[theme_id]
            
            # Delete file
            theme_file = self.themes_dir / f"{theme_id}.json"
            if theme_file.exists():
                theme_file.unlink()
            
            # If deleted theme was current, switch to default
            if self.current_theme == theme_id:
                self.current_theme = 'default'
            
            return True
        return False
    
    def export_theme(self, theme_name: str, filepath: str) -> bool:
        """Export theme to file"""
        theme = self.get_theme(theme_name)
        if not theme:
            return False
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self._theme_to_dict(theme), f, indent=2)
            return True
        except Exception as e:
            print(f"Error exporting theme: {e}")
            return False
    
    def import_theme(self, filepath: str) -> bool:
        """Import theme from file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                theme_data = json.load(f)
            
            theme = self._dict_to_theme(theme_data)
            theme_id = theme.name.lower().replace(' ', '_')
            self.themes[theme_id] = theme
            
            # Save to themes directory
            theme_file = self.themes_dir / f"{theme_id}.json"
            with open(theme_file, 'w', encoding='utf-8') as f:
                json.dump(theme_data, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error importing theme: {e}")
            return False
    
    def get_cli_colors(self) -> CLIColors:
        """Get current CLI colors"""
        return self.get_current_theme().cli_colors
    
    def get_web_colors(self) -> WebColors:
        """Get current web colors"""
        return self.get_current_theme().web_colors
    
    def generate_css(self) -> str:
        """Generate CSS for web UI based on current theme"""
        theme = self.get_current_theme()
        colors = theme.web_colors
        
        css = f"""
        :root {{
            --primary-color: {colors.primary};
            --secondary-color: {colors.secondary};
            --success-color: {colors.success};
            --error-color: {colors.error};
            --warning-color: {colors.warning};
            --info-color: {colors.info};
            --light-color: {colors.light};
            --dark-color: {colors.dark};
            --background-color: {colors.background};
            --text-color: {colors.text};
            --border-color: {colors.border};
            --font-family: {theme.font_family};
            --font-size: {theme.font_size};
            --border-radius: {theme.border_radius};
            --animation-speed: {theme.animation_speed};
        }}
        
        body {{
            background-color: var(--background-color);
            color: var(--text-color);
            font-family: var(--font-family);
            font-size: var(--font-size);
        }}
        
        .btn-primary {{
            background-color: var(--primary-color);
            border-color: var(--primary-color);
        }}
        
        .btn-secondary {{
            background-color: var(--secondary-color);
            border-color: var(--secondary-color);
        }}
        
        .btn-success {{
            background-color: var(--success-color);
            border-color: var(--success-color);
        }}
        
        .btn-danger {{
            background-color: var(--error-color);
            border-color: var(--error-color);
        }}
        
        .btn-warning {{
            background-color: var(--warning-color);
            border-color: var(--warning-color);
        }}
        
        .btn-info {{
            background-color: var(--info-color);
            border-color: var(--info-color);
        }}
        
        .card {{
            border-radius: var(--border-radius);
            border: 1px solid var(--border-color);
            transition: all var(--animation-speed) ease;
        }}
        
        .form-control {{
            border-radius: var(--border-radius);
            border: 1px solid var(--border-color);
        }}
        
        .navbar {{
            background-color: var(--primary-color) !important;
        }}
        
        .sidebar {{
            background-color: var(--light-color);
            border-right: 1px solid var(--border-color);
        }}
        
        .chat-message {{
            border-radius: var(--border-radius);
            margin-bottom: 10px;
            padding: 10px;
        }}
        
        .chat-message.user {{
            background-color: var(--primary-color);
            color: white;
        }}
        
        .chat-message.assistant {{
            background-color: var(--light-color);
            border: 1px solid var(--border-color);
        }}
        """
        
        return css

# Global theme manager instance
theme_manager = ThemeManager()

def apply_cli_theme():
    """Apply current theme colors to CLI"""
    colors = theme_manager.get_cli_colors()
    return colors

def print_themed(text: str, color_type: str = "primary", bold: bool = False, dim: bool = False):
    """Print text with current theme colors"""
    colors = theme_manager.get_cli_colors()
    
    color_map = {
        "primary": colors.primary,
        "secondary": colors.secondary,
        "success": colors.success,
        "error": colors.error,
        "warning": colors.warning,
        "info": colors.info,
        "muted": colors.muted
    }
    
    color = color_map.get(color_type, colors.primary)
    style = ""
    
    if bold:
        style += colors.bold
    if dim:
        style += colors.dim
    
    print(f"{style}{color}{text}{colors.reset}")

def get_theme_css():
    """Get CSS for web UI"""
    return theme_manager.generate_css() 