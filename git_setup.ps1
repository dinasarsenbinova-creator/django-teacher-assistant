# Скрипт для подготовки проекта к GitHub
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Подготовка проекта для GitHub" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

Set-Location $PSScriptRoot

# Проверка Git
Write-Host "[1/6] Проверка Git..." -ForegroundColor Yellow
$gitInstalled = Get-Command git -ErrorAction SilentlyContinue
if (-not $gitInstalled) {
    Write-Host "ОШИБКА: Git не установлен!" -ForegroundColor Red
    Write-Host "Скачайте с https://git-scm.com/download/win" -ForegroundColor Yellow
    Read-Host "Нажмите Enter для выхода"
    exit 1
}

Write-Host "[2/6] Инициализация Git репозитория..." -ForegroundColor Yellow
git init

Write-Host ""
Write-Host "[3/6] Добавление файлов..." -ForegroundColor Yellow
git add .

Write-Host ""
Write-Host "[4/6] Создание первого коммита..." -ForegroundColor Yellow
git commit -m "Initial commit: Django Teacher Assistant"

Write-Host ""
Write-Host "[5/6] Настройка основной ветки..." -ForegroundColor Yellow
git branch -M main

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "  Git репозиторий готов!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "Следующие шаги:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Создайте репозиторий на GitHub:" -ForegroundColor White
Write-Host "   https://github.com/new" -ForegroundColor Yellow
Write-Host ""
Write-Host "2. Скопируйте URL вашего репозитория" -ForegroundColor White
Write-Host ""
Write-Host "3. Выполните команды (замените YOUR_USERNAME и YOUR_REPO):" -ForegroundColor White
Write-Host ""
Write-Host "   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git" -ForegroundColor Green
Write-Host "   git push -u origin main" -ForegroundColor Green
Write-Host ""
Write-Host "4. Откройте DEPLOY_INSTRUCTIONS.md для деплоя на Railway/Render" -ForegroundColor White
Write-Host ""
Read-Host "Нажмите Enter для выхода"
