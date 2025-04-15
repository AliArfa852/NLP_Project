#!/usr/bin/env python3
"""
Startup script for the Emotion Chatbot Web Interface.
This script checks dependencies and starts the Flask web server.
"""

import os
import sys
import subprocess
import platform
import webbrowser
import time
import threading

def check_python_version():
    """Check if Python version is 3.8 or higher."""
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required.")
        sys.exit(1)
    print(f"✓ Python version: {sys.version.split()[0]}")

def check_dependencies():
    """Check if required packages are installed."""
    required_packages = ['flask', 'yaml', 'requests', 'pymongo']
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    # if missing_packages:
    #     print(f"Error: Missing required packages: {', '.join(missing_packages)}")
    #     print("Please run: pip install -r requirements-web.txt")
    #     sys.exit(1)
    
    print("✓ Required packages are installed")

def check_vosk_models():
    """Check if Vosk speech recognition models are available."""
    model_dir = os.path.join("models", "vosk")
    
    if not os.path.exists(model_dir):
        print("Warning: Vosk model directory not found.")
        print("Speech recognition might not work correctly.")
    else:
        models = [d for d in os.listdir(model_dir) if os.path.isdir(os.path.join(model_dir, d))]
        if not models:
            print("Warning: No Vosk models found in models/vosk/")
            print("Speech recognition might not work correctly.")
        else:
            print(f"✓ Found {len(models)} Vosk models: {', '.join(models)}")

def check_ollama():
    """Check if Ollama is installed and running."""
    try:
        import requests
        response = requests.get("http://localhost:11434/api/version", timeout=2)
        if response.status_code == 200:
            print(f"✓ Ollama is running: {response.json().get('version', 'unknown version')}")
        else:
            print("Warning: Ollama is not responding correctly.")
    except Exception:
        print("Warning: Ollama is not running or not installed.")
        print("Please start Ollama before running the application.")

def start_flask_app():
    """Start the Flask web application."""
    try:
        from app import app
        
        # Determine the host and port
        host = '0.0.0.0'  # Listen on all interfaces
        port = 5000  # Default Flask port
        
        # Check if port is in use
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', port))
        if result == 0:
            print(f"Warning: Port {port} is already in use.")
            port = 5001
            print(f"Trying port {port} instead.")
        sock.close()
        
        print(f"\nStarting web server on http://localhost:{port}")
        print("Press Ctrl+C to stop the server")
        
        # Open web browser after a short delay
        def open_browser():
            time.sleep(1.5)
            webbrowser.open(f"http://localhost:{port}")
        
        threading.Thread(target=open_browser).start()
        
        # Start Flask app
        app.run(host=host, port=port, debug=False)
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Error starting Flask app: {str(e)}")
        sys.exit(1)

def main():
    """Main function to run the startup checks and start the application."""
    print("=" * 60)
    print("Emotion Chatbot Web Interface - Startup")
    print("=" * 60)
    
    # Run startup checks
    check_python_version()
    check_dependencies()
    check_vosk_models()
    check_ollama()
    
    # Create necessary directories
    os.makedirs("logs", exist_ok=True)
    os.makedirs("static/uploads", exist_ok=True)
    os.makedirs("static/temp", exist_ok=True)
    
    print("\nAll checks completed. Starting web application...")
    start_flask_app()

if __name__ == "__main__":
    main()