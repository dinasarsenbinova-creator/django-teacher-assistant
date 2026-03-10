#!/usr/bin/env python
"""Трассировка выполнения view функции"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User
from django.contrib.sessions.middleware import SessionMiddleware
from teacher.models import Quiz

# Monkey patch для логирования
original_render = __import__('django.shortcuts', fromlist=['render']).render

def logged_render(request, template_name, context=None, *args, **kwargs):
    print(f"\n>>> render() вызвана!")
    print(f"    template_name: {template_name}")
    if context:
        print(f"    context keys: {list(context.keys())}")
        if 'question' in context:
            print(f"    [OK] 'question' ЕСТЬ в context")
        else:
            print(f"    [NO] 'question' НЕТ в context")
    return original_render(request, template_name, context, *args, **kwargs)

__import__('django.shortcuts', fromlist=['render']).render = logged_render

# Также логируем redirect
from django.shortcuts import redirect as original_redirect

def logged_redirect(*args, **kwargs):
    print(f"\n>>> redirect() вызвана!")
    print(f"    args: {args}")
    print(f"    kwargs: {kwargs}")
    return original_redirect(*args, **kwargs)

__import__('django.shortcuts', fromlist=['redirect']).redirect = logged_redirect

# Теперь импортируем view ПОСЛЕ monkey patching
from teacher import views

# Замещаем функцию
views.render = logged_render
views.redirect = logged_redirect

# Запускаем тест
quiz = Quiz.objects.first()
user = User.objects.get(username='teacher')

factory = RequestFactory()
request = factory.get(f'/teacher/quizzes/{quiz.id}/take/')
request.user = user

middleware = SessionMiddleware(lambda x: None)
middleware.process_request(request)
request.session.save()

print("=" * 80)
print("ТРАССИРОВКА ВЫПОЛНЕНИЯ take_quiz()")
print("=" * 80)
print(f"\nВызываю: take_quiz(request, pk={quiz.id})")
print()

response = views.take_quiz(request, pk=quiz.id)

print(f"\n{'='*80}")
print("ЗАВЕРШЕНИЕ")
print(f"{'='*80}")
print(f"\nResponse тип: {type(response)}")
print(f"Response status_code: {response.status_code if hasattr(response, 'status_code') else 'N/A'}")
