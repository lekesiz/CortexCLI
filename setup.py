"""
CortexCLI - AI Assistant CLI
Setup configuration for PyPI distribution
"""

from setuptools import setup, find_packages
import os

# Read README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="cortexcli",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A powerful AI assistant CLI with Ollama integration, plugin system, and web interface",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/cortexcli",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/cortexcli/issues",
        "Documentation": "https://github.com/yourusername/cortexcli#readme",
        "Source Code": "https://github.com/yourusername/cortexcli",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: System :: Shells",
        "Topic :: Terminals",
        "Topic :: Utilities",
    ],
    packages=find_packages(),
    py_modules=[
        "llm_shell",
        "config",
        "plugin_system",
        "multi_model",
        "advanced_code_execution",
        "web_interface"
    ],
    include_package_data=True,
    package_data={
        "": [
            "web_templates/*.html",
            "web_static/*",
            "plugins/*.py",
            "*.md",
            "*.txt",
            "*.sh"
        ],
    },
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "pre-commit>=3.0.0",
        ],
        "web": [
            "flask>=2.3.0",
            "flask-socketio>=5.3.0",
        ],
        "docker": [
            "docker>=6.0.0",
        ],
        "full": [
            "flask>=2.3.0",
            "flask-socketio>=5.3.0",
            "docker>=6.0.0",
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "cortexcli=llm_shell:main",
            "cortex=llm_shell:main",
        ],
    },
    python_requires=">=3.8",
    keywords=[
        "ai",
        "assistant",
        "cli",
        "ollama",
        "llm",
        "chat",
        "terminal",
        "shell",
        "plugin",
        "web-interface",
        "code-execution",
        "multi-model",
    ],
    zip_safe=False,
) 