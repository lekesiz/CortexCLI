"""
CortexCLI Gelişmiş Kod Çalıştırma Sistemi
Güvenli, sandboxed kod çalıştırma ve debug özellikleri
"""

import os
import sys
import subprocess
import tempfile
import shutil
import time
import signal
import threading
import json
import ast
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import docker
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

@dataclass
class CodeExecutionResult:
    """Kod çalıştırma sonucu"""
    success: bool
    output: str
    error: str
    execution_time: float
    memory_usage: Optional[float] = None
    cpu_usage: Optional[float] = None
    exit_code: int = 0
    language: str = "python"
    file_path: Optional[str] = None

class CodeAnalyzer:
    """Kod analizi ve güvenlik kontrolü"""
    
    def __init__(self):
        self.dangerous_modules = {
            'os', 'subprocess', 'sys', 'shutil', 'glob', 'pathlib',
            'tempfile', 'pickle', 'marshal', 'ctypes', 'socket',
            'urllib', 'requests', 'ftplib', 'smtplib'
        }
        
        self.dangerous_functions = {
            'eval', 'exec', 'compile', 'input', 'open',
            'file', 'raw_input', '__import__'
        }
        
    def analyze_code(self, code: str, language: str = "python") -> Dict[str, Any]:
        """Kodu analiz et ve güvenlik risklerini tespit et"""
        analysis = {
            'language': language,
            'lines': len(code.split('\n')),
            'characters': len(code),
            'words': len(code.split()),
            'security_risks': [],
            'imports': [],
            'functions': [],
            'complexity': 'low'
        }
        
        if language.lower() == "python":
            analysis.update(self._analyze_python_code(code))
        elif language.lower() == "javascript":
            analysis.update(self._analyze_javascript_code(code))
        elif language.lower() == "bash":
            analysis.update(self._analyze_bash_code(code))
            
        return analysis
        
    def _analyze_python_code(self, code: str) -> Dict[str, Any]:
        """Python kodunu analiz et"""
        analysis = {}
        
        try:
            tree = ast.parse(code)
            
            # Import'ları bul
            imports = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for alias in node.names:
                        imports.append(f"{module}.{alias.name}")
                        
            analysis['imports'] = imports
            
            # Güvenlik risklerini kontrol et
            security_risks = []
            for imp in imports:
                if imp in self.dangerous_modules:
                    security_risks.append(f"Dangerous import: {imp}")
                    
            # Fonksiyon çağrılarını bul
            functions = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        functions.append(node.func.id)
                        
            analysis['functions'] = functions
            
            # Tehlikeli fonksiyonları kontrol et
            for func in functions:
                if func in self.dangerous_functions:
                    security_risks.append(f"Dangerous function: {func}")
                    
            analysis['security_risks'] = security_risks
            
            # Karmaşıklık hesapla
            complexity = len(functions) + len(imports)
            if complexity > 20:
                analysis['complexity'] = 'high'
            elif complexity > 10:
                analysis['complexity'] = 'medium'
            else:
                analysis['complexity'] = 'low'
                
        except SyntaxError as e:
            analysis['syntax_error'] = str(e)
            
        return analysis
        
    def _analyze_javascript_code(self, code: str) -> Dict[str, Any]:
        """JavaScript kodunu analiz et"""
        analysis = {}
        
        # Basit regex tabanlı analiz
        dangerous_patterns = [
            r'eval\s*\(',
            r'Function\s*\(',
            r'setTimeout\s*\(',
            r'setInterval\s*\(',
            r'fetch\s*\(',
            r'XMLHttpRequest',
            r'localStorage',
            r'sessionStorage'
        ]
        
        security_risks = []
        for pattern in dangerous_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                security_risks.append(f"Dangerous pattern: {pattern}")
                
        analysis['security_risks'] = security_risks
        return analysis
        
    def _analyze_bash_code(self, code: str) -> Dict[str, Any]:
        """Bash kodunu analiz et"""
        analysis = {}
        
        dangerous_commands = [
            'rm -rf', 'dd', 'mkfs', 'fdisk', 'chmod 777',
            'sudo', 'su', 'passwd', 'useradd', 'userdel'
        ]
        
        security_risks = []
        for cmd in dangerous_commands:
            if cmd in code:
                security_risks.append(f"Dangerous command: {cmd}")
                
        analysis['security_risks'] = security_risks
        return analysis

