@echo off
REM Запуск Django development server используя python из .venv
SETLOCAL ENABLEDELAYEDEXPANSION
SET "PROJECT_DIR=%~dp0"
PUSHD "%PROJECT_DIR%"
IF EXIST ".venv\Scripts\activate.bat" (
    CALL ".venv\Scripts\activate.bat"
    python manage.py runserver 0.0.0.0:8000
) ELSE (
    "%~dp0\.venv\Scripts\python.exe" manage.py runserver 0.0.0.0:8000
)
POPD
ENDLOCAL
