#!/usr/bin/env python3
"""
Build script for CortexCLI package
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def run_command(command, check=True):
    """Run a shell command"""
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    
    if check and result.returncode != 0:
        raise subprocess.CalledProcessError(result.returncode, command)
    
    return result

def clean_build():
    """Clean build artifacts"""
    print("🧹 Cleaning build artifacts...")
    
    dirs_to_clean = ["build", "dist", "*.egg-info"]
    for pattern in dirs_to_clean:
        for path in Path(".").glob(pattern):
            if path.is_dir():
                shutil.rmtree(path)
                print(f"Removed: {path}")
            else:
                path.unlink()
                print(f"Removed: {path}")

def run_tests():
    """Run tests"""
    print("🧪 Running tests...")
    try:
        run_command("python -m pytest tests/ -v")
        print("✅ Tests passed!")
    except subprocess.CalledProcessError:
        print("❌ Tests failed!")
        sys.exit(1)

def check_code_quality():
    """Check code quality"""
    print("🔍 Checking code quality...")
    
    # Check if tools are available
    tools = {
        "black": "python -m black --check .",
        "flake8": "python -m flake8 .",
        "mypy": "python -m mypy ."
    }
    
    for tool, command in tools.items():
        try:
            print(f"Running {tool}...")
            run_command(command)
            print(f"✅ {tool} passed!")
        except subprocess.CalledProcessError:
            print(f"❌ {tool} failed!")
            print(f"Run '{command}' to see details")
        except FileNotFoundError:
            print(f"⚠️  {tool} not installed, skipping...")

def build_package():
    """Build the package"""
    print("📦 Building package...")
    
    # Build both wheel and source distribution
    run_command("python -m build")
    
    print("✅ Package built successfully!")

def build_docker():
    """Build Docker image"""
    print("🐳 Building Docker image...")
    
    try:
        run_command("docker build -t cortexcli:latest .")
        print("✅ Docker image built successfully!")
    except subprocess.CalledProcessError:
        print("❌ Docker build failed!")
        sys.exit(1)

def main():
    """Main build function"""
    print("🚀 CortexCLI Build Script")
    print("=" * 50)
    
    # Parse command line arguments
    args = sys.argv[1:]
    
    if not args:
        print("Usage: python build.py [clean|test|quality|build|docker|all]")
        sys.exit(1)
    
    command = args[0]
    
    try:
        if command == "clean":
            clean_build()
        elif command == "test":
            run_tests()
        elif command == "quality":
            check_code_quality()
        elif command == "build":
            build_package()
        elif command == "docker":
            build_docker()
        elif command == "all":
            clean_build()
            run_tests()
            check_code_quality()
            build_package()
            build_docker()
        else:
            print(f"Unknown command: {command}")
            sys.exit(1)
            
        print("🎉 Build completed successfully!")
        
    except Exception as e:
        print(f"❌ Build failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 