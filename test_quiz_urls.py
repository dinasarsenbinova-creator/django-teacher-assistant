#!/usr/bin/env python
"""Проверка URL и доступности викторины"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from teacher.models import Quiz

print("=" * 80)
print("ПРОВЕРКА ДОСТУПНОСТИ СТРАНИЦЫ ВИКТОРИНЫ")
print("=" * 80)

# Получаем викторину
quiz = Quiz.objects.first()
if not quiz:
    print("\n⚠️ Викторины не найдены!")
    exit()

print(f"\nВикторина: {quiz.title}")
print(f"ID: {quiz.id}")
print(f"Вопросов: {quiz.questions.count()}")

# Получаем пользователя
user = User.objects.filter(username='teacher').first()
if not user:
    print("\n⚠️ Пользователь 'teacher' не найден!")
    exit()

print(f"\nПользователь: {user.username}")

# Создаем тестовый клиент
client = Client()

# Авторизуемся
login_success = client.login(username='teacher', password='teacher')
print(f"\nАвторизация: {'✅ Успешно' if login_success else '❌ Неудачно'}")

if not login_success:
    print("Попробуйте другие учетные данные или создайте пользователя")
    exit()

# Тестируем URL'ы
urls_to_test = [
    (f'/teacher/quizzes/{quiz.id}/', 'Детали викторины'),
    (f'/teacher/quizzes/{quiz.id}/take/', 'Прохождение викторины'),
]

print(f"\n{'='*80}")
print("ТЕСТИРОВАНИЕ URL")
print(f"{'='*80}")

for url, description in urls_to_test:
    print(f"\n{description}: {url}")
    try:
        response = client.get(url)
        print(f"  Статус: {response.status_code}")
        
        if response.status_code == 200:
            print(f"  ✅ Страница доступна")
            
            # Проверяем контекст
            if hasattr(response, 'context') and response.context:
                context = response.context
                
                if 'question' in context:
                    question = context['question']
                    print(f"\n  КОНТЕКСТ:")
                    print(f"    question.id: {question.id}")
                    print(f"    question.question_text: {question.question_text[:50]}...")
                    print(f"    question.question_type: {question.question_type}")
                    print(f"    question.options: {question.options}")
                    print(f"    question.options тип: {type(question.options)}")
                    
                    if question.options:
                        print(f"    question.options длина: {len(question.options)}")
                        print(f"    ✅ Варианты передаются в шаблон!")
                    else:
                        print(f"    ❌ Варианты НЕ передаются!")
                
                if 'debug_info' in context:
                    debug_info = context['debug_info']
                    print(f"\n  DEBUG INFO в контексте:")
                    for key, value in debug_info.items():
                        print(f"    {key}: {value}")
            
            # Проверяем содержимое HTML
            content = response.content.decode('utf-8')
            
            if 'DEBUG INFO' in content:
                print(f"\n  ✅ DEBUG блок присутствует в HTML")
                
                # Извлекаем DEBUG блок
                debug_start = content.find('<div style="background: #ffe5e5')
                if debug_start > 0:
                    debug_end = content.find('</div>', debug_start)
                    debug_block = content[debug_start:debug_end+6]
                    
                    print(f"\n  DEBUG блок из HTML:")
                    # Простая очистка HTML тегов для читаемости
                    import re
                    debug_text = re.sub(r'<[^>]+>', ' ', debug_block)
                    debug_text = re.sub(r'\s+', ' ', debug_text).strip()
                    print(f"    {debug_text[:200]}...")
            
            if 'Варианты ответов не заданы' in content:
                print(f"\n  ❌ Найдено сообщение 'Варианты ответов не заданы'")
            
            if 'option-label' in content:
                print(f"  ✅ Найдены элементы вариантов ответа (option-label)")
                
                # Подсчитаем количество вариантов
                option_count = content.count('class="option-label"')
                print(f"    Количество вариантов на странице: {option_count}")
                
        elif response.status_code == 302:
            print(f"  ↪ Перенаправление на: {response.url}")
        else:
            print(f"  ❌ Ошибка")
            
    except Exception as e:
        print(f"  ❌ Исключение: {e}")

print(f"\n{'='*80}")
print("ИТОГ")
print(f"{'='*80}")
print(f"\nДля просмотра страницы в браузере:")
print(f"  http://localhost:8000/teacher/quizzes/{quiz.id}/take/")
print(f"\nУчетные данные для входа:")
print(f"  Логин: teacher")
print(f"  Пароль: teacher (или другой, если был изменен)")
