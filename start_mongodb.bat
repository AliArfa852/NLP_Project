@echo off
echo Starting MongoDB...
start "MongoDB" mongod --dbpath=data\mongodb
echo MongoDB is running. Press Ctrl+C to stop.
pause
