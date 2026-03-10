#!/usr/bin/env python
"""Тест view функции take_quiz"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.test import RequestFactory, Client
from django.contrib.auth.models import User, AnonymousUser
from django.contrib.sessions.middleware import SessionMiddleware
from teacher.models import Quiz
from teacher.views import take_quiz

print("=" * 80)
print("ТЕСТ VIEW ФУНКЦИИ take_quiz")
print("=" * 80)

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

print(f"Пользователь: {user.username}")

# Тест через RequestFactory
print("\n" + "=" * 80)
print("ТЕСТ 1: RequestFactory")
print("=" * 80)

factory = RequestFactory()
request = factory.get(f'/teacher/quizzes/{quiz.id}/take/')
request.user = user

# Добавляем сессию
middleware = SessionMiddleware(lambda x: None)
middleware.process_request(request)
request.session.save()

try:
    response = take_quiz(request, pk=quiz.id)
    print(f"\nResponse status: {response.status_code}")
    
    if hasattr(response, 'context_data'):
        context = response.context_data
        print(f"\nКонтекст найден!")
        
        if 'question' in context:
            q = context['question']
            print(f"\n✅ question в контексте:")
            print(f"   ID: {q.id}")
            print(f"   Text: {q.question_text[:50]}...")
            print(f"   Type: {q.question_type}")
            print(f"   Options: {q.options}")
        else:
            print(f"\n❌ question НЕТ в контексте!")
            
        if 'debug_info' in context:
            debug = context['debug_info']
            print(f"\n✅ debug_info в контексте:")
            for key, val in debug.items():
                print(f"   {key}: {val}")
        else:
            print(f"\n❌ debug_info НЕТ в контексте!")
    else:
        print("\n⚠️ context_data недоступен")
        
except Exception as e:
    print(f"\n❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()

# Тест через Client
print("\n" + "=" * 80)
print("ТЕСТ 2: Django Test Client")
print("=" * 80)

client = Client()
login_ok = client.login(username='teacher', password='teacher123')
print(f"Авторизация: {'✅ OK' if login_ok else '❌ FAILED'}")

if login_ok:
    response = client.get(f'/teacher/quizzes/{quiz.id}/take/')
    print(f"Response status: {response.status_code}")
    
    if response.status_code == 200:
        # Проверяем контекст
        if hasattr(response, 'context'):
            context = response.context
            
            print(f"\n✅ Контекст доступен!")
            print(f"Ключи контекста: {list(context.keys())}")
            
            if 'question' in context:
                q = context['question']
                print(f"\n✅ question в контексте:")
                print(f"   ID: {q.id}")
                print(f"   Text: {q.question_text[:50]}...")
                print(f"   Type: {q.question_type}")
                print(f"   Options: {q.options}")
                print(f"   Options type: {type(q.options)}")
            else:
                print(f"\n❌ question НЕТ в контексте!")
                print(f"   Доступные ключи: {list(context.keys())}")
            
            if 'debug_info' in context:
                debug = context['debug_info']
                print(f"\n✅ debug_info в контексте:")
                for key, val in debug.items():
                    print(f"   {key}: {val}")
            else:
                print(f"\n❌ debug_info НЕТ в контексте!")
        else:
            print(f"\n❌ Контекст недоступен!")
        
        # Проверяем HTML
        content = response.content.decode('utf-8')
        
        if 'DEBUG INFO:' in content:
            print(f"\n✅ DEBUG INFO найден в HTML")
            
            # Ищем значения
            import re
            id_match = re.search(r'ID:\s*(\d+)', content)
            type_match = re.search(r'Type:\s*(\w+)', content)
            
            if id_match:
                print(f"   ID в HTML: {id_match.group(1)}")
            else:
                print(f"   ❌ ID пустой в HTML")
                
            if type_match:
                print(f"   Type в HTML: {type_match.group(1)}")
            else:
                print(f"   ❌ Type пустой в HTML")
        else:
            print(f"\n❌ DEBUG INFO не найден в HTML")
    else:
        print(f"\n⚠️ Неожиданный статус: {response.status_code}")
        if response.status_code == 302:
            print(f"   Перенаправление на: {response.url}")

print("\n" + "=" * 80)
print("ВЫВОД")
print("=" * 80)
print("\nЕсли тесты показывают, что данные есть в контексте, но DEBUG INFO пустой,")
print("то проблема в шаблоне или в том, как браузер отображает страницу.")
