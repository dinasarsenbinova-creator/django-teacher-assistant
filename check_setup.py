#!/usr/bin/env python
"""
Быстрая проверка установки и конфигурации приложения Ассистент педагога.

Использование: python check_setup.py
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.conf import settings
from django.core.management import call_command
from teacher.models import (
    Curriculum, Topic, Schedule, Lesson, Grade, Test, TestResult
)


def print_header(text):
    """Печать заголовка"""
    print("\n" + "=" * 50)
    print(f"  {text}")
    print("=" * 50)


def check_database():
    """Проверка базы данных"""
    print_header("Проверка базы данных")
    
    models = [
        ('Рабочие программы', Curriculum),
        ('Темы', Topic),
        ('Расписание', Schedule),
        ('Уроки', Lesson),
        ('Оценки', Grade),
        ('Тесты', Test),
        ('Результаты тестов', TestResult),
    ]
    
    total = 0
    for name, model in models:
        count = model.objects.count()
        total += count
        status = "✓" if count > 0 else "○"
        print(f"  {status} {name:<25} {count:>4} записей")
    
    print(f"\n  Всего объектов в БД: {total}")
    return total > 0


def check_users():
    """Проверка пользователей"""
    print_header("Проверка пользователей")
    
    from django.contrib.auth.models import User
    
    users = User.objects.filter(is_active=True)
    if users.count() > 0:
        for user in users[:5]:
            status = "🔓" if user.is_superuser else "👤"
            print(f"  {status} {user.username:<20} {user.get_full_name()}")
        if users.count() > 5:
            print(f"  ... и ещё {users.count() - 5}")
        return True
    else:
        print("  ⚠️  Активные пользователи не найдены!")
        return False


def check_installed_apps():
    """Проверка установленных приложений"""
    print_header("Установленные приложения")
    
    for app in settings.INSTALLED_APPS[:10]:
        if app.startswith('django'):
            symbol = "🔵"
        elif app in ['teacher', 'core']:
            symbol = "🟢"
        else:
            symbol = "🔷"
        print(f"  {symbol} {app}")
    
    if len(settings.INSTALLED_APPS) > 10:
        print(f"  ... и ещё {len(settings.INSTALLED_APPS) - 10}")


def print_usage():
    """Печать инструкций по использованию"""
    print_header("Как начать работу")
    
    print("""
  1. Запустите сервер разработки:
     python manage.py runserver

  2. Откройте в браузере:
     http://localhost:8000/teacher/

  3. Используйте учетные данные:
     Пользователь: teacher
     Пароль: password123

  4. Для администраторского доступа:
     http://localhost:8000/admin/

  5. Доступные функции:
     📚 Управление рабочими программами
     📅 Ведение расписания занятий
     ✏️ Планирование уроков
     📝 Ведение журнала оценок
     📋 Создание и хранение тестов
""")


def main():
    """Главная функция"""
    print("\n")
    print("╔" + "═" * 48 + "╗")
    print("║  Проверка установки Ассистента педагога    ║")
    print("╚" + "═" * 48 + "╝")
    
    # Проверки
    checks = [
        ("База данных", check_database),
        ("Пользователи", check_users),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n  ❌ Ошибка при проверке: {e}")
            results.append((name, False))
    
    check_installed_apps()
    
    # Итоги
    print_header("Итоги проверки")
    
    all_ok = all(result for _, result in results)
    
    for name, result in results:
        status = "✓" if result else "✗"
        print(f"  [{status}] {name}")
    
    if all_ok:
        print("\n  ✓ Все проверки пройдены успешно!")
        print_usage()
    else:
        print("\n  ⚠️  Некоторые проверки не пройдены.")
        print("  Пожалуйста, проверьте конфигурацию.")
    
    print("\n" + "=" * 50 + "\n")


if __name__ == '__main__':
    main()
