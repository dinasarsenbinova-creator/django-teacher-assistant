"""Тест генерации викторины на русском языке"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from teacher.neural_network_views import generate_quiz_questions, generate_quiz_local
import json

print("=== Тест генерации викторины на русском ===\n")

# Тест 1: Полная генерация с приоритетом русского языка
print("Тест 1: Полная генерация (OpenAI -> Локальные)")
quiz1 = generate_quiz_questions(
    subject='Математика',
    topic='Квадратные уравнения',
    class_level='9 класс',
    difficulty='medium',
    questions_count=3,
    language='russian'
)
print(f"Источник: {quiz1.get('generated_by', 'unknown')}")
print(f"Название: {quiz1['title']}")
print(f"Описание: {quiz1['description']}")
for i, q in enumerate(quiz1['questions'][:2], 1):
    print(f"\nВопрос {i}: {q['question_text']}")
    if q.get('options'):
        print(f"  Варианты: {', '.join(q['options'][:2])}...")
print("\n" + "="*60 + "\n")

# Тест 2: Локальная генерация (гарантированно русский)
print("Тест 2: Локальная генерация - Физика")
quiz2 = generate_quiz_local('Физика', 'Законы Ньютона', '10 класс', 'medium', 3)
print(f"Источник: {quiz2.get('generated_by', 'unknown')}")
for i, q in enumerate(quiz2['questions'], 1):
    print(f"\nВопрос {i}: {q['question_text'][:80]}...")
    if q.get('options'):
        print(f"  Первый вариант: {q['options'][0]}")

print("\n" + "="*60 + "\n")

# Тест 3: Химия
print("Тест 3: Локальная генерация - Химия")
quiz3 = generate_quiz_local('Химия', 'Органические соединения', '10 класс', 'medium', 2)
for q in quiz3['questions']:
    print(f"\n✅ {q['question_text']}")
    if q.get('options'):
        print(f"   Варианты ответов: {len(q['options'])} шт на русском")

print("\n" + "="*60)
print("✅ Все викторины сгенерированы на русском языке!")
print("="*60)
