#!/usr/bin/env python
"""Проверка пользователей и их паролей"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.contrib.auth.models import User

print("=" * 80)
print("СПИСОК ПОЛЬЗОВАТЕЛЕЙ")
print("=" * 80)

users = User.objects.all()

if not users:
    print("\n⚠️ Пользователи не найдены!")
else:
    print(f"\nВсего пользователей: {users.count()}\n")
    
    for user in users:
        print(f"Логин: {user.username}")
        print(f"  Email: {user.email}")
        print(f"  Суперпользователь: {'Да' if user.is_superuser else 'Нет'}")
        print(f"  Активен: {'Да' if user.is_active else 'Нет'}")
        print(f"  Дата создания: {user.date_joined}")
        print()

print("=" * 80)
print("СОЗДАНИЕ ТЕСТОВОГО ПОЛЬЗОВАТЕЛЯ")
print("=" * 80)

# Проверяем, существует ли пользователь testuser
test_username = 'testuser'
test_password = 'testpass123'

test_user, created = User.objects.get_or_create(
    username=test_username,
    defaults={
        'email': 'test@test.com',
        'is_staff': True,
    }
)

if created:
    test_user.set_password(test_password)
    test_user.save()
    print(f"\n✅ Создан новый пользователь:")
else:
    # Обновляем пароль на случай если забыли
    test_user.set_password(test_password)
    test_user.save()
    print(f"\n✅ Пользователь уже существует, пароль обновлен:")

print(f"  Логин: {test_username}")
print(f"  Пароль: {test_password}")
print(f"\nИспользуйте эти данные для входа в систему")
