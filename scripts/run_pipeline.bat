@echo off
REM Activate the virtual environment
call .venv\Scripts\activate

REM Run the pipeline script
python src\pipeline.py
