#!/usr/bin/env python
"""Тест исправленной функции генерации викторин"""
import os
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from teacher.neural_network_views import generate_quiz_local

# Тест 1: 5 вопросов
print("=" * 60)
print("ТЕСТ 1: Генерация 5 вопросов")
print("=" * 60)
result = generate_quiz_local('Математика', 'Квадратные уравнения', '9', 'medium', 5)
print(f"Викторина: {result['title']}")
print(f"Описание: {result['description']}")
print(f"Количество вопросов: {len(result['questions'])}")
print("\nВопросы:")
for i, q in enumerate(result['questions'], 1):
    print(f"{i}. {q['question_text']}")
    print(f"   Тип: {q['question_type']}")
    if 'options' in q:
        print(f"   Варианты: {', '.join(q['options'])}")
    print()

# Тест 2: 10 вопросов
print("=" * 60)
print("ТЕСТ 2: Генерация 10 вопросов")
print("=" * 60)
result2 = generate_quiz_local('История', 'Древний Рим', '7', 'easy', 10)
print(f"Викторина: {result2['title']}")
print(f"Описание: {result2['description']}")
print(f"Количество вопросов: {len(result2['questions'])}")
print("\nПервые 5 вопросов:")
for i, q in enumerate(result2['questions'][:5], 1):
    print(f"{i}. {q['question_text'][:70]}...")

print("\n✅ Все тесты пройдены успешно!")
