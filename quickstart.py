#!/usr/bin/env python3
"""
Quick Start Script for VerdicTech AI Engine
This script helps you verify your setup and get started quickly.
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)

def print_step(step, text):
    """Print a step"""
    print(f"\n[{step}] {text}")

def check_python_version():
    """Check if Python version is 3.8+"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ is required")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True

def check_env_file():
    """Check if .env file exists and has required variables"""
    if not Path(".env").exists():
        print("❌ .env file not found")
        print("   Run: copy .env.example .env")
        print("   Then edit .env and add your OpenAI API key")
        return False
    
    with open(".env", "r") as f:
        content = f.read()
        if "your_openai_api_key_here" in content or "OPENAI_API_KEY=" not in content:
            print("⚠️  .env file exists but may not be configured")
            print("   Make sure to add your OpenAI API key to .env")
            return False
    
    print("✅ .env file configured")
    return True

def check_venv():
    """Check if virtual environment exists"""
    venv_path = Path("venv")
    if not venv_path.exists():
        print("⚠️  Virtual environment not found")
        print("   Run: python -m venv venv")
        return False
    print("✅ Virtual environment exists")
    return True

def check_qdrant():
    """Check if Qdrant is accessible"""
    try:
        import requests
        response = requests.get("http://localhost:6333/", timeout=2)
        if response.status_code == 200:
            print("✅ Qdrant is running")
            return True
    except:
        pass
    
    print("❌ Qdrant is not running")
    print("   Run: docker run -p 6333:6333 qdrant/qdrant")
    return False

def check_packages():
    """Check if required packages are installed"""
    try:
        import fastapi
        import openai
        import qdrant_client
        import langchain
        print("✅ Required packages installed")
        return True
    except ImportError as e:
        print(f"❌ Missing package: {e.name}")
        print("   Run: pip install -r requirements.txt")
        return False

def main():
    """Main quickstart function"""
    print_header("VerdicTech AI Engine - Quick Start")
    
    print("\n🚀 Checking your setup...\n")
    
    all_good = True
    
    # Check 1: Python version
    print_step(1, "Checking Python version...")
    if not check_python_version():
        all_good = False
    
    # Check 2: Virtual environment
    print_step(2, "Checking virtual environment...")
    if not check_venv():
        all_good = False
    
    # Check 3: Environment file
    print_step(3, "Checking .env configuration...")
    if not check_env_file():
        all_good = False
    
    # Check 4: Python packages
    print_step(4, "Checking Python packages...")
    if not check_packages():
        all_good = False
    
    # Check 5: Qdrant
    print_step(5, "Checking Qdrant connection...")
    if not check_qdrant():
        all_good = False
    
    # Summary
    print_header("Setup Status")
    
    if all_good:
        print("\n🎉 All checks passed! You're ready to go!")
        print("\n📝 Next steps:")
        print("   1. Start the service:")
        print("      Windows: start.bat")
        print("      Linux/Mac: python main.py")
        print("\n   2. Test the API:")
        print("      python test_client.py")
        print("\n   3. Open API docs:")
        print("      http://localhost:8000/docs")
    else:
        print("\n⚠️  Some checks failed. Please fix the issues above.")
        print("\n📚 Need help? Read SETUP_GUIDE.md")
    
    print("\n" + "=" * 60 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)
