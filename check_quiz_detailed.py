#!/usr/bin/env python
"""Детальная проверка вопросов викторины"""
import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from teacher.models import Quiz, QuizQuestion

print("=" * 80)
print("ДЕТАЛЬНАЯ ПРОВЕРКА ВОПРОСОВ ВИКТОРИНЫ")
print("=" * 80)

quiz = Quiz.objects.first()
if not quiz:
    print("\n⚠️ Викторины не найдены!")
    exit()

print(f"\nВикторина: {quiz.title}")
print(f"ID: {quiz.id}")

questions = quiz.questions.all().order_by('order')
print(f"\nВопросов: {questions.count()}")

if questions.count() == 0:
    print("\n❌ ПРОБЛЕМА: Нет вопросов!")
else:
    print("\n✅ Вопросы найдены!\n")
    
    for i, q in enumerate(questions[:3], 1):  # Проверяем первые 3 вопроса
        print(f"\n{'='*60}")
        print(f"Вопрос {i}")
        print(f"{'='*60}")
        print(f"ID: {q.id}")
        print(f"Текст: {q.question_text}")
        print(f"Тип: {q.question_type}")
        print(f"Порядок: {q.order}")
        print(f"\nВарианты (options):")
        print(f"  Тип: {type(q.options)}")
        print(f"  Значение: {q.options}")
        if q.options:
            print(f"  Длина: {len(q.options)}")
            print(f"  JSON-строка: {json.dumps(q.options, ensure_ascii=False)}")
        else:
            print(f"  ❌ ПУСТО!")
        
        print(f"\nПравильный ответ (correct_answer):")
        print(f"  Тип: {type(q.correct_answer)}")
        print(f"  Значение: {q.correct_answer}")
        
        print(f"\nБаллы: {q.points}")
        print(f"Пояснение: {q.explanation[:50] if q.explanation else 'Нет'}")

print("\n" + "=" * 80)
print("\nПРОВЕРКА ОТОБРАЖЕНИЯ В ШАБЛОНЕ:")
print("=" * 80)

first_q = questions.first()
if first_q:
    print(f"\nПервый вопрос:")
    print(f"question_type: {first_q.question_type}")
    
    if first_q.question_type in ['single_choice', 'multiple_choice']:
        if first_q.options:
            print(f"\n✅ options существует и содержит {len(first_q.options)} вариантов:")
            for idx, opt in enumerate(first_q.options):
                print(f"  [{idx}] {opt}")
        else:
            print(f"\n❌ options пустой!")
            print(f"  Значение: {first_q.options}")
            print(f"  Тип: {type(first_q.options)}")
    
    print(f"\nСимуляция шаблона:")
    print("{% if question.question_type == 'single_choice' or question.question_type == 'multiple_choice' %}")
    print(f"  Результат: {first_q.question_type in ['single_choice', 'multiple_choice']}")
    print("  {% if question.options %}")
    print(f"    Результат: {bool(first_q.options)}")
    
    if first_q.options:
        print("    {% for option in question.options %}")
        for idx, opt in enumerate(first_q.options):
            print(f"      Итерация {idx}: {opt}")
        print("    {% endfor %}")
    else:
        print(f"    ❌ Цикл не выполнится, options пустой!")
