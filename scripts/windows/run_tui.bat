@echo off
cd %~dp0\..\..
call .\venv\Scripts\activate
python app.py
pause
