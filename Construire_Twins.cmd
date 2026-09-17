@echo off
setlocal
cd /d "%~dp0"
py -3 -m venv .venv
if errorlevel 1 goto erreur
".venv\Scripts\python.exe" -m pip install -r requirements-build.txt
if errorlevel 1 goto erreur
".venv\Scripts\python.exe" build_windows.py
if errorlevel 1 goto erreur
echo.
echo Twins-1.0.0.exe est dans le dossier dist.
echo Fermez l ancien Twins puis lancez ce nouveau fichier.
echo Vos preferences restent dans LOCALAPPDATA\EigrutelLab\Twins.
echo Settings stay in LOCALAPPDATA\EigrutelLab\Twins.
pause
exit /b 0
:erreur
echo.
echo Construction interrompue / Build failed. Consultez le message ci-dessus.
pause
exit /b 1
