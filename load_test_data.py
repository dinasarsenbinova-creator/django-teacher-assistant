#!/usr/bin/env python
"""
Скрипт для создания тестовых данных в приложении Teacher.
Используется для демонстрации функций системы.

Использование: python load_test_data.py
"""

import os
import django
from datetime import datetime, timedelta, time

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.contrib.auth.models import User
from teacher.models import (
    Curriculum, Topic, Schedule, Lesson, Grade, Test, TestResult, Subject, StudentGroup
)


def clear_data():
    """Удаление всех тестовых данных"""
    print("Удаление старых данных...")
    Curriculum.objects.all().delete()
    Topic.objects.all().delete()
    Schedule.objects.all().delete()
    Lesson.objects.all().delete()
    Grade.objects.all().delete()
    Test.objects.all().delete()
    TestResult.objects.all().delete()
    Subject.objects.filter(name='Математика').delete()
    StudentGroup.objects.filter(name__in=['5 А', '5 Б']).delete()
    print("✓ Старые данные удалены")


def create_test_data():
    """Создание тестовых данных"""
    
    # Получаем или создаем пользователя-педагога
    teacher, created = User.objects.get_or_create(
        username='teacher',
        defaults={
            'first_name': 'Иван',
            'last_name': 'Петров',
            'email': 'teacher@example.com',
            'is_staff': False
        }
    )
    if created:
        teacher.set_password('password123')
        teacher.save()
        print(f"✓ Создан пользователь: {teacher.get_full_name()} (teacher)")
    else:
        print(f"✓ Найден пользователь: {teacher.get_full_name()}")

    # Создание или получение предмета
    subject, created = Subject.objects.get_or_create(
        name='Математика',
        defaults={
            'description': 'Предмет математика',
            'created_by': teacher
        }
    )
    if created:
        print(f"✓ Создан предмет: {subject.name}")
    else:
        print(f"✓ Найден предмет: {subject.name}")

    # Создание рабочей программы
    curriculum, created = Curriculum.objects.get_or_create(
        title='Математика 5 класс',
        defaults={
            'subject': subject,
            'class_level': '5',
            'year': 2025
        }
    )
    if created:
        print(f"✓ Создана рабочая программа: {curriculum.title}")
    
    # Создание тем
    topics_data = [
        ('Натуральные числа', 'Введение в натуральные числа', 8),
        ('Сложение и вычитание', 'Операции со натуральными числами', 10),
        ('Умножение и деление', 'Умножение и деление натуральных чисел', 12),
        ('Дроби', 'Введение в обыкновенные дроби', 10),
    ]
    
    topics = []
    for i, (title, desc, hours) in enumerate(topics_data, 1):
        topic, created = Topic.objects.get_or_create(
            curriculum=curriculum,
            title=title,
            defaults={
                'description': desc,
                'order': i,
                'hours': hours
            }
        )
        topics.append(topic)
        if created:
            print(f"  ✓ Тема: {title} ({hours} часов)")

    # Создание групп студентов
    groups_data = ['5 А', '5 Б']
    groups = {}
    for group_name in groups_data:
        group, created = StudentGroup.objects.get_or_create(
            name=group_name,
            defaults={
                'year': 2024,
                'students': '',
                'created_by': teacher
            }
        )
        groups[group_name] = group
        if created:
            print(f"  ✓ Группа: {group_name}")

    # Создание расписания
    schedule_data = [
        ('Математика', '5 А', 0, time(9, 0), time(9, 45), '301'),  # Понедельник
        ('Математика', '5 А', 2, time(11, 0), time(11, 45), '301'),  # Среда
        ('Математика', '5 А', 4, time(10, 0), time(10, 45), '301'),  # Пятница
        ('Математика', '5 Б', 1, time(10, 0), time(10, 45), '302'),  # Вторник
        ('Математика', '5 Б', 3, time(9, 0), time(9, 45), '302'),  # Четверг
    ]
    
    for subject_name, class_name, day, start, end, room in schedule_data:
        schedule, created = Schedule.objects.get_or_create(
            teacher=teacher,
            subject=subject,
            class_name=groups[class_name],
            day_of_week=day,
            defaults={
                'start_time': start,
                'end_time': end,
                'room': room
            }
        )
        if created:
            print(f"  ✓ Расписание: {class_name} в {start.strftime('%H:%M')} ({room})")

    # Создание планов уроков
    today = datetime.today().date()
    lesson_data = [
        ('Понятие натурального числа', today, '5 А', 'Введение в натуральные числа', topics[0]),
        ('Сравнение натуральных чисел', today + timedelta(days=2), '5 А', 'Сравнение чисел', topics[0]),
        ('Сложение натуральных чисел', today + timedelta(days=4), '5 А', 'Основные операции', topics[1]),
        ('Умножение натуральных чисел', today + timedelta(days=6), '5 А', 'Умножение', topics[2]),
    ]
    
    for title, date, class_name, content, topic in lesson_data:
        lesson, created = Lesson.objects.get_or_create(
            teacher=teacher,
            title=title,
            date=date,
            defaults={
                'curriculum': curriculum,
                'class_name': groups[class_name],
                'subject': subject,
                'topic': topic,
                'objectives': f'Цель: {title}',
                'content': content,
                'materials': 'Учебник, доска, карточки',
                'homework': 'Параграф с примерами'
            }
        )
        if created:
            print(f"  ✓ Урок: {title} ({date})")

    # Создание оценок
    students = [
        'Александров Иван',
        'Белова Мария', 
        'Волков Петр',
        'Гаврилов Сергей',
        'Данилов Алексей'
    ]
    
    for student in students:
        for i in range(3):
            grade, created = Grade.objects.get_or_create(
                teacher=teacher,
                student_name=student,
                class_name=groups['5 А'],
                subject=subject,
                curriculum=curriculum,
                date=today - timedelta(days=i),
                grade_type=['homework', 'classwork', 'test'][i],
                defaults={
                    'grade': 3 + (hash(student + str(i)) % 3),
                    'comment': 'Хорошая работа' if hash(student) % 2 == 0 else ''
                }
            )
    print(f"  ✓ Добавлены оценки для {len(students)} учеников")

    # Создание тестов
    test_data = [
        ('Тест: Натуральные числа', 'test', 'Проверка знаний натуральных чисел', topics[0], 50, 45),
        ('Контрольная: Сложение и вычитание', 'control_work', 'Проверка сложения и вычитания', topics[1], 100, 45),
        ('Тест: Умножение', 'test', 'Проверка умножения', topics[2], 50, 30),
    ]
    
    for title, test_type, desc, topic, max_score, duration in test_data:
        test, created = Test.objects.get_or_create(
            teacher=teacher,
            title=title,
            defaults={
                'curriculum': curriculum,
                'topic': topic,
                'test_type': test_type,
                'subject': subject,
                'class_name': groups['5 А'],
                'description': desc,
                'content': '''1. Сколько натуральных чисел от 1 до 10?
2. Какой результат 5 + 3?
3. Найти x: x + 2 = 7
4. Вычислить 12 - 5
5. Сколько будет 3 × 4?''',
                'answer_key': '''1. Десять
2. 8
3. 5
4. 7
5. 12''',
                'max_score': max_score,
                'duration_minutes': duration
            }
        )
        if created:
            print(f"  ✓ Тест: {title}")
            
            # Добавление результатов тестов
            for j, student in enumerate(students[:3]):
                score = max_score - (j * 10)
                TestResult.objects.create(
                    test=test,
                    student_name=student,
                    score=score,
                )


if __name__ == '__main__':
    print("\n" + "="*50)
    print("Загрузка тестовых данных для Ассистента педагога")
    print("="*50 + "\n")
    
    clear_data()
    create_test_data()
    
    print("\n" + "="*50)
    print("✓ Все тестовые данные успешно созданы!")
    print("\nДоступ к приложению:")
    print("  URL: http://localhost:8000/teacher/")
    print("  Пользователь: teacher")
    print("  Пароль: password123")
    print("="*50 + "\n")
