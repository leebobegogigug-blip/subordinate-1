@echo off
rem M0 check kit launcher. Usage: kit\env\run.cmd env | template "PATH" | office
rem Uses kit\env\.venv if present, else "py -3", else "python".
if exist "%~dp0.venv\Scripts\python.exe" goto venv
where py >nul 2>nul
if not errorlevel 1 goto pylauncher
where python >nul 2>nul
if not errorlevel 1 goto plainpython
echo Python was not found. Install Python 3.8 or newer, then run again.
exit /b 1
:venv
"%~dp0.venv\Scripts\python.exe" "%~dp0check_env.py" %*
exit /b %errorlevel%
:pylauncher
py -3 "%~dp0check_env.py" %*
exit /b %errorlevel%
:plainpython
python "%~dp0check_env.py" %*
exit /b %errorlevel%
