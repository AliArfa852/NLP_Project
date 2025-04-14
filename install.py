#!/usr/bin/env python3
"""
Complete installation script for Multilingual Emotion Chatbot.
This script sets up the entire environment on both Windows and Linux.
"""

import os
import sys
import subprocess
import platform
import shutil
import time
import urllib.request
import zipfile
import tarfile
import json
from pathlib import Path

# Define colors for console output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_color(text, color=Colors.BLUE):
    """Print colored text to the console."""
    print(f"{color}{text}{Colors.ENDC}")

def print_step(step_num, total_steps, description):
    """Print a formatted step header."""
    print("\n" + "=" * 80)
    print_color(f"Step {step_num}/{total_steps}: {description}", Colors.HEADER + Colors.BOLD)
    print("=" * 80)

def check_python_version():
    """Check if Python version is 3.8 or higher."""
    if sys.version_info < (3, 8):
        print_color("Error: Python 3.8 or higher is required.", Colors.RED)
        sys.exit(1)
    print_color(f"✓ Python version: {sys.version.split()[0]}", Colors.GREEN)

def get_platform_info():
    """Get detailed information about the current platform."""
    system = platform.system().lower()
    info = {
        "system": system,
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "python_version": sys.version.split()[0],
        "is_64bit": sys.maxsize > 2**32
    }
    
    if system == "windows":
        info["admin"] = is_admin_windows()
    elif system in ["linux", "darwin"]:
        info["admin"] = is_admin_unix()
    else:
        info["admin"] = False
    
    return info

def is_admin_windows():
    """Check if the script is running with administrative privileges on Windows."""
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False

def is_admin_unix():
    """Check if the script is running with administrative privileges on Unix."""
    try:
        return os.geteuid() == 0
    except:
        return False

def create_virtual_env():
    """Create a virtual environment."""
    if os.path.exists(".venv"):
        print_color("Virtual environment already exists.", Colors.YELLOW)
        choice = input("Do you want to recreate it? (y/n): ").lower()
        if choice == 'y':
            try:
                shutil.rmtree(".venv")
                print_color("Removed existing virtual environment.", Colors.YELLOW)
            except Exception as e:
                print_color(f"Error removing virtual environment: {str(e)}", Colors.RED)
                return False
        else:
            return True

    print_color("Creating virtual environment...", Colors.BLUE)
    try:
        subprocess.run([sys.executable, "-m", "venv", ".venv"], check=True)
        print_color("✓ Virtual environment created", Colors.GREEN)
        return True
    except Exception as e:
        print_color(f"Error creating virtual environment: {str(e)}", Colors.RED)
        return False

def get_venv_python():
    """Get the path to the Python executable in the virtual environment."""
    if platform.system().lower() == "windows":
        return os.path.abspath(".venv\\Scripts\\python.exe")
    else:
        return os.path.abspath(".venv/bin/python")

def get_venv_pip():
    """Get the path to the pip executable in the virtual environment."""
    if platform.system().lower() == "windows":
        return os.path.abspath(".venv\\Scripts\\pip.exe")
    else:
        return os.path.abspath(".venv/bin/pip")

def activate_venv_command():
    """Get the command to activate the virtual environment."""
    if platform.system().lower() == "windows":
        return f"call {os.path.abspath('.venv/Scripts/activate.bat')}"
    else:
        return f"source {os.path.abspath('.venv/bin/activate')}"

def install_requirements():
    """Install Python dependencies."""
    print_color("Installing Python dependencies...", Colors.BLUE)
    pip = get_venv_pip()
    
    # Upgrade pip
    try:
        subprocess.run([pip, "install", "--upgrade", "pip"], check=True)
        print_color("✓ Upgraded pip", Colors.GREEN)
    except Exception as e:
        print_color(f"Error upgrading pip: {str(e)}", Colors.RED)
    
    # Install requirements
    try:
        subprocess.run([pip, "install", "-r", "requirements.txt"], check=True)
        print_color("✓ Installed dependencies from requirements.txt", Colors.GREEN)
        return True
    except Exception as e:
        print_color(f"Error installing requirements: {str(e)}", Colors.RED)
        return False