class SandboxedExecutor:
    """Güvenli, sandboxed kod çalıştırma"""
    
    def __init__(self, use_docker: bool = True):
        self.use_docker = use_docker
        self.docker_client = None
        self.analyzer = CodeAnalyzer()
        
        if use_docker:
            try:
                self.docker_client = docker.from_env()
                console.print("[green]✅ Docker sandbox hazır[/green]")
            except Exception as e:
                console.print(f"[yellow]⚠️ Docker bulunamadı, yerel çalıştırma kullanılacak: {e}[/yellow]")
                self.use_docker = False
                
    def execute_code(self, code: str, language: str = "python", timeout: int = 30) -> CodeExecutionResult:
        """Kodu güvenli bir şekilde çalıştır"""
        start_time = time.time()
        
        # Kod analizi
        analysis = self.analyzer.analyze_code(code, language)
        
        # Güvenlik risklerini göster
        if analysis.get('security_risks'):
            console.print("[yellow]⚠️ Güvenlik riskleri tespit edildi:[/yellow]")
            for risk in analysis['security_risks']:
                console.print(f"  • {risk}")
                
            if not console.input("[yellow]Devam etmek istiyor musunuz? (y/N): [/yellow]").lower().startswith('y'):
                return CodeExecutionResult(
                    success=False,
                    output="",
                    error="Kullanıcı tarafından iptal edildi",
                    execution_time=time.time() - start_time,
                    language=language
                )
        
        # Çalıştırma yöntemini seç
        if self.use_docker and language == "python":
            return self._execute_in_docker(code, timeout)
        else:
            return self._execute_locally(code, language, timeout)
            
    def _execute_in_docker(self, code: str, timeout: int) -> CodeExecutionResult:
        """Docker container'da çalıştır"""
        try:
            # Geçici dosya oluştur
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_file = f.name
                
            # Docker container oluştur ve çalıştır
            container = self.docker_client.containers.run(
                'python:3.9-slim',
                command=f'python /tmp/code.py',
                volumes={temp_file: {'bind': '/tmp/code.py', 'mode': 'ro'}},
                detach=True,
                mem_limit='100m',
                cpu_period=100000,
                cpu_quota=25000,  # %25 CPU limit
                network_disabled=True,
                read_only=True
            )
            
            try:
                # Container'ın bitmesini bekle
                container.wait(timeout=timeout)
                
                # Çıktıları al
                logs = container.logs().decode('utf-8')
                exit_code = container.attrs['State']['ExitCode']
                
                success = exit_code == 0
                error = "" if success else f"Exit code: {exit_code}"
                
            finally:
                # Container'ı temizle
                container.remove(force=True)
                os.unlink(temp_file)
                
            return CodeExecutionResult(
                success=success,
                output=logs,
                error=error,
                execution_time=time.time(),
                language="python",
                exit_code=exit_code
            )
            
        except Exception as e:
            return CodeExecutionResult(
                success=False,
                output="",
                error=f"Docker execution error: {e}",
                execution_time=time.time(),
                language="python"
            )
            
    def _execute_locally(self, code: str, language: str, timeout: int) -> CodeExecutionResult:
        """Yerel olarak çalıştır"""
        try:
            if language.lower() == "python":
                # Geçici dosya oluştur
                with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                    f.write(code)
                    temp_file = f.name
                    
                # Kodu çalıştır
                result = subprocess.run(
                    [sys.executable, temp_file],
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    cwd=tempfile.gettempdir()
                )
                
                # Geçici dosyayı sil
                os.unlink(temp_file)
                
            elif language.lower() == "bash":
                result = subprocess.run(
                    code,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=timeout
                )
                
            else:
                return CodeExecutionResult(
                    success=False,
                    output="",
                    error=f"Unsupported language: {language}",
                    execution_time=time.time(),
                    language=language
                )
                
            return CodeExecutionResult(
                success=result.returncode == 0,
                output=result.stdout,
                error=result.stderr,
                execution_time=time.time(),
                language=language,
                exit_code=result.returncode
            )
            
        except subprocess.TimeoutExpired:
            return CodeExecutionResult(
                success=False,
                output="",
                error=f"Execution timeout ({timeout}s)",
                execution_time=timeout,
                language=language
            )
        except Exception as e:
            return CodeExecutionResult(
                success=False,
                output="",
                error=f"Execution error: {e}",
                execution_time=time.time(),
                language=language
            )

class JupyterIntegration:
    """Jupyter notebook entegrasyonu"""
    
    def __init__(self):
        self.notebook_dir = Path("notebooks")
        self.notebook_dir.mkdir(exist_ok=True)
        
    def create_notebook(self, name: str, code: str = "") -> str:
        """Yeni notebook oluştur"""
        notebook_path = self.notebook_dir / f"{name}.ipynb"
        
        notebook = {
            "cells": [
                {
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "outputs": [],
                    "source": [code]
                }
            ],
            "metadata": {
                "kernelspec": {
                    "display_name": "Python 3",
                    "language": "python",
                    "name": "python3"
                }
            },
            "nbformat": 4,
            "nbformat_minor": 4
        }
        
        with open(notebook_path, 'w', encoding='utf-8') as f:
            json.dump(notebook, f, indent=2)
            
        return str(notebook_path)
        
    def add_cell(self, notebook_path: str, code: str, cell_type: str = "code") -> bool:
        """Notebook'a yeni hücre ekle"""
        try:
            with open(notebook_path, 'r', encoding='utf-8') as f:
                notebook = json.load(f)
                
            new_cell = {
                "cell_type": cell_type,
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [code]
            }
            
            notebook["cells"].append(new_cell)
            
            with open(notebook_path, 'w', encoding='utf-8') as f:
                json.dump(notebook, f, indent=2)
                
            return True
            
        except Exception as e:
            console.print(f"[red]❌ Notebook hatası: {e}[/red]")
            return False

class CodeDebugger:
    """Gelişmiş kod debug özellikleri"""
    
    def __init__(self):
        self.breakpoints = []
        self.variables = {}
        
    def add_breakpoint(self, line: int, condition: str = None):
        """Breakpoint ekle"""
        self.breakpoints.append({
            'line': line,
            'condition': condition
        })
        
    def debug_code(self, code: str) -> Dict[str, Any]:
        """Kodu debug modunda çalıştır"""
        # Basit debug simülasyonu
        lines = code.split('\n')
        debug_info = {
            'total_lines': len(lines),
            'breakpoints': self.breakpoints,
            'variables': {},
            'execution_path': []
        }
        
        for i, line in enumerate(lines, 1):
            debug_info['execution_path'].append({
                'line': i,
                'code': line.strip(),
                'executed': True
            })
            
        return debug_info

# Global instances
sandbox_executor = SandboxedExecutor()
jupyter_integration = JupyterIntegration()
code_debugger = CodeDebugger() 