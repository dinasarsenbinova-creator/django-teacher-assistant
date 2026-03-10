#!/usr/bin/env python
"""Скрипт для исправления функции generate_quiz_local"""
import sys

# Новая функция
NEW_FUNCTION = r'''def generate_quiz_local(subject, topic, class_level, difficulty, questions_count):
    """Локальная генерация викторины на основе шаблонов"""
    import random
    
    # Базовые шаблоны вопросов
    templates = {
        'math': {
            'multiple_choice': [
                {'question_text': f'Какое решение уравнения по теме "{topic}"?', 'options': ['x=2', 'x=-3', 'x=0', 'x=5'], 'correct_answer': 0, 'explanation': 'Правильное решение.'},
                {'question_text': f'Какой объект в теме "{topic}"?', 'options': ['Круг', 'Квадрат', 'Треугольник', 'Прямоугольник'], 'correct_answer': 2, 'explanation': 'Основной объект.'},
                {'question_text': f'Какая формула для "{topic}"?', 'options': ['a²+b²', 'πr²', '(a+b)²', 'ab'], 'correct_answer': 1, 'explanation': 'Основная формула.'},
                {'question_text': f'Какое свойство чисел в "{topic}"?', 'options': ['Коммутативность', 'Ассоциативность', 'Дистрибутивность', 'Транзитивность'], 'correct_answer': 0, 'explanation': 'Важное свойство.'},
                {'question_text': f'Сколько решений в "{topic}"?', 'options': ['Одно', 'Два', 'Три', 'Бесконечно'], 'correct_answer': 1, 'explanation': 'Обычно два.'},
                {'question_text': f'Какой метод решения в "{topic}"?', 'options': ['Подстановка', 'Сложение', 'Графический', 'Факторизация'], 'correct_answer': 3, 'explanation': 'Эффективный метод.'}
            ],
            'true_false': [
                {'question_text': f'Верно ли, что в "{topic}" изучаются операции?', 'correct_answer': True, 'explanation': 'Да, изучаются.'},
                {'question_text': f'Верно ли, что все числа положительные в "{topic}"?', 'correct_answer': False, 'explanation': 'Нет, не все.'},
                {'question_text': f'Верно ли, что "{topic}" связана с алгеброй?', 'correct_answer': True, 'explanation': 'Да, связана.'},
                {'question_text': f'Верно ли, что дроби не используются в "{topic}"?', 'correct_answer': False, 'explanation': 'Используются.'}
            ],
            'short_answer': [
                {'question_text': f'Назовите формулу из "{topic}".', 'correct_answer': 'Формула темы', 'explanation': 'Основная формула.'},
                {'question_text': f'Какое действие главное в "{topic}"?', 'correct_answer': 'Зависит от задачи', 'explanation': 'Разные операции.'}
            ]
        },
        'default': {
            'multiple_choice': [
                {'question_text': f'Что основное в "{topic}"?', 'options': ['Определение', 'Классификация', 'Применение', 'История'], 'correct_answer': 0, 'explanation': 'Основа темы.'},
                {'question_text': f'Какой аспект важен в "{topic}"?', 'options': ['Теория', 'Практика', 'История', 'Комплексный'], 'correct_answer': 3, 'explanation': 'Комплексный подход.'},
                {'question_text': f'Как "{topic}" связана с другими?', 'options': ['Напрямую', 'Косвенно', 'Не связана', 'Зависит'], 'correct_answer': 3, 'explanation': 'Зависит от контекста.'},
                {'question_text': f'Какой метод для "{topic}"?', 'options': ['Анализ', 'Практика', 'Группа', 'Все методы'], 'correct_answer': 3, 'explanation': 'Все методы хороши.'}
            ],
            'true_false': [
                {'question_text': f'Важна ли "{topic}"?', 'correct_answer': True, 'explanation': 'Да, важна.'},
                {'question_text': f'Есть ли применение у "{topic}"?', 'correct_answer': True, 'explanation': 'Да, есть.'},
                {'question_text': f'Нельзя изучить "{topic}" самостоятельно?', 'correct_answer': False, 'explanation': 'Можно изучить.'},
                {'question_text': f'Связана ли "{topic}" с технологиями?', 'correct_answer': True, 'explanation': 'Да, связана.'}
            ],
            'short_answer': [
                {'question_text': f'Дайте определение из "{topic}".', 'correct_answer': 'Определение термина', 'explanation': 'Ключевой термин.'},
                {'question_text': f'Опишите идею "{topic}".', 'correct_answer': 'Главная идея', 'explanation': 'Центральная идея.'}
            ]
        }
    }
    
    subject_key = (subject or '').lower()
    if 'матем' in subject_key or 'алгебр' in subject_key or 'геометр' in subject_key:
        subject_key = 'math'
    elif 'физ' in subject_key or 'хим' in subject_key:
        subject_key = 'math'
    else:
        subject_key = 'default'
    
    subject_templates = templates.get(subject_key, templates['default'])
    
    questions = []
    question_types = ['multiple_choice', 'true_false', 'short_answer']
    
    for i in range(questions_count):
        q_type = question_types[i % len(question_types)]
        if q_type in subject_templates:
            type_templates = subject_templates[q_type]
            template_index = (i // len(question_types)) % len(type_templates)
            template = type_templates[template_index].copy()
            template['question_type'] = q_type
            template['points'] = 1
            questions.append(template)
    
    return {
        'title': f'Викторина: {topic}',
        'description': f'Локально сгенерированная викторина по теме "{topic}" ({questions_count} вопросов)',
        'questions': questions,
        'generated_by': 'local'
    }'''

def main():
    # Читаем файл
    with open('teacher/neural_network_views.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Находим начало функции
    start_marker = 'def generate_quiz_local(subject, topic, class_level, difficulty, questions_count):'
    start_idx = content.find(start_marker)
    
    if start_idx == -1:
        print('ERROR: Function not found')
        return 1
    
    # Находим конец функции
    end_search = content.find('\n\ndef ', start_idx + 1)
    if end_search == -1:
        end_search = content.find('\n\nclass ', start_idx + 1)
    if end_search == -1:
        end_search = len(content)
    
    # Заменяем функцию
    new_content = content[:start_idx] + NEW_FUNCTION + content[end_search:]
    
    # Сохраняем
    with open('teacher/neural_network_views.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print('✅ Функция generate_quiz_local успешно обновлена!')
    print('✅ Теперь генератор создаёт разнообразные вопросы')
    return 0

if __name__ == '__main__':
    sys.exit(main())
