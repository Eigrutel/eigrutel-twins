@echo off
cd /d "%~dp0"
py -3 EigrutelTwins.py
if errorlevel 1 pause
