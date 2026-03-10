#!/usr/bin/env python
"""Прямая проверка рендеринга шаблона"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.template import Context, Template
from teacher.models import Quiz

print("=" * 80)
print("ПРЯМАЯ ПРОВЕРКА РЕНДЕРИНГА ШАБЛОНА")
print("=" * 80)

quiz = Quiz.objects.first()
if not quiz:
    print("\n⚠️ Викторины не найдены!")
    exit()

questions = list(quiz.questions.all().order_by('order'))
if not questions:
    print("\n⚠️ Вопросы не найдены!")
    exit()

current_question = questions[0]

print(f"\nВикторина: {quiz.title}")
print(f"Вопрос: {current_question.question_text}")
print(f"Тип: {current_question.question_type}")
print(f"Варианты: {current_question.options}")

# Создаем упрощенный шаблон для проверки
template_str = """
{% if question.question_type == 'single_choice' or question.question_type == 'multiple_choice' %}
    TYPE MATCH: YES
    {% if question.options %}
        OPTIONS EXIST: YES
        OPTIONS COUNT: {{ question.options|length }}
        <ul>
        {% for option in question.options %}
            <li>{{ forloop.counter }}. {{ option }}</li>
        {% endfor %}
        </ul>
    {% else %}
        OPTIONS EXIST: NO
    {% endif %}
{% else %}
    TYPE MATCH: NO (got {{ question.question_type }})
{% endif %}
"""

template = Template(template_str)
context = Context({
    'question': current_question
})

rendered = template.render(context)

print(f"\n{'='*80}")
print("РЕЗУЛЬТАТ РЕНДЕРИНГА")
print(f"{'='*80}")
print(rendered)

print(f"\n{'='*80}")
print("ВЫВОД")
print(f"{'='*80}")

if 'OPTIONS EXIST: YES' in rendered and '<li>' in rendered:
    print("\n✅ Шаблон рендерится правильно!")
    print("Варианты ответов отображаются в HTML.")
    print("\nВозможные причины проблемы:")
    print("1. Кэш браузера - попробуйте Ctrl+Shift+R")
    print("2. Проблема с JavaScript - проверьте консоль (F12)")
    print("3. Другой вопрос без вариантов показывается первым")
else:
    print("\n❌ Проблема с рендерингом шаблона!")
    print("Шаблон не может правильно обработать данные вопроса.")
