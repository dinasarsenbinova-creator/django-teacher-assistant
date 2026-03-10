@echo off
echo ============================================
echo   Подготовка проекта для GitHub
echo ============================================
echo.

cd /d "%~dp0"

echo [1/6] Инициализация Git репозитория...
git init
if errorlevel 1 (
    echo ОШИБКА: Git не установлен! Скачайте с https://git-scm.com/download/win
    pause
    exit /b 1
)

echo.
echo [2/6] Добавление файлов...
git add .

echo.
echo [3/6] Создание первого коммита...
git commit -m "Initial commit: Django Teacher Assistant"

echo.
echo [4/6] Настройка основной ветки...
git branch -M main

echo.
echo ============================================
echo   Git репозиторий готов!
echo ============================================
echo.
echo Следующие шаги:
echo.
echo 1. Создайте репозиторий на GitHub:
echo    https://github.com/new
echo.
echo 2. Скопируйте URL вашего репозитория
echo.
echo 3. Выполните команды (замените YOUR_USERNAME и YOUR_REPO):
echo.
echo    git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
echo    git push -u origin main
echo.
echo 4. Откройте DEPLOY_INSTRUCTIONS.md для деплоя на Railway/Render
echo.
pause
