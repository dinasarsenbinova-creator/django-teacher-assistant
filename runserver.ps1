# Запуск Django development server через интерпретатор из .venv (обходит необходимость активации)
# Запуск: right-click -> Run with PowerShell или из терминала: .\runserver.ps1
Set-Location -Path $PSScriptRoot
$python = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (Test-Path $python) {
    Write-Host "Использую интерпретатор: $python"
    & $python manage.py runserver 0.0.0.0:8000
} else {
    Write-Error "Не найден интерпретатор: $python. Проверьте, что .venv создана."
}
