#!/usr/bin/env python3
"""
Publish script for CortexCLI package to PyPI
"""

import os
import sys
import subprocess
import argparse
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

def check_prerequisites():
    """Check if prerequisites are met"""
    print("🔍 Checking prerequisites...")
    
    # Check if build artifacts exist
    dist_dir = Path("dist")
    if not dist_dir.exists():
        print("❌ No build artifacts found. Run 'python build.py build' first.")
        return False
    
    # Check for wheel and sdist
    wheel_files = list(dist_dir.glob("*.whl"))
    sdist_files = list(dist_dir.glob("*.tar.gz"))
    
    if not wheel_files:
        print("❌ No wheel files found in dist/")
        return False
    
    if not sdist_files:
        print("❌ No source distribution files found in dist/")
        return False
    
    print(f"✅ Found {len(wheel_files)} wheel files and {len(sdist_files)} source distributions")
    return True

def check_twine():
    """Check if twine is installed"""
    try:
        run_command("twine --version", check=False)
        return True
    except FileNotFoundError:
        print("❌ twine not found. Install with: pip install twine")
        return False

def upload_to_testpypi():
    """Upload to TestPyPI"""
    print("📤 Uploading to TestPyPI...")
    
    try:
        run_command("twine upload --repository testpypi dist/*")
        print("✅ Successfully uploaded to TestPyPI!")
        print("🔗 TestPyPI URL: https://test.pypi.org/project/cortexcli/")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to upload to TestPyPI: {e}")
        return False

def upload_to_pypi():
    """Upload to PyPI"""
    print("📤 Uploading to PyPI...")
    
    try:
        run_command("twine upload dist/*")
        print("✅ Successfully uploaded to PyPI!")
        print("🔗 PyPI URL: https://pypi.org/project/cortexcli/")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to upload to PyPI: {e}")
        return False

def check_package():
    """Check package before upload"""
    print("🔍 Checking package...")
    
    try:
        run_command("twine check dist/*")
        print("✅ Package check passed!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Package check failed: {e}")
        return False

def main():
    """Main publish function"""
    parser = argparse.ArgumentParser(description="Publish CortexCLI to PyPI")
    parser.add_argument("--test", action="store_true", help="Upload to TestPyPI instead of PyPI")
    parser.add_argument("--check-only", action="store_true", help="Only check package, don't upload")
    parser.add_argument("--force", action="store_true", help="Skip confirmation prompts")
    
    args = parser.parse_args()
    
    print("🚀 CortexCLI Publish Script")
    print("=" * 50)
    
    # Check prerequisites
    if not check_prerequisites():
        sys.exit(1)
    
    if not check_twine():
        sys.exit(1)
    
    # Check package
    if not check_package():
        sys.exit(1)
    
    if args.check_only:
        print("✅ Package check completed successfully!")
        return
    
    # Confirm upload
    if not args.force:
        target = "TestPyPI" if args.test else "PyPI"
        response = input(f"Are you sure you want to upload to {target}? (y/N): ")
        if response.lower() != 'y':
            print("Upload cancelled.")
            return
    
    # Upload
    if args.test:
        success = upload_to_testpypi()
    else:
        success = upload_to_pypi()
    
    if success:
        print("🎉 Package published successfully!")
        
        if args.test:
            print("\n📝 To install from TestPyPI:")
            print("pip install --index-url https://test.pypi.org/simple/ cortexcli")
        else:
            print("\n📝 To install from PyPI:")
            print("pip install cortexcli")
    else:
        print("❌ Package publishing failed!")
        sys.exit(1)

if __name__ == "__main__":
    main() 