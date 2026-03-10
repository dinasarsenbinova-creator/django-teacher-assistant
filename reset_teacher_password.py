#!/usr/bin/env python
"""Установить пароль для пользователя teacher"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.contrib.auth.models import User

username = 'teacher'
new_password = 'teacher123'

try:
    user = User.objects.get(username=username)
    user.set_password(new_password)
    user.save()
    
    print("=" * 80)
    print("ПАРОЛЬ УСПЕШНО ИЗМЕНЕН")
    print("=" * 80)
    print(f"\nПользователь: {username}")
    print(f"Новый пароль: {new_password}")
    print(f"\nТеперь вы можете войти в систему с этими учетными данными")
    print(f"URL для входа: http://localhost:8000/accounts/login/")
    
except User.DoesNotExist:
    print(f"\n⚠️ Пользователь '{username}' не найден!")
    print("Создайте пользователя через:")
    print("  python manage.py createsuperuser")
