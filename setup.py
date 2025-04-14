#!/usr/bin/env python3
"""
Cross-platform setup script for multilingual emotion chatbot.
This script sets up the required environment for both Windows and Linux.
"""

import os
import sys
import platform
import subprocess
import shutil
from pathlib import Path

def check_python_version():
    """Check if Python version is 3.8 or higher."""
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required.")
        sys.exit(1)
    print(f"Python version: {sys.version.split()[0]} ✓")

def create_virtual_env():
    """Create a virtual environment."""
    if os.path.exists(".venv"):
        print("Virtual environment already exists.")
        return

    print("Creating virtual environment...")
    subprocess.run([sys.executable, "-m", "venv", ".venv"], check=True)
    print("Virtual environment created ✓")

def get_activate_command():
    """Get the command to activate the virtual environment based on the platform."""
    if platform.system() == "Windows":
        return [os.path.join(".venv", "Scripts", "activate.bat")]
    else:  # Linux/Mac
        return ["source", os.path.join(".venv", "bin", "activate")]

def install_requirements():
    """Install Python dependencies."""
    print("Installing Python dependencies...")
    
    # Determine the pip command based on platform
    if platform.system() == "Windows":
        pip_cmd = [os.path.join(".venv", "Scripts", "pip")]
    else:  # Linux/Mac
        pip_cmd = [os.path.join(".venv", "bin", "pip")]
    
    # Upgrade pip
    subprocess.run([*pip_cmd, "install", "--upgrade", "pip"], check=True)
    
    # Install requirements
    subprocess.run([*pip_cmd, "install", "-r", "requirements.txt"], check=True)
    
    print("Python dependencies installed ✓")

def setup_vosk_models():
    """Download Vosk speech recognition models for supported languages."""
    print("Setting up Vosk speech recognition models...")
    
    # Create models directory if it doesn't exist
    models_dir = Path("models/vosk")
    models_dir.mkdir(parents=True, exist_ok=True)
    
    # Determine the pip command based on platform
    if platform.system() == "Windows":
        pip_cmd = [os.path.join(".venv", "Scripts", "pip")]
    else:  # Linux/Mac
        pip_cmd = [os.path.join(".venv", "bin", "pip")]
    
    # List of models to download
    models = {
        "vosk-model-small-en-us": "English (US) - Small",
        "vosk-model-small-ur": "Urdu - Small",
        "vosk-model-small-hi": "Hindi - Small",
        "vosk-model-small-pa": "Punjabi - Small"
    }
    
    for model, description in models.items():
        print(f"Installing {description} model...")
        try:
            subprocess.run([*pip_cmd, "install", model], check=True)
            # Find the installed model and copy it to our models directory
            if platform.system() == "Windows":
                python_cmd = [os.path.join(".venv", "Scripts", "python")]
            else:  # Linux/Mac
                python_cmd = [os.path.join(".venv", "bin", "python")]
            
            # Get the site-packages directory
            result = subprocess.run(
                [*python_cmd, "-c", "import site; print(site.getsitepackages()[0])"],
                capture_output=True,
                text=True,
                check=True
            )
            site_packages = result.stdout.strip()
            
            # Copy the model to our models directory
            model_dir = os.path.join(site_packages, model)
            if os.path.exists(model_dir):
                # Extract just the model name (without vosk-model- prefix)
                model_name = model.replace("vosk-model-small-", "")
                target_dir = os.path.join(models_dir, model_name)
                
                # Create the target directory if it doesn't exist
                if os.path.exists(target_dir):
                    shutil.rmtree(target_dir)
                
                shutil.copytree(model_dir, target_dir)
                print(f"Copied {model} to {target_dir} ✓")
            else:
                print(f"Warning: Could not find {model} in {site_packages}")
        except subprocess.CalledProcessError:
            print(f"Warning: Failed to install {model}. You may need to download it manually.")

def create_directories():
    """Create necessary directories."""
    directories = [
        "data/processed",
        "models/llm",
        "models/vosk",
        "outputs/speech",
        "logs"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    print("Directories created ✓")

def create_startup_scripts():
    """Create startup scripts for Windows and Linux."""
    # Windows batch script
    with open("start.bat", "w") as f:
        f.write("@echo off\n")
        f.write("call .venv\\Scripts\\activate\n")
        f.write("python src\\app.py\n")
        f.write("pause\n")
    
    # Linux shell script
    with open("start.sh", "w") as f:
        f.write("#!/bin/bash\n")
        f.write("source .venv/bin/activate\n")
        f.write("python src/app.py\n")
    
    # Make the Linux script executable
    if platform.system() != "Windows":
        os.chmod("start.sh", 0o755)
    
    print("Startup scripts created ✓")

def main():
    """Main setup function."""
    print("=" * 60)
    print("Setting up Multilingual Emotion Chatbot")
    print("=" * 60)
    
    check_python_version()
    create_virtual_env()
    install_requirements()
    create_directories()
    setup_vosk_models()
    create_startup_scripts()
    
    print("\nSetup complete! You can now run the chatbot:")
    if platform.system() == "Windows":
        print("  - Windows: Run 'start.bat'")
    else:
        print("  - Linux: Run './start.sh'")
    print("=" * 60)

if __name__ == "__main__":
    main()