def install_vosk_models():
    """Install Vosk speech recognition models."""
    print_color("Installing Vosk speech recognition models...", Colors.BLUE)
    pip = get_venv_pip()
    
    # Create models directory
    os.makedirs("models/vosk", exist_ok=True)
    
    # List of models to install
    models = [
        {"name": "vosk-model-small-en-us-0.15", "description": "English US (small)"},
        {"name": "vosk-model-small-en-in-0.4", "description": "English India (for Roman Urdu)"},
        {"name": "vosk-model-small-hi-0.22", "description": "Hindi (small)"},
        {"name": "vosk-model-small-hi-0.22", "description": "Punjabi (small)"}
    ]
    
    success_count = 0
    for model in models:
        model_name = model["name"]
        try:
            print_color(f"Installing {model['description']} model...", Colors.BLUE)
            result = subprocess.run(
                [pip, "install", model_name], 
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode != 0:
                print_color(f"Warning: Failed to install {model_name}:", Colors.YELLOW)
                print_color(result.stderr, Colors.YELLOW)
                continue
            
            # Find where the model was installed
            site_packages_cmd = [get_venv_python(), "-c", 
                                "import site; print(site.getsitepackages()[0])"]
            result = subprocess.run(site_packages_cmd, capture_output=True, text=True, check=True)
            site_packages = result.stdout.strip()
            
            # Extract the model name without the prefix
            short_name = model_name.replace("vosk-model-small-", "")
            target_dir = os.path.join("models", "vosk", short_name)
            
            # Check if the model exists in site-packages
            model_path = os.path.join(site_packages, model_name)
            if os.path.exists(model_path):
                # Create the target directory or clear it if it exists
                if os.path.exists(target_dir):
                    shutil.rmtree(target_dir)
                
                # Copy the model files
                shutil.copytree(model_path, target_dir)
                print_color(f"✓ Installed {model['description']} model", Colors.GREEN)
                success_count += 1
            else:
                print_color(f"Warning: Could not find {model_name} in {site_packages}", Colors.YELLOW)
                
        except Exception as e:
            print_color(f"Error installing {model_name}: {str(e)}", Colors.RED)
    
    if success_count > 0:
        print_color(f"✓ Successfully installed {success_count} of {len(models)} Vosk models", Colors.GREEN)
        return True
    else:
        print_color("Failed to install any Vosk models. Speech recognition may not work.", Colors.RED)
        return False

def detect_ollama():
    """Check if Ollama is installed and running."""
    print_color("Checking Ollama installation...", Colors.BLUE)
    
    # Check if Ollama is in PATH
    ollama_path = shutil.which("ollama")
    if ollama_path:
        print_color(f"✓ Ollama found at: {ollama_path}", Colors.GREEN)
        
        # Check if Ollama is running
        try:
            # Try to connect to the Ollama API
            import urllib.request
            import json
            import time
            
            try:
                with urllib.request.urlopen("http://localhost:11434/api/version", timeout=2) as response:
                    if response.status == 200:
                        version = json.loads(response.read().decode())
                        print_color(f"✓ Ollama is running (version: {version.get('version', 'unknown')})", Colors.GREEN)
                        return True
            except:
                print_color("Ollama is installed but not running.", Colors.YELLOW)
                
                # Try to start Ollama
                try:
                    if platform.system().lower() == "windows":
                        # On Windows, start Ollama in a new command window
                        subprocess.Popen(["start", "cmd", "/c", "ollama", "serve"], 
                                        shell=True, 
                                        stdout=subprocess.DEVNULL, 
                                        stderr=subprocess.DEVNULL)
                    else:
                        # On Linux/Mac, start Ollama in the background
                        subprocess.Popen(["ollama", "serve"], 
                                        stdout=subprocess.DEVNULL, 
                                        stderr=subprocess.DEVNULL)
                    
                    print_color("Started Ollama service. Waiting for it to initialize...", Colors.BLUE)
                    
                    # Wait for Ollama to start
                    for _ in range(10):  # Try for 10 seconds
                        time.sleep(1)
                        try:
                            with urllib.request.urlopen("http://localhost:11434/api/version", timeout=1) as response:
                                if response.status == 200:
                                    print_color("✓ Ollama service started successfully", Colors.GREEN)
                                    return True
                        except:
                            pass
                    
                    print_color("Could not confirm that Ollama started. Please start it manually.", Colors.YELLOW)
                except Exception as e:
                    print_color(f"Error starting Ollama: {str(e)}", Colors.YELLOW)
                    print_color("Please start Ollama manually before running the application.", Colors.YELLOW)
        except ImportError:
            print_color("Could not check if Ollama is running. Please ensure it's started before running the application.", Colors.YELLOW)
        
        return True
    else:
        print_color("Ollama not found. You need to install it manually.", Colors.YELLOW)
        print_color("Please visit https://ollama.ai/download for installation instructions.", Colors.YELLOW)
        
        if platform.system().lower() == "linux":
            choice = input("Do you want to try installing Ollama now? (y/n): ").lower()
            if choice == 'y':
                try:
                    # Try to install Ollama on Linux
                    print_color("Installing Ollama...", Colors.BLUE)
                    subprocess.run(["curl", "-fsSL", "https://ollama.ai/install.sh"], 
                                input=b"yes\n", 
                                check=True)
                    print_color("✓ Ollama installed", Colors.GREEN)
                    return True
                except Exception as e:
                    print_color(f"Error installing Ollama: {str(e)}", Colors.RED)
                    print_color("Please install Ollama manually before running the application.", Colors.YELLOW)
        
        return False

def download_llm_model():
    """Download the required LLM model using Ollama."""
    print_color("Checking LLM models...", Colors.BLUE)
    
    # Read config to get the model name
    try:
        with open("config/config.yaml", "r") as f:
            import yaml
            config = yaml.safe_load(f)
            model_name = config.get("llm", {}).get("model_name", "llama3.2:latest")
    except Exception as e:
        print_color(f"Error reading config file: {str(e)}", Colors.RED)
        model_name = "llama3.2:latest"
        print_color(f"Using default model: {model_name}", Colors.YELLOW)
    
    # Check if the model is already downloaded
    try:
        result = subprocess.run(
            ["ollama", "list"], 
            capture_output=True,
            text=True,
            check=True
        )
        
        if model_name in result.stdout:
            print_color(f"✓ Model {model_name} is already downloaded", Colors.GREEN)
            return True
        
        # Download the model
        print_color(f"Downloading model {model_name}. This may take a while...", Colors.BLUE)
        subprocess.run(["ollama", "pull", model_name], check=True)
        print_color(f"✓ Model {model_name} downloaded successfully", Colors.GREEN)
        return True
        
    except Exception as e:
        print_color(f"Error checking/downloading model: {str(e)}", Colors.RED)
        print_color(f"Please download the model manually by running: ollama pull {model_name}", Colors.YELLOW)
        return False

def create_startup_scripts():
    """Create startup scripts for Windows and Linux."""
    print_color("Creating startup scripts...", Colors.BLUE)
    
    # Windows batch script
    try:
        with open("start.bat", "w") as f:
            f.write("@echo off\n")
            f.write("echo Starting Multilingual Emotion Chatbot...\n")
            f.write("echo Checking if Ollama is running...\n")
            f.write("curl -s http://localhost:11434/api/version >nul 2>&1\n")
            f.write("if %ERRORLEVEL% NEQ 0 (\n")
            f.write("    echo Ollama is not running. Starting Ollama...\n")
            f.write("    start \"Ollama Server\" cmd /c ollama serve\n")
            f.write("    echo Waiting for Ollama to start...\n")
            f.write("    timeout /t 5 /nobreak >nul\n")
            f.write(")\n")
            f.write("call .venv\\Scripts\\activate\n")
            f.write("python src\\pipeline.py\n")
            f.write("pause\n")
        
        print_color("✓ Created Windows startup script (start.bat)", Colors.GREEN)
    except Exception as e:
        print_color(f"Error creating Windows script: {str(e)}", Colors.RED)
    
    # Linux shell script
    try:
        with open("start.sh", "w") as f:
            f.write("#!/bin/bash\n")
            f.write("echo \"Starting Multilingual Emotion Chatbot...\"\n")
            f.write("echo \"Checking if Ollama is running...\"\n")
            f.write("if ! curl -s http://localhost:11434/api/version > /dev/null; then\n")
            f.write("    echo \"Ollama is not running. Starting Ollama...\"\n")
            f.write("    ollama serve &\n")
            f.write("    echo \"Waiting for Ollama to start...\"\n")
            f.write("    sleep 5\n")
            f.write("fi\n")
            f.write("source .venv/bin/activate\n")
            f.write("python src/pipeline.py\n")
        
        # Make the script executable
        os.chmod("start.sh", 0o755)
        print_color("✓ Created Linux startup script (start.sh)", Colors.GREEN)
    except Exception as e:
        print_color(f"Error creating Linux script: {str(e)}", Colors.RED)
    
    return True

def create_mongodb_script():
    """Create script to start MongoDB if available."""
    print_color("Creating MongoDB helper script...", Colors.BLUE)
    
    # Check if MongoDB is installed
    mongo_path = shutil.which("mongod")
    if not mongo_path:
        print_color("MongoDB not found. Skipping MongoDB helper script.", Colors.YELLOW)
        return False
    
    # Create directory for MongoDB data
    os.makedirs("data/mongodb", exist_ok=True)
    
    # Windows batch script
    try:
        if platform.system().lower() == "windows":
            with open("start_mongodb.bat", "w") as f:
                f.write("@echo off\n")
                f.write("echo Starting MongoDB...\n")
                f.write("start \"MongoDB\" mongod --dbpath=data\\mongodb\n")
                f.write("echo MongoDB is running. Press Ctrl+C to stop.\n")
                f.write("pause\n")
            
            print_color("✓ Created MongoDB startup script (start_mongodb.bat)", Colors.GREEN)
        else:
            with open("start_mongodb.sh", "w") as f:
                f.write("#!/bin/bash\n")
                f.write("echo \"Starting MongoDB...\"\n")
                f.write("mongod --dbpath=data/mongodb\n")
            
            # Make the script executable
            os.chmod("start_mongodb.sh", 0o755)
            print_color("✓ Created MongoDB startup script (start_mongodb.sh)", Colors.GREEN)
        
        return True
    except Exception as e:
        print_color(f"Error creating MongoDB script: {str(e)}", Colors.RED)
        return False

def create_directories():
    """Create required directories."""
    print_color("Creating required directories...", Colors.BLUE)
    
    directories = [
        "data/processed",
        "models/llm",
        "models/vosk",
        "outputs/speech",
        "logs"
    ]
    
    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
            print_color(f"✓ Created directory: {directory}", Colors.GREEN)
        except Exception as e:
            print_color(f"Error creating directory {directory}: {str(e)}", Colors.RED)
    
    return True

def check_microphone():
    """Check if a microphone is available."""
    print_color("Checking microphone...", Colors.BLUE)
    
    try:
        import pyaudio
        p = pyaudio.PyAudio()
        
        # Get the number of available input devices
        input_devices = 0
        for i in range(p.get_device_count()):
            device_info = p.get_device_info_by_index(i)
            if device_info.get('maxInputChannels') > 0:
                input_devices += 1
                print_color(f"Found input device: {device_info.get('name')}", Colors.GREEN)
        
        p.terminate()
        
        if input_devices > 0:
            print_color(f"✓ Found {input_devices} microphone(s)", Colors.GREEN)
            return True
        else:
            print_color("No microphones found. Speech input will not work.", Colors.YELLOW)
            return False
    except Exception as e:
        print_color(f"Error checking microphone: {str(e)}", Colors.YELLOW)
        print_color("Could not check for microphones. Speech input may not work.", Colors.YELLOW)
        return False

def main():
    """Main function to run the installation."""
    print_color("\n" + "=" * 80, Colors.HEADER)
    print_color("MULTILINGUAL EMOTION CHATBOT - INSTALLATION", Colors.HEADER + Colors.BOLD)
    print_color("=" * 80 + "\n", Colors.HEADER)
    
    # Get platform information
    platform_info = get_platform_info()
    print_color(f"System: {platform_info['system'].title()} {platform_info['release']} ({platform_info['machine']})", Colors.BLUE)
    print_color(f"Python: {platform_info['python_version']}", Colors.BLUE)
    print_color(f"Running as admin: {'Yes' if platform_info['admin'] else 'No'}", Colors.BLUE)
    print("\n")
    
    # Define the installation steps
    total_steps = 9
    current_step = 1
    
    # Step 1: Check Python version
    print_step(current_step, total_steps, "Checking Python version")
    check_python_version()
    current_step += 1
    
    # Step 2: Create virtual environment
    print_step(current_step, total_steps, "Creating virtual environment")
    create_virtual_env()
    current_step += 1
    
    # Step 3: Install dependencies
    print_step(current_step, total_steps, "Installing dependencies")
    install_requirements()
    current_step += 1
    
    # Step 4: Create directories
    print_step(current_step, total_steps, "Creating directories")
    create_directories()
    current_step += 1
    
    # Step 5: Install Vosk models
    print_step(current_step, total_steps, "Installing speech recognition models")
    install_vosk_models()
    current_step += 1
    
    # Step 6: Check for Ollama
    print_step(current_step, total_steps, "Checking Ollama installation")
    detect_ollama()
    current_step += 1
    
    # Step 7: Download LLM model
    print_step(current_step, total_steps, "Downloading LLM model")
    download_llm_model()
    current_step += 1
    
    # Step 8: Create startup scripts
    print_step(current_step, total_steps, "Creating startup scripts")
    create_startup_scripts()
    create_mongodb_script()
    current_step += 1
    
    # Step 9: Check for microphone
    print_step(current_step, total_steps, "Checking microphone")
    check_microphone()
    
    # All done!
    print("\n" + "=" * 80)
    print_color("INSTALLATION COMPLETE!", Colors.GREEN + Colors.BOLD)
    print("=" * 80)
    print("\nYou can now start the application:")
    if platform_info['system'] == 'windows':
        print_color("  Run 'start.bat'", Colors.YELLOW)
    else:
        print_color("  Run './start.sh'", Colors.YELLOW)
    
    print("\nMake sure Ollama is running before starting the application.")
    print("If you have any issues, please check the README.md file for troubleshooting.")
    print("\nEnjoy your multilingual emotion chatbot!")
    
    # Ask if user wants to start the application now
    choice = input("\nDo you want to start the application now? (y/n): ").lower()
    if choice == 'y':
        print_color("\nStarting the application...", Colors.BLUE)
        
        try:
            if platform_info['system'] == 'windows':
                os.system("start.bat")
            else:
                os.system("./start.sh")
        except Exception as e:
            print_color(f"Error starting application: {str(e)}", Colors.RED)
            print_color("Please start the application manually.", Colors.YELLOW)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_color("\nInstallation interrupted by user.", Colors.YELLOW)
        print_color("You can restart the installation by running this script again.", Colors.YELLOW)
    except Exception as e:
        print_color(f"\nAn error occurred during installation: {str(e)}", Colors.RED)
        import traceback
        traceback.print_exc()
        print_color("\nPlease try again or check the README.md for manual installation instructions.", Colors.YELLOW)