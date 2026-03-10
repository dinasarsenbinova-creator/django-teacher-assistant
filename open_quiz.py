#!/usr/bin/env python
"""Открыть викторину в браузере"""
import os
import django
import webbrowser
import time

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from teacher.models import Quiz

print("=" * 80)
print("ОТКРЫТИЕ ВИКТОРИНЫ В БРАУЗЕРЕ")
print("=" * 80)

quiz = Quiz.objects.first()
if not quiz:
    print("\n⚠️ Викторины не найдены!")
    exit()

print(f"\nВикторина: {quiz.title}")
print(f"ID: {quiz.id}")
print(f"Вопросов: {quiz.questions.count()}")

# URL для открытия
urls = {
    '1': f'http://localhost:8000/teacher/quizzes/{quiz.id}/',
    '2': f'http://localhost:8000/teacher/quizzes/{quiz.id}/take/',
    '3': f'http://localhost:8000/teacher/quizzes/{quiz.id}/student/',
}

print("\nВыберите страницу для открытия:")
print("1. Детали викторины")
print("2. Прохождение викторины (авторизованный)")
print("3. Прохождение викторины (студент)")
print("4. Открыть все")

choice = input("\nВведите номер (1-4) или нажмите Enter для выбора 2: ").strip() or '2'

if choice == '4':
    print("\nОткрываю все страницы...")
    for url in urls.values():
        print(f"  {url}")
        webbrowser.open(url)
        time.sleep(0.5)
elif choice in urls:
    url = urls[choice]
    print(f"\nОткрываю: {url}")
    webbrowser.open(url)
else:
    print("\n⚠️ Неверный выбор!")
    exit()

print("\n" + "=" * 80)
print("ВАЖНЫЕ ЗАМЕТКИ")
print("=" * 80)
print("\n1. Если вопросы не отображаются - нажмите Ctrl+Shift+R для жесткой перезагрузки")
print("2. Проверьте консоль браузера (F12) на наличие ошибок")
print("3. Учетные данные для входа:")
print("   - Логин: testuser")
print("   - Пароль: testpass123")
print("\n   или")
print("   - Логин: teacher")
print("   - Пароль: (ваш пароль)")
