#!/bin/bash
echo "Starting Multilingual Emotion Chatbot..."
echo "Checking if Ollama is running..."
if ! curl -s http://localhost:11434/api/version > /dev/null; then
    echo "Ollama is not running. Starting Ollama..."
    ollama serve &
    echo "Waiting for Ollama to start..."
    sleep 5
fi
source .venv/bin/activate
python src/pipeline.py
