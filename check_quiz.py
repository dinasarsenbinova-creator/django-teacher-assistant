#!/usr/bin/env python
"""Проверка викторин и их вопросов"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from teacher.models import Quiz, QuizQuestion

print("=" * 60)
print("Проверка викторин")
print("=" * 60)

quizzes = Quiz.objects.all()
print(f"\nВсего викторин: {quizzes.count()}")

for quiz in quizzes:
    print(f"\n📝 Викторина: {quiz.title}")
    print(f"   ID: {quiz.id}")
    print(f"   Учитель: {quiz.teacher.username}")
    
    questions = quiz.questions.all().order_by('order')
    print(f"   Количество вопросов: {questions.count()}")
    
    if questions.count() == 0:
        print(f"   ⚠️ НЕТ ВОПРОСОВ!")
    else:
        for i, q in enumerate(questions, 1):
            print(f"\n   Вопрос {i}:")
            print(f"      ID: {q.id}")
            print(f"      Текст: {q.question_text[:50]}...")
            print(f"      Тип: {q.question_type}")
            print(f"      Варианты: {q.options}")
            print(f"      Правильный ответ: {q.correct_answer}")
            print(f"      Порядок: {q.order}")

print("\n" + "=" * 60)

# Найдем викторину "Лучший процессор"
processor_quiz = Quiz.objects.filter(title__icontains="процессор").first()
if processor_quiz:
    print(f"\n🔍 Найдена викторина про процессор: {processor_quiz.title}")
    print(f"   Вопросов: {processor_quiz.questions.count()}")
    
    if processor_quiz.questions.count() == 0:
        print("\n⚠️ ПРОБЛЕМА: В викторине нет вопросов!")
        print("Нужно создать вопросы через админку или генератор.")
else:
    print("\n⚠️ Викторина про процессор не найдена!")
