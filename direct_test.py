#!/usr/bin/env python
"""Прямой тест данных викторины"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from teacher.models import Quiz

print("=" * 80)
print("ПРЯМАЯ ПРОВЕРКА ДАННЫХ")
print("=" * 80)

quiz = Quiz.objects.first()
if not quiz:
    print("\n⚠️ Викторины не найдены!")
    exit()

questions = list(quiz.questions.all().order_by('order'))

print(f"\nВикторина: {quiz.title}")
print(f"ID: {quiz.id}")
print(f"Загружено вопросов: {len(questions)}")

if not questions:
    print("\n❌ КРИТИЧЕСКАЯ ПРОБЛЕМА: Нет вопросов!")
    print("\nВозможные причины:")
    print("1. Вопросы не созданы в базе данных")
    print("2. Связь quiz.questions не работает")
    exit()

print("\n✅ Вопросы найдены!")

current_question = questions[0]

print(f"\n{'='*80}")
print("ДАННЫЕ ПЕРВОГО ВОПРОСА (как должны передаваться в шаблон)")
print(f"{'='*80}")

print(f"\ncurrent_question.id = {current_question.id}")
print(f"current_question.question_text = {current_question.question_text}")
print(f"current_question.question_type = {current_question.question_type}")
print(f"current_question.options = {current_question.options}")
print(f"type(current_question.options) = {type(current_question.options)}")

if current_question.options:
    print(f"len(current_question.options) = {len(current_question.options)}")
else:
    print(f"len(current_question.options) = 0 (options пустой!)")

# Создаем debug_info как в view
debug_info = {
    'id': current_question.id,
    'text': current_question.question_text,
    'type': current_question.question_type,
    'options': current_question.options,
    'options_type': str(type(current_question.options)),
    'options_len': len(current_question.options) if current_question.options else 0,
}

print(f"\n{'='*80}")
print("DEBUG_INFO (как передается в шаблон)")
print(f"{'='*80}")

for key, value in debug_info.items():
    print(f"{key}: {value}")

print(f"\n{'='*80}")
print("СИМУЛЯЦИЯ ОТОБРАЖЕНИЯ В ШАБЛОНЕ")
print(f"{'='*80}")

print(f"\nID: {debug_info['id']}")
print(f"Type: {debug_info['type']}")
print(f"Options type: {debug_info['options_type']}")
print(f"Options len: {debug_info['options_len']}")
print(f"Options: {debug_info['options']}")

if debug_info['id'] and debug_info['type']:
    print(f"\n✅ Все данные заполнены корректно!")
else:
    print(f"\n❌ Данные пустые!")

print(f"\n{'='*80}")
print("ПРОВЕРКА УСЛОВИЙ ШАБЛОНА")
print(f"{'='*80}")

is_choice = current_question.question_type in ['single_choice', 'multiple_choice']
has_options = bool(current_question.options)

print(f"\nУсловие 1: question_type in ['single_choice', 'multiple_choice']")
print(f"  Результат: {is_choice}")

print(f"\nУсловие 2: if question.options")
print(f"  Результат: {has_options}")

if is_choice and has_options:
    print(f"\n✅ ОБА условия выполнены - варианты ДОЛЖНЫ отображаться!")
    print(f"\nВарианты:")
    for idx, opt in enumerate(current_question.options):
        print(f"  [{idx}] {opt}")
else:
    print(f"\n❌ Условия НЕ выполнены - варианты НЕ отобразятся!")
    if not is_choice:
        print(f"  Тип вопроса: {current_question.question_type} (не подходит)")
    if not has_options:
        print(f"  options = {current_question.options} (пустой)")
