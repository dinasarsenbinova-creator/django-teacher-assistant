#!/usr/bin/env python
"""Проверка содержимого HTML ответа"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User
from django.contrib.sessions.middleware import SessionMiddleware
from teacher.models import Quiz
from teacher.views import take_quiz

quiz = Quiz.objects.first()
user = User.objects.get(username='teacher')

factory = RequestFactory()
request = factory.get(f'/teacher/quizzes/{quiz.id}/take/')
request.user = user

middleware = SessionMiddleware(lambda x: None)
middleware.process_request(request)
request.session.save()

response = take_quiz(request, pk=quiz.id)

# Получаем содержимое HTML
content = response.content.decode('utf-8')

print("=" * 80)
print("АНАЛИЗ HTML ОТВЕТА")
print("=" * 80)

# Проверяем наличие ключевых элементов
checks = [
    ('DEBUG INFO блок', '<div style="background: #ffe5e5'),
    ('question exists: YES', 'question exists: YES'),
    ('question.id:', 'question.id:'),
    ('question.question_text:', 'question.question_text:'),
    ('question.question_type:', 'question.question_type:'),
    ('question.options:', 'question.options:'),
    ('Вопрос заголовок (h3)', '<h3 style="margin:0 0 1rem 0'),
    ('Текст вопроса (question_card)', '<div class="question-card"'),
    ('Варианты ответов (option-label)', 'class="option-label"'),
    ('DEBUG INFO "debug_info exists"', 'debug_info exists:'),
]

print(f"\nДлина HTML: {len(content)} символов")
print(f"\nПроверка элементов:")

for check_name, pattern in checks:
    found = pattern in content
    symbol = "[OK]" if found else "[NO]"
    print(f"{symbol} {check_name}")
    if found and 'DEBUG' in check_name:
        # Найдем эту строку в контексте
        idx = content.find(pattern)
        snippet = content[max(0, idx-50):min(len(content), idx+150)]
        print(f"   Контекст: ...{snippet.strip()}...")

print(f"\n{'='*80}")
print("ПОИСК DEBUG БЛОКА")
print(f"{'='*80}")

debug_start = content.find('<div style="background: #ffe5e5')
if debug_start > 0:
    debug_end = content.find('</div>', debug_start) + 6
    debug_block = content[debug_start:debug_end]
    
    # Убираем HTML теги для читаемости
    import re
    text = re.sub(r'<[^>]+>', '\n', debug_block)
    text = re.sub(r'\s+', ' ', text).strip()
    
    print(f"\n✅ DEBUG блок найден!")
    print(f"\nСодержимое (первые 500 символов):")
    print(text[:500])
else:
    print(f"\n❌ DEBUG блок НЕ найден!")

print(f"\n{'='*80}")
print("ПОИСК ФОРМЫ ВОПРОСА")
print(f"{'='*80}")

form_start = content.find('<form method="post" id="quizForm">')
if form_start > 0:
    form_end = content.find('</form>', form_start) + 7
    form_content = content[form_start:form_end]
    
    print(f"\n✅ Форма найдена!")
    print(f"Длина формы: {len(form_content)} символов")
    
    # Проверяем наличие элементов формы
    if 'question_card' in form_content:
        print(f"✅ question_card найден")
    else:
        print(f"❌ question_card НЕ найден")
    
    if 'option-label' in form_content:
        option_count = form_content.count('option-label')
        print(f"✅ option-label найдено {option_count} раз")
    else:
        print(f"❌ option-label НЕ найдено")
        
    if 'name="question_' in form_content:
        print(f"✅ Инпуты вопросов найдены")
    else:
        print(f"❌ Инпуты вопросов НЕ найдены")
else:
    print(f"\n❌ Форма НЕ найдена!")

print(f"\n{'='*80}")
print("ПРОВЕРКА JAVASCRIPT")
print(f"{'='*80}")

if '<script>' in content:
    script_count = content.count('<script>')
    print(f"✅ Найдено {script_count} блоков JavaScript")
else:
    print(f"⚠️ JavaScript не найден")

# Проверяем наличие ошибок в HTML
if 'undefined' in content.lower():
    print(f"⚠️ Найдено 'undefined' в HTML - возможна ошибка JavaScript")

print(f"\n{'='*80}")
print("ВЫВОД")
print(f"{'='*80}")

if 'question exists: YES' in content:
    print(f"\n✅ 'question exists: YES' - данные передаются в шаблон!")
    if 'question.options:' in content:
        print(f"✅ Поле options есть в HTML")
    else:
        print(f"❌ Поля options нет в HTML - проблема в шаблоне")
elif 'question exists: NO' in content:
    print(f"\n❌ 'question exists: NO' - данные НЕ передаются в шаблон")
    print(f"Это может быть:")
    print(f"1. Ошибка в view функции")
    print(f"2. Проблема с сессией")
    print(f"3. Редирект вместо render")
else:
    print(f"\n⚠️ DEBUG блок вообще не рендерится")
    print(f"Это может означать, что используется другой шаблон")

# Сохраняем HTML в файл для анализа
with open('quiz_take_debug.html', 'w', encoding='utf-8') as f:
    f.write(content)
print(f"\n💾 HTML сохранен в: quiz_take_debug.html")
