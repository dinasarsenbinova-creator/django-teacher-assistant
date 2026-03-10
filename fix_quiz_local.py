"""
Патч для исправления функции generate_quiz_local
Добавляет больше разнообразных вопросов и улучшает логику генерации
"""

# Найти строку в файле teacher/neural_network_views.py начиная с:
# def generate_quiz_local(subject, topic, class_level, difficulty, questions_count):

# И заменить всю функцию на следующий код:

NEW_FUNCTION = """
def generate_quiz_local(subject, topic, class_level, difficulty, questions_count):
    '''Локальная генерация викторины на основе шаблонов'''
    import random
    
    # Базовые шаблоны вопросов для разных предметов
    templates = {
        'math': {
            'multiple_choice': [
                {
                    'question_text': f'Какое из следующих выражений является решением уравнения по теме "{topic}"?',
                    'options': ['x = 2', 'x = -3', 'x = 0', 'x = 5'],
                    'correct_answer': 0,
                    'explanation': 'Это правильное решение согласно правилам математики.'
                },
                {
                    'question_text': f'Какой геометрический объект изучается в теме "{topic}"?',
                    'options': ['Круг', 'Квадрат', 'Треугольник', 'Прямоугольник'],
                    'correct_answer': 2,
                    'explanation': 'Треугольник является основным объектом изучения в этой теме.'
                },
                {
                    'question_text': f'Какая формула используется для вычисления в теме "{topic}"?',
                    'options': ['a² + b²', 'πr²', '(a+b)²', 'a·b'],
                    'correct_answer': 1,
                    'explanation': 'Эта формула является основной для данного типа задач.'
                },
                {
                    'question_text': f'Какое свойство чисел применяется в теме "{topic}"?',
                    'options': ['Коммутативность', 'Ассоциативность', 'Дистрибутивность', 'Транзитивность'],
                    'correct_answer': 0,
                    'explanation': 'Коммутативность - важное свойство для этой темы.'
                },
                {
                    'question_text': f'Сколько решений имеет типичное уравнение в теме "{topic}"?',
                    'options': ['Одно', 'Два', 'Три', 'Бесконечно много'],
                    'correct_answer': 1,
                    'explanation': 'Обычно такие уравнения имеют два решения.'
                },
                {
                    'question_text': f'Какой метод решения используется в теме "{topic}"?',
                    'options': ['Подстановка', 'Сложение', 'Графический', 'Факторизация'],
                    'correct_answer': 3,
                    'explanation': 'Факторизация - эффективный метод для этого типа задач.'
                }
            ],
            'true_false': [
                {
                    'question_text': f'Верно ли, что в теме "{topic}" изучаются основные математические операции?',
                    'correct_answer': True,
                    'explanation': 'Да, тема включает изучение основных операций.'
                },
                {
                    'question_text': f'Верно ли, что все числа в теме "{topic}" являются положительными?',
                    'correct_answer': False,
                    'explanation': 'В математике изучаются как положительные, так и отрицательные числа.'
                },
                {
                    'question_text': f'Верно ли, что тема "{topic}" связана с алгеброй?',
                    'correct_answer': True,
                    'explanation': 'Эта тема является частью алгебры.'
                },
                {
                    'question_text': f'Верно ли, что в теме "{topic}" не используются дроби?',
                    'correct_answer': False,
                    'explanation': 'Дроби часто используются в математических расчетах.'
                }
            ],
            'short_answer': [
                {
                    'question_text': f'Назовите основную формулу, изучаемую в теме "{topic}".',
                    'correct_answer': 'Формула зависит от конкретной темы',
                    'explanation': 'Это основная формула данной темы.'
                },
                {
                    'question_text': f'Какое математическое действие является главным в теме "{topic}"?',
                    'correct_answer': 'Зависит от типа задачи',
                    'explanation': 'Разные задачи требуют разных операций.'
                }
            ]
        },
        'default': {
            'multiple_choice': [
                {
                    'question_text': f'Что является основным понятием в теме "{topic}"?',
                    'options': ['Определение', 'Классификация', 'Применение', 'История'],
                    'correct_answer': 0,
                    'explanation': 'Определение - основа понимания темы.'
                },
                {
                    'question_text': f'Какой аспект темы "{topic}" наиболее важен?',
                    'options': ['Теоретический', 'Практический', 'Исторический', 'Комплексный'],
                    'correct_answer': 3,
                    'explanation': 'Комплексный подход важен для понимания.'
                },
                {
                    'question_text': f'Как тема "{topic}" связана с другими областями?',
                    'options': ['Напрямую', 'Косвенно', 'Не связана', 'Зависит от контекста'],
                    'correct_answer': 3,
                    'explanation': 'Связь зависит от контекста.'
                },
                {
                    'question_text': f'Какой метод изучения эффективен для темы "{topic}"?',
                    'options': ['Анализ', 'Практика', 'Группа', 'Все методы'],
                    'correct_answer': 3,
                    'explanation': 'Комбинация методов эффективна.'
                }
            ],
            'true_false': [
                {
                    'question_text': f'Верно ли, что тема "{topic}" важна для предмета?',
                    'correct_answer': True,
                    'explanation': 'Все темы важны для понимания.'
                },
                {
                    'question_text': f'Верно ли, что тема "{topic}" имеет практическое применение?',
                    'correct_answer': True,
                    'explanation': 'Большинство тем имеют применение.'
                },
                {
                    'question_text': f'Верно ли, что тему "{topic}" нельзя изучить самостоятельно?',
                    'correct_answer': False,
                    'explanation': 'Любую тему можно изучить самостоятельно.'
                },
                {
                    'question_text': f'Верно ли, что тема "{topic}" связана с технологиями?',
                    'correct_answer': True,
                    'explanation': 'Многие темы связаны с технологиями.'
                }
            ],
            'short_answer': [
                {
                    'question_text': f'Дайте определение термина из темы "{topic}".',
                    'correct_answer': 'Определение зависит от термина',
                    'explanation': 'Это определение ключевого термина.'
                },
                {
                    'question_text': f'Опишите главную идею темы "{topic}".',
                    'correct_answer': 'Идея зависит от контекста',
                    'explanation': 'Каждая тема имеет центральную идею.'
                }
            ]
        }
    }
    
    # Определение предмета
    subject_key = (subject or '').lower()
    if 'матем' in subject_key or 'алгебр' in subject_key or 'геометр' in subject_key:
        subject_key = 'math'
    elif 'физ' in subject_key:
        subject_key = 'math'  # Используем математические шаблоны
    elif 'хим' in subject_key:
        subject_key = 'math'  # Используем математические шаблоны
    else:
        subject_key = 'default'
    
    # Получение шаблонов
    subject_templates = templates.get(subject_key, templates['default'])
    
    # Генерация вопросов - циклически проходим по всем типам и шаблонам
    questions = []
    question_types = ['multiple_choice', 'true_false', 'short_answer']
    
    # Генерируем запрошенное количество вопросов, чередуя типы и шаблоны
    for i in range(questions_count):
        q_type = question_types[i % len(question_types)]
        if q_type in subject_templates:
            type_templates = subject_templates[q_type]
            # Используем разные шаблоны для разнообразия
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
    }
"""

print("Инструкции по применению патча:")
print("="*60)
print("1. Откройте файл teacher/neural_network_views.py")
print("2. Найдите функцию generate_quiz_local")
print("3. Замените её содержимое на код из переменной NEW_FUNCTION")
print("="*60)
