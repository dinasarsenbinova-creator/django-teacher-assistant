@echo off
REM Скрипт для быстрого старта Ассистента педагога (Windows)

echo.
echo ========================================
echo Ассистент педагога - Быстрый старт
echo ========================================
echo.

echo 1. Активация виртуального окружения...
call .venv\Scripts\activate.bat

echo 2. Установка зависимостей...
pip install -r requirements.txt

echo 3. Применение миграций БД...
python manage.py migrate

echo 4. Загрузка тестовых данных...
python load_test_data.py

echo.
echo ========================================
echo ✓ Инициализация завершена!
echo ========================================
echo.
echo Для запуска приложения выполните:
echo   python manage.py runserver
echo.
echo Затем откройте в браузере:
echo   http://localhost:8000/teacher/
echo.
pause
