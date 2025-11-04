@echo off

REM Start frontend (npm) in background
cd frontend
start "" cmd /c "npm run start"

REM Start backend (python manage.py)
cd ..\backend
.\venv\Scripts\activate
python manage.py