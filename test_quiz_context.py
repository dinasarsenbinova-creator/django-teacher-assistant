#!/usr/bin/env python
"""Тестирование прохождения викторины"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from teacher.models import Quiz, QuizQuestion

print("=" * 80)
print("ТЕСТ: Симуляция прохождения викторины")
print("=" * 80)

quiz = Quiz.objects.first()
if not quiz:
    print("\n⚠️ Викторины не найдены!")
    exit()

questions = list(quiz.questions.all().order_by('order'))

print(f"\nВикторина: {quiz.title}")
print(f"Вопросов загружено: {len(questions)}")

if not questions:
    print("\n❌ НЕТ ВОПРОСОВ!")
    exit()

# Берем первый вопрос
current_question = questions[0]

print(f"\n{'='*80}")
print("ТЕКУЩИЙ ВОПРОС (как в контексте шаблона)")
print(f"{'='*80}")
print(f"ID: {current_question.id}")
print(f"Текст: {current_question.question_text}")
print(f"Тип: {current_question.question_type}")
print(f"Варианты (options): {current_question.options}")
print(f"Тип options: {type(current_question.options)}")

# Проверяем условия шаблона
print(f"\n{'='*80}")
print("ПРОВЕРКА УСЛОВИЙ ШАБЛОНА")
print(f"{'='*80}")

is_choice_type = current_question.question_type in ['single_choice', 'multiple_choice']
print(f"\n1. question_type in ['single_choice', 'multiple_choice']: {is_choice_type}")

has_options = bool(current_question.options)
print(f"2. bool(question.options): {has_options}")

if is_choice_type and has_options:
    print(f"\n✅ Условия выполнены! Варианты должны отображаться.")
    print(f"\nВарианты для отображения:")
    for idx, option in enumerate(current_question.options):
        print(f"  [{idx}] {option}")
else:
    print(f"\n❌ Условия НЕ выполнены!")
    if not is_choice_type:
        print(f"  - Тип вопроса: {current_question.question_type}")
    if not has_options:
        print(f"  - options пустой или None")

# Debug info как в шаблоне
print(f"\n{'='*80}")
print("DEBUG INFO (как в шаблоне)")
print(f"{'='*80}")
debug_info = {
    'id': current_question.id,
    'text': current_question.question_text,
    'type': current_question.question_type,
    'options': current_question.options,
    'options_type': str(type(current_question.options)),
    'options_len': len(current_question.options) if current_question.options else 0,
}

for key, value in debug_info.items():
    print(f"{key}: {value}")

print(f"\n{'='*80}")
print("ВЫВОД")
print(f"{'='*80}")

if is_choice_type and has_options and len(current_question.options) > 0:
    print("\n✅ Все проверки пройдены! Вопросы и варианты должны отображаться.")
    print("\nВозможные причины отсутствия на странице:")
    print("1. Проблема с загрузкой страницы в браузере")
    print("2. JavaScript блокирует отображение")
    print("3. CSS скрывает элементы")
    print("4. Кэш браузера показывает старую версию")
    print("\nРекомендации:")
    print("- Очистить кэш браузера (Ctrl+Shift+R)")
    print("- Проверить консоль браузера на ошибки (F12)")
    print("- Проверить исходный код страницы (Ctrl+U)")
else:
    print("\n❌ Есть проблемы с данными!")
