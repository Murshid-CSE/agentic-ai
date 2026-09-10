@echo off
title VerifyFlow Interactive Demo
cd /d "%~dp0\verifyflow"
if exist ".venv\Scripts\python.exe" (
    .venv\Scripts\python.exe run_demo.py
) else (
    python run_demo.py
)
pause
