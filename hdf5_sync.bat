@echo off
cd /D "%~dp0"
call .venv\scripts\activate
python -m hdf5_sync
pause
