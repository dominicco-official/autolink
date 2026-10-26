@echo off
echo Starting AutoLink demo at http://127.0.0.1:8777 (close this window to stop)
start http://127.0.0.1:8777/
C:\Users\domlimco\AppData\Local\miniconda3\Scripts\conda.exe run -n autolink-cad --no-capture-output python "%~dp0server.py" 8777

