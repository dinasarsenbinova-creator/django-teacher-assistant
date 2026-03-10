#!/usr/bin/env python
"""Критическая диагностика - проверка что передается в шаблон"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User
from django.contrib.sessions.middleware import SessionMiddleware
from teacher.models import Quiz
from teacher.views import take_quiz, take_quiz_student

print("=" * 80)
print("КРИТИЧЕСКАЯ ДИАГНОСТИКА")
print("=" * 80)

# Получаем викторину и пользователя
quiz = Quiz.objects.first()
if not quiz:
    print("\n❌ Викторины не найдены!")
    exit()

user = User.objects.get(username='teacher')
print(f"\nВикторина: {quiz.title} (ID: {quiz.id})")
print(f"Пользователь: {user.username}")
print(f"Вопросов: {quiz.questions.count()}")

# Создаем запрос
factory = RequestFactory()

print(f"\n{'='*80}")
print("ТЕСТ 1: URL /teacher/quizzes/8/take/")
print(f"{'='*80}")

request = factory.get(f'/teacher/quizzes/{quiz.id}/take/')
request.user = user

# Добавляем сессию
middleware = SessionMiddleware(lambda x: None)
middleware.process_request(request)
request.session.save()

try:
    response = take_quiz(request, pk=quiz.id)
    
    print(f"\n✅ Функция take_quiz() вызвана успешно")
    print(f"Response тип: {type(response)}")
    print(f"Response status_code: {response.status_code}")
    
    # Проверяем, это редирект или render?
    if hasattr(response, 'context'):
        print(f"\n✅ Это TemplateResponse (render)")
        context = response.context
        
        print(f"\nКлючи контекста: {list(context.keys())}")
        
        if 'question' in context:
            q = context['question']
            print(f"\n✅ 'question' ЕСТЬ в контексте:")
            print(f"   question.id: {q.id}")
            print(f"   question.question_text: {q.question_text[:50]}...")
            print(f"   question.question_type: {q.question_type}")
            print(f"   question.options: {q.options}")
        else:
            print(f"\n❌ 'question' НЕТ в контексте!")
            print(f"   Доступные ключи: {list(context.keys())}")
        
        if 'debug_info' in context:
            print(f"\n✅ 'debug_info' ЕСТЬ в контексте")
        else:
            print(f"\n❌ 'debug_info' НЕТ в контексте!")
    
    elif response.status_code in [301, 302]:
        print(f"\n⚠️ Это редирект на: {response.url}")
        print(f"Возможные причины:")
        print(f"1. Нет вопросов в викторине")
        print(f"2. Ошибка при обработке запроса")
        print(f"3. Вы прошли викторину полностью (redirect на результаты)")
    else:
        print(f"\n⚠️ Неизвестный тип response: {response}")
        
except Exception as e:
    print(f"\n❌ Ошибка при вызове take_quiz:")
    print(f"   {e}")
    import traceback
    traceback.print_exc()

print(f"\n{'='*80}")
print("ТЕСТ 2: URL /teacher/quizzes/8/student/")
print(f"{'='*80}")

request2 = factory.get(f'/teacher/quizzes/{quiz.id}/student/')
# Не авторизуем для /student/

middleware2 = SessionMiddleware(lambda x: None)
middleware2.process_request(request2)
request2.session.save()

try:
    response2 = take_quiz_student(request2, pk=quiz.id)
    
    print(f"\n✅ Функция take_quiz_student() вызвана успешно")
    print(f"Response тип: {type(response2)}")
    print(f"Response status_code: {response2.status_code}")
    
    if hasattr(response2, 'context'):
        print(f"\n✅ Это TemplateResponse (render)")
        context2 = response2.context
        print(f"Ключи контекста: {list(context2.keys())}")
        
        if 'question' in context2:
            print(f"✅ 'question' ЕСТЬ в контексте")
        else:
            print(f"❌ 'question' НЕТ в контексте!")
    elif response2.status_code in [301, 302]:
        print(f"\n⚠️ Это редирект на: {response2.url}")
    
except Exception as e:
    print(f"\n❌ Ошибка: {e}")

print(f"\n{'='*80}")
print("ПРОВЕРКА СЕССИИ")
print(f"{'='*80}")

# Симулируем первый запрос с GET
print(f"\nПервый запрос (GET) - должен показать первый вопрос:")

request_get = factory.get(f'/teacher/quizzes/{quiz.id}/take/')
request_get.user = user
request_get.method = 'GET'

middleware_get = SessionMiddleware(lambda x: None)
middleware_get.process_request(request_get)
request_get.session.save()

try:
    response_get = take_quiz(request_get, pk=quiz.id)
    
    if hasattr(response_get, 'context'):
        ctx = response_get.context
        if 'question' in ctx:
            print(f"✅ Вопрос есть в контексте")
            print(f"   ID: {ctx['question'].id}")
        else:
            print(f"❌ Вопроса нет!")
    elif response_get.status_code in [301, 302]:
        print(f"⚠️ Редирект: {response_get.url}")
        
except Exception as e:
    print(f"❌ Ошибка: {e}")

print(f"\n{'='*80}")
print("ВЫВОД")
print(f"{'='*80}")
print("""
Если take_quiz() показывает 'question' в контексте, но на странице он пуст,
то проблема в одном из:
1. Неправильный URL (не /take/)
2. Открыт /student/ вместо /take/
3. Вы видите другой шаблон
4. JavaScript удаляет контент
5. CSS скрывает элементы
""")
