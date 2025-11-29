#!/usr/bin/env python3
"""
Setup script for MAS Training Audio Generator
Creates virtual environment and installs dependencies
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Command: {cmd}")
        print(f"   Error: {e.stderr.strip()}")
        return False

def main():
    """Set up the project environment."""
    print("🏃 MAS Training Audio Generator Setup")
    print("=" * 50)

    # Check if we're already in a virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  Already in a virtual environment")
        choice = input("Continue with current environment? (y/n): ").lower()
        if choice != 'y':
            print("Please exit the virtual environment and run setup again.")
            return False
    else:
        # Create virtual environment
        if not run_command("python -m venv .venv", "Creating virtual environment"):
            return False

        print("\n🔧 Virtual environment created!")
        print("To activate it manually:")
        if os.name == 'nt':  # Windows
            print("   .venv\\Scripts\\activate")
        else:  # Unix/Linux/Mac
            print("   source .venv/bin/activate")

    # Determine activation command
    if os.name == 'nt':  # Windows
        pip_cmd = ".venv\\Scripts\\python -m pip"
    else:  # Unix/Linux/Mac
        pip_cmd = ".venv/bin/python -m pip"

    # Upgrade pip
    if not run_command(f"{pip_cmd} install --upgrade pip", "Upgrading pip"):
        return False

    # Install requirements
    if Path("requirements.txt").exists():
        if not run_command(f"{pip_cmd} install -r requirements.txt", "Installing dependencies"):
            return False
    else:
        print("⚠️  requirements.txt not found, installing pyttsx3 directly")
        if not run_command(f"{pip_cmd} install pyttsx3==2.99", "Installing pyttsx3"):
            return False

    print("\n🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Activate the virtual environment:")
    if os.name == 'nt':  # Windows
        print("   .venv\\Scripts\\activate")
    else:  # Unix/Linux/Mac
        print("   source .venv/bin/activate")
    print("2. Run the application:")
    print("   python mas.py")
    print("\nThis will generate 'mas_training_audio.wav' for your training session.")

    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)