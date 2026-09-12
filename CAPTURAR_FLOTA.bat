@echo off
REM Deja corriendo la captura de flota durante una semana en este equipo.
REM Necesita Python 3 instalado y marcado "Add to PATH" (python.org/downloads).
REM La ventana tiene que quedarse abierta; Ctrl+C la detiene sin perder lo leido.
cd /d "%~dp0"
python tools\capture_fleet.py --out data\raw\fleet_capture\fleet.jsonl --every 15 --from-hour 6 --to-hour 22 --days 8
pause
