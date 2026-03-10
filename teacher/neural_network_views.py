"""
Представления (Views) для работы с нейросетями
и предсказанием оценок студентов
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, DeleteView
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.db.models import Q, Avg
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.template.loader import render_to_string
from django.conf import settings

import json
from datetime import datetime
import random
import os
import re
from html import unescape
from urllib.parse import urlencode
from urllib.request import urlopen
from urllib.error import URLError

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


def _get_openai_api_key():
    """Возвращает API-ключ OpenAI из settings/env с резервными именами переменных."""
    key = getattr(settings, 'OPENAI_API_KEY', '') or os.getenv('OPENAI_API_KEY', '')
    if not key:
        # Часто по ошибке задают OPEN_API_KEY вместо OPENAI_API_KEY
        key = os.getenv('OPEN_API_KEY', '')
    return (key or '').strip()


def _is_openai_enabled():
    return OPENAI_AVAILABLE and bool(_get_openai_api_key())


def _openai_chat_completion(messages, max_tokens=500, temperature=0.7):
    """Совместимый вызов OpenAI для SDK 0.x и 1.x."""
    api_key = _get_openai_api_key()
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY не задан")

    model_name = (os.getenv('OPENAI_MODEL', 'gpt-4o-mini') or 'gpt-4o-mini').strip()
    web_search_enabled = (os.getenv('OPENAI_WEB_SEARCH', 'False').lower() == 'true')
    request_timeout = int(os.getenv('OPENAI_TIMEOUT_SECONDS', '20'))

    # Новый SDK (openai>=1.x)
    if hasattr(openai, 'OpenAI'):
        client = openai.OpenAI(api_key=api_key)

        # Опционально: web search через Responses API
        if web_search_enabled and hasattr(client, 'responses'):
            try:
                input_messages = []
                for m in messages:
                    role = m.get('role', 'user')
                    content = m.get('content', '')
                    input_messages.append({
                        "role": role,
                        "content": [{"type": "input_text", "text": content}],
                    })

                response = client.responses.create(
                    model=model_name,
                    input=input_messages,
                    tools=[{"type": "web_search_preview"}],
                    timeout=request_timeout,
                )
                output_text = getattr(response, 'output_text', '')
                if output_text:
                    return output_text.strip()
            except Exception:
                # Если web search недоступен для модели/аккаунта — fallback ниже.
                pass

        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            timeout=request_timeout,
        )
        return (response.choices[0].message.content or '').strip()

    # Старый SDK (openai==0.x)
    openai.api_key = api_key
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature,
        request_timeout=request_timeout,
    )
    return (response.choices[0].message.content or '').strip()
from .models import (
    Grade,
    TestResult,
    Subject,
    Curriculum,
    StudentGroup,
    NeuralNetworkModel,
    GradePrediction,
)


def _get_neural_network_classes():
    """Ленивый импорт нейросетевых классов, чтобы не тормозить старт Django."""
    from .neural_network import StudentPerformancePredictor, StudentAnalyzer
    return StudentPerformancePredictor, StudentAnalyzer


@login_required
def neural_network_dashboard(request):
    """Панель управления нейросетевыми моделями"""
    teacher = request.user

    # Получение активных моделей педагога
    models = NeuralNetworkModel.objects.filter(teacher=teacher, is_active=True)
    recent_predictions = GradePrediction.objects.filter(
        curriculum__lessons__teacher=teacher
    ).distinct().order_by('-prediction_date')[:10]

    # Статистика по моделям
    models_count = models.count()
    predictions_count = GradePrediction.objects.filter(
        curriculum__lessons__teacher=teacher
    ).count()
    accurate_predictions = GradePrediction.objects.filter(
        curriculum__lessons__teacher=teacher,
        is_accurate=True
    ).count()
    accuracy_rate = (accurate_predictions / predictions_count * 100) if predictions_count > 0 else 0

    context = {
        'models': models,
        'recent_predictions': recent_predictions,
        'models_count': models_count,
        'predictions_count': predictions_count,
        'accurate_predictions': accurate_predictions,
        'accuracy_rate': accuracy_rate,
    }

    return render(request, 'teacher/neural_network/dashboard.html', context)


@login_required
def train_neural_network(request, curriculum_id):
    """
    Обучение нейросетевой модели на данных студентов
    """
    curriculum = get_object_or_404(Curriculum, pk=curriculum_id)
    teacher = request.user

    if request.method == 'POST':
        StudentPerformancePredictor, _ = _get_neural_network_classes()

        # Сбор данных для обучения
        grades = Grade.objects.filter(
            curriculum=curriculum,
            teacher=teacher
        ).select_related('subject', 'class_name')

        # Группировка по студентам
        students_data = {}
        for grade in grades:
            if grade.student_name not in students_data:
                students_data[grade.student_name] = {
                    'grades': [],
                    'test_scores': [],
                    'homework_done': 0,
                    'homework_total': 0,
                    'participation': 0.7
                }
            students_data[grade.student_name]['grades'].append(grade.grade)
            if grade.grade_type == 'homework':
                students_data[grade.student_name]['homework_done'] += 1
            students_data[grade.student_name]['homework_total'] += 1

        # Добавление результатов тестов
        test_results = TestResult.objects.filter(
            test__curriculum=curriculum
        ).select_related('test')

        for result in test_results:
            if result.student_name in students_data:
                students_data[result.student_name]['test_scores'].append(result.percentage)

        # Подготовка данных для обучения
        training_data = []
        for student_name, data in students_data.items():
            if len(data['grades']) > 0:
                training_record = {
                    'student_name': student_name,
                    'grades': data['grades'],
                    'test_scores': data['test_scores'],
                    'homework_done': data['homework_done'],
                    'homework_total': max(data['homework_total'], 1),
                    'attendance': 80,
                    'participation': data['participation'],
                    'expected_grade': sum(data['grades']) / len(data['grades'])
                }
                training_data.append(training_record)

        if len(training_data) > 0:
            # Инициализация и обучение модели
            predictor = StudentPerformancePredictor()
            history = predictor.train(training_data, epochs=100, batch_size=8)

            if 'error' not in history:
                # Сохранение модели в БД
                model_name = f"{curriculum.title} - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                nn_model = NeuralNetworkModel.objects.create(
                    teacher=teacher,
                    subject=curriculum.subject,
                    curriculum=curriculum,
                    name=model_name,
                    description=f"Модель обучена на {len(training_data)} студентах",
                    is_active=True,
                    accuracy=history.get('val_mae', 0),
                    training_samples=len(training_data),
                    last_trained=datetime.now()
                )

                # Сохранение файла модели (в реальности нужна система хранилища)
                model_file_path = f"nn_models/{nn_model.id}_model"
                predictor.save_model(model_file_path)

                return JsonResponse({
                    'success': True,
                    'model_id': nn_model.id,
                    'accuracy': round(history.get('val_mae', 0), 4),
                    'samples': len(training_data),
                    'message': 'Модель успешно обучена!'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': history.get('error', 'Ошибка обучения')
                })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Недостаточно данных для обучения'
            })

    context = {
        'curriculum': curriculum,
    }
    return render(request, 'teacher/neural_network/train.html', context)


@login_required
def predict_student_grade(request, student_name, curriculum_id):
    """
    Предсказание оценки студента используя обученную модель
    """
    curriculum = get_object_or_404(Curriculum, pk=curriculum_id)
    teacher = request.user

    # Получение активной модели для этого курса
    nn_model = NeuralNetworkModel.objects.filter(
        curriculum=curriculum,
        teacher=teacher,
        is_active=True
    ).first()

    if not nn_model:
        return JsonResponse({
            'success': False,
            'error': 'Нет обученной модели для этого курса'
        })

    # Сбор данных студента
    student_grades = Grade.objects.filter(
        curriculum=curriculum,
        student_name=student_name,
        teacher=teacher
    ).select_related('subject')

    student_tests = TestResult.objects.filter(
        student_name=student_name,
        test__curriculum=curriculum
    )

    grades_list = list(student_grades.values_list('grade', flat=True))
    test_scores = list(student_tests.values_list('percentage', flat=True))

    homework_done = student_grades.filter(grade_type='homework').count()
    homework_total = max(student_grades.count(), 1)

    attendance = min(100, len(grades_list) * 10) if grades_list else 80

    # Инициализация предиктора
    StudentPerformancePredictor, _ = _get_neural_network_classes()
    predictor = StudentPerformancePredictor()
    predictor.load_model(f"nn_models/{nn_model.id}_model")

    # Получение предсказания
    prediction = predictor.predict(
        grades_history=grades_list,
        test_scores=test_scores,
        attendance=attendance,
        homework_done=homework_done,
        homework_total=homework_total,
        class_participation=0.7
    )

    if 'error' not in prediction:
        # Сохранение предсказания в БД
        grade_prediction = GradePrediction.objects.create(
            student_name=student_name,
            subject=curriculum.subject,
            curriculum=curriculum,
            nn_model=nn_model,
            predicted_grade=prediction['predicted_grade'],
            confidence=prediction['confidence'] * 100,
            average_grade=sum(grades_list) / len(grades_list) if grades_list else 0,
            attendance=attendance,
            test_average=sum(test_scores) / len(test_scores) if test_scores else 0,
            homework_completion=(homework_done / homework_total * 100) if homework_total > 0 else 0
        )

        prediction['prediction_id'] = grade_prediction.id
        prediction['success'] = True

    return JsonResponse(prediction)


@login_required
def student_analysis(request, student_name, curriculum_id):
    """
    Детальный анализ студента и его прогнозы
    """
    curriculum = get_object_or_404(Curriculum, pk=curriculum_id)
    teacher = request.user
    _, StudentAnalyzer = _get_neural_network_classes()

    # Получение данных студента
    student_data = StudentAnalyzer.collect_student_data(
        student_name=student_name,
        grades_qs=Grade.objects.filter(curriculum=curriculum, teacher=teacher),
        test_results_qs=TestResult.objects.filter(test__curriculum=curriculum)
    )

    # Анализ тренда
    trend_analysis = StudentAnalyzer.get_trend_analysis(student_data['grades'])

    # Сводка по производительности
    performance_summary = StudentAnalyzer.get_performance_summary(student_data)

    # Получение предсказаний
    predictions = GradePrediction.objects.filter(
        student_name=student_name,
        curriculum=curriculum
    ).order_by('-prediction_date')[:5]

    context = {
        'student_name': student_name,
        'curriculum': curriculum,
        'student_data': student_data,
        'trend_analysis': trend_analysis,
        'performance_summary': performance_summary,
        'predictions': predictions,
    }

    return render(request, 'teacher/neural_network/student_analysis.html', context)


class NeuralNetworkModelListView(LoginRequiredMixin, ListView):
    """Список нейросетевых моделей пользователя"""
    model = NeuralNetworkModel
    template_name = 'teacher/neural_network/model_list.html'
    context_object_name = 'models'
    paginate_by = 20

    def get_queryset(self):
        return NeuralNetworkModel.objects.filter(
            teacher=self.request.user
        ).select_related('subject', 'curriculum').order_by('-updated_at')


class NeuralNetworkModelDetailView(LoginRequiredMixin, DetailView):
    """Детальная информация о модели"""
    model = NeuralNetworkModel
    template_name = 'teacher/neural_network/model_detail.html'
    context_object_name = 'model'

    def get_queryset(self):
        return NeuralNetworkModel.objects.filter(teacher=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['predictions'] = GradePrediction.objects.filter(
            nn_model=self.object
        ).order_by('-prediction_date')[:20]
        return context


class GradePredictionListView(LoginRequiredMixin, ListView):
    """Список предсказаний оценок"""
    model = GradePrediction
    template_name = 'teacher/neural_network/prediction_list.html'
    context_object_name = 'predictions'
    paginate_by = 50

    def get_queryset(self):
        return GradePrediction.objects.filter(
            curriculum__lessons__teacher=self.request.user
        ).distinct().select_related('subject', 'curriculum', 'nn_model').order_by('-prediction_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        predictions = self.get_queryset()
        context['total_predictions'] = predictions.count()
        context['accurate_count'] = predictions.filter(is_accurate=True).count()
        context['accuracy_rate'] = (
            context['accurate_count'] / context['total_predictions'] * 100
            if context['total_predictions'] > 0 else 0
        )
        return context


@login_required
@require_POST
def confirm_student_grade(request):
    """
    AJAX запрос для подтверждения фактической оценки студента
    и проверки точности предсказания
    """
    try:
        data = json.loads(request.body)
        prediction_id = data.get('prediction_id')
        actual_grade = data.get('actual_grade')

        prediction = get_object_or_404(GradePrediction, pk=prediction_id)

        # Обновление фактической оценки
        prediction.actual_grade = actual_grade
        prediction.save()  # save() автоматически установит is_accurate

        return JsonResponse({
            'success': True,
            'is_accurate': prediction.is_accurate,
            'message': 'Оценка подтверждена' if prediction.is_accurate else 'Предсказание неточно'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
def model_statistics(request, model_id):
    """Детальная статистика по модели"""
    model = get_object_or_404(NeuralNetworkModel, pk=model_id, teacher=request.user)

    predictions = GradePrediction.objects.filter(nn_model=model).order_by('-prediction_date')

    stats = {
        'total_predictions': predictions.count(),
        'accurate_predictions': predictions.filter(is_accurate=True).count(),
        'average_confidence': predictions.aggregate(avg=Avg('confidence'))['avg'] or 0,
        'average_predicted_grade': predictions.aggregate(avg=Avg('predicted_grade'))['avg'] or 0,
    }

    stats['accuracy_rate'] = (
        stats['accurate_predictions'] / stats['total_predictions'] * 100
        if stats['total_predictions'] > 0 else 0
    )

    context = {
        'model': model,
        'stats': stats,
        'recent_predictions': predictions[:20],
    }

    return render(request, 'teacher/neural_network/model_statistics.html', context)


@login_required
def generate_homework_helper(request):
    """Помощник в генерации домашних заданий с помощью ИИ"""
    if request.method == 'POST':
        subject_name = request.POST.get('subject', '')
        topic_name = request.POST.get('topic', '')
        class_level = request.POST.get('class_level', '')
        difficulty = request.POST.get('difficulty', 'medium')
        lesson_type = request.POST.get('lesson_type', 'theory')

        # Генерация задания на основе параметров
        homework = generate_homework_text(
            subject=subject_name,
            topic=topic_name,
            class_level=class_level,
            difficulty=difficulty,
            lesson_type=lesson_type
        )

        return JsonResponse({
            'success': True,
            'homework': homework
        })

    # Проверка доступности OpenAI
    openai_enabled = _is_openai_enabled()

    return render(request, 'teacher/homework_generator.html', {
        'openai_enabled': openai_enabled
    })


def generate_homework_text(subject, topic, class_level, difficulty, lesson_type):
    """Генерация текста домашнего задания на основе параметров"""

    # Попытка генерации через OpenAI API
    if _is_openai_enabled():
        try:
            # Определение уровня сложности на английском
            difficulty_map = {
                'easy': 'easy',
                'medium': 'medium',
                'hard': 'advanced/challenging'
            }

            lesson_type_map = {
                'theory': 'theoretical',
                'practice': 'practical'
            }

            prompt = f"""
            Create a homework assignment for a {class_level or 'school'} student in {subject}.
            Topic: {topic}
            Difficulty level: {difficulty_map.get(difficulty, 'medium')}
            Lesson type: {lesson_type_map.get(lesson_type, 'mixed')}

            The assignment should be:
            - Age-appropriate for {class_level or 'school'} level
            - Educational and engaging
            - Clear and specific
            - Include specific tasks or exercises
            - Suitable for home completion

            Generate a concise homework assignment in Russian language.
            """

            homework = _openai_chat_completion(
                messages=[
                    {"role": "system", "content": "You are an experienced teacher creating homework assignments. Always respond in Russian."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.7,
            )

            # На всякий случай принудительно приводим к русскому языку
            homework = _translate_text_to_russian(homework)
            if not _contains_cyrillic(homework):
                return generate_homework_local(subject, topic, class_level, difficulty, lesson_type)

            # Добавление дополнительной информации в зависимости от сложности
            if difficulty == 'hard':
                homework += "\n\nДополнительно: Подготовить презентацию или отчет о проделанной работе."
            elif difficulty == 'medium':
                homework += "\n\nПодготовить краткое объяснение выполненных заданий."

            return homework

        except Exception as e:
            print(f"OpenAI API error: {e}")
            # Fallback to local generation

    # Локальная генерация (fallback)
    homework = generate_homework_local(subject, topic, class_level, difficulty, lesson_type)
    homework = _translate_text_to_russian(homework)
    if not _contains_cyrillic(homework):
        return generate_homework_local(subject, topic, class_level, difficulty, lesson_type)
    return homework


def generate_homework_local(subject, topic, class_level, difficulty, lesson_type):
    """Локальная генерация домашнего задания на основе шаблонов"""

    # Базовые шаблоны для разных предметов и типов уроков
    templates = {
        'math': {
            'theory': {
                'easy': [
                    "Повторить основные понятия из темы '{topic}'. Решить упражнения №{numbers} из учебника.",
                    "Изучить материал по теме '{topic}'. Подготовить краткий конспект основных формул.",
                    "Прочитать параграф учебника по теме '{topic}'. Ответить на вопросы в конце параграфа."
                ],
                'medium': [
                    "Решить задачи №{numbers} из учебника по теме '{topic}'. Подготовить объяснение решения.",
                    "Изучить доказательство теоремы по теме '{topic}'. Подготовить примеры применения.",
                    "Выполнить упражнения на закрепление материала по теме '{topic}'."
                ],
                'hard': [
                    "Решить сложные задачи повышенной сложности по теме '{topic}'. Подготовить презентацию решения.",
                    "Исследовать применение теоремы '{topic}' в практических задачах. Подготовить отчет.",
                    "Разработать алгоритм решения задач по теме '{topic}' и протестировать его на примерах."
                ]
            },
            'practice': {
                'easy': [
                    "Решить 10 простых задач по теме '{topic}' из рабочей тетради.",
                    "Выполнить тренировочные упражнения на закрепление навыков по теме '{topic}'.",
                    "Подготовить примеры решения типовых задач по теме '{topic}'."
                ],
                'medium': [
                    "Решить задачи средней сложности №{numbers} по теме '{topic}'.",
                    "Выполнить комплекс упражнений на применение знаний по теме '{topic}'.",
                    "Подготовить и решить 5 задач творческого характера по теме '{topic}'."
                ],
                'hard': [
                    "Решить олимпиадные задачи по теме '{topic}'. Подготовить подробные решения.",
                    "Выполнить исследовательскую работу по теме '{topic}' с практическим применением.",
                    "Разработать и решить систему задач по теме '{topic}' повышенной сложности."
                ]
            }
        },
        'physics': {
            'theory': {
                'easy': [
                    "Изучить основные законы и понятия по теме '{topic}'. Подготовить словарь терминов.",
                    "Прочитать материал учебника по теме '{topic}'. Выписать основные формулы.",
                    "Подготовить презентацию основных понятий по теме '{topic}'."
                ],
                'medium': [
                    "Изучить и законспектировать материал по теме '{topic}'. Подготовить примеры применения законов.",
                    "Решить качественные задачи по теме '{topic}' с объяснением физического смысла.",
                    "Подготовить лабораторную работу по демонстрации явлений из темы '{topic}'."
                ],
                'hard': [
                    "Провести исследование физических явлений по теме '{topic}'. Подготовить научный отчет.",
                    "Разработать эксперимент по проверке законов из темы '{topic}'.",
                    "Подготовить проект по практическому применению законов '{topic}'."
                ]
            },
            'practice': {
                'easy': [
                    "Решить задачи №{numbers} из учебника по теме '{topic}'.",
                    "Выполнить расчеты по формулам из темы '{topic}' на конкретных примерах.",
                    "Подготовить графики и диаграммы по теме '{topic}'."
                ],
                'medium': [
                    "Решить комплексные задачи по теме '{topic}' с построением графиков.",
                    "Выполнить лабораторные измерения и расчеты по теме '{topic}'.",
                    "Подготовить презентацию решения задач по теме '{topic}'."
                ],
                'hard': [
                    "Решить задачи повышенной сложности по теме '{topic}' с анализом результатов.",
                    "Выполнить проектную работу по теме '{topic}' с экспериментальной частью.",
                    "Разработать математическую модель явлений из темы '{topic}'."
                ]
            }
        },
        'chemistry': {
            'theory': {
                'easy': [
                    "Изучить основные понятия и термины по теме '{topic}'. Подготовить словарь.",
                    "Прочитать материал учебника по теме '{topic}'. Выписать химические реакции.",
                    "Подготовить таблицу основных веществ и их свойств по теме '{topic}'."
                ],
                'medium': [
                    "Изучить и законспектировать материал по теме '{topic}'. Подготовить схемы реакций.",
                    "Решить задачи на расчеты по химическим реакциям из темы '{topic}'.",
                    "Подготовить лабораторную работу по демонстрации реакций из темы '{topic}'."
                ],
                'hard': [
                    "Провести исследование химических реакций по теме '{topic}'. Подготовить отчет.",
                    "Разработать эксперимент по изучению свойств веществ из темы '{topic}'.",
                    "Подготовить проект по промышленному применению реакций из темы '{topic}'."
                ]
            },
            'practice': {
                'easy': [
                    "Решить задачи №{numbers} из учебника по теме '{topic}'.",
                    "Выполнить расчеты по химическим реакциям из темы '{topic}'.",
                    "Подготовить коллекцию химических реакций по теме '{topic}'."
                ],
                'medium': [
                    "Решить комплексные задачи по теме '{topic}' с составлением уравнений реакций.",
                    "Выполнить лабораторные опыты по теме '{topic}' с записью наблюдений.",
                    "Подготовить презентацию химических реакций из темы '{topic}'."
                ],
                'hard': [
                    "Решить задачи повышенной сложности по теме '{topic}' с анализом результатов.",
                    "Выполнить исследовательскую работу по теме '{topic}' с экспериментальной частью.",
                    "Разработать технологический процесс на основе реакций из темы '{topic}'."
                ]
            }
        },
        'default': {
            'theory': {
                'easy': [
                    "Изучить материал по теме '{topic}'. Подготовить краткий конспект.",
                    "Прочитать учебный материал по теме '{topic}'. Ответить на вопросы для самопроверки.",
                    "Подготовить словарь основных терминов по теме '{topic}'."
                ],
                'medium': [
                    "Изучить и законспектировать материал по теме '{topic}'. Подготовить примеры.",
                    "Выполнить упражнения на закрепление знаний по теме '{topic}'.",
                    "Подготовить презентацию основных понятий по теме '{topic}'."
                ],
                'hard': [
                    "Провести исследование по теме '{topic}'. Подготовить отчет с выводами.",
                    "Разработать проект по практическому применению знаний из темы '{topic}'.",
                    "Подготовить аналитическую работу по теме '{topic}' с использованием дополнительных источников."
                ]
            },
            'practice': {
                'easy': [
                    "Выполнить практические задания по теме '{topic}' из учебника.",
                    "Подготовить примеры применения знаний из темы '{topic}'.",
                    "Выполнить тренировочные упражнения по теме '{topic}'."
                ],
                'medium': [
                    "Выполнить комплекс практических заданий по теме '{topic}'.",
                    "Подготовить и выполнить проект по теме '{topic}'.",
                    "Выполнить творческие задания по применению знаний из темы '{topic}'."
                ],
                'hard': [
                    "Выполнить исследовательскую работу по теме '{topic}' с практическим применением.",
                    "Разработать и реализовать проект по теме '{topic}' повышенной сложности.",
                    "Подготовить презентацию результатов исследования по теме '{topic}'."
                ]
            }
        }
    }

    # Определение предмета
    subject_key = subject.lower()
    if 'матем' in subject_key or 'алгебр' in subject_key or 'геометр' in subject_key:
        subject_key = 'math'
    elif 'физ' in subject_key:
        subject_key = 'physics'
    elif 'хим' in subject_key:
        subject_key = 'chemistry'
    else:
        subject_key = 'default'

    # Получение шаблонов
    subject_templates = templates.get(subject_key, templates['default'])
    lesson_templates = subject_templates.get(lesson_type, subject_templates['theory'])
    difficulty_templates = lesson_templates.get(difficulty, lesson_templates['medium'])

    # Выбор случайного шаблона
    import random
    template = random.choice(difficulty_templates)

    # Генерация номеров задач для математических предметов
    if subject_key in ['math', 'physics', 'chemistry'] and '{numbers}' in template:
        numbers = ", ".join([str(random.randint(1, 50)) for _ in range(random.randint(3, 8))])
        template = template.replace('{numbers}', numbers)

    # Заполнение шаблона
    homework = template.format(topic=topic or "тема урока")

    # Добавление дополнительной информации в зависимости от сложности
    if difficulty == 'hard':
        homework += "\n\nДополнительно: Подготовить презентацию или отчет о проделанной работе."
    elif difficulty == 'medium':
        homework += "\n\nПодготовить краткое объяснение выполненных заданий."

    return homework


def generate_quiz_helper(request):
    """Помощник в генерации викторины с помощью ИИ"""
    if request.method == 'POST':
        # Значения по умолчанию, чтобы безопасно использовать их в fallback.
        subject_name = ''
        topic_name = ''
        class_level = ''
        difficulty = 'medium'
        questions_count = 5

        try:
            if not request.user.is_authenticated:
                return JsonResponse({
                    'success': False,
                    'error': 'Требуется авторизация',
                    'login_url': f"/accounts/login/?next={request.path}",
                }, status=401)

            payload = {}
            if request.content_type and 'application/json' in request.content_type:
                try:
                    payload = json.loads(request.body or '{}')
                except json.JSONDecodeError:
                    payload = {}

            source = payload if payload else request.POST
            subject_name = source.get('subject', '')
            topic_name = source.get('topic', '')
            class_level = source.get('class_level', '')
            difficulty = source.get('difficulty', 'medium')
            # Принудительно используем русский язык для всего генератора
            language = 'russian'
            deep_search = source.get('deep_search', 'standard')
            try:
                questions_count = int(source.get('questions_count', 5))
            except (TypeError, ValueError):
                questions_count = 5

            # Генерация викторины на основе параметров
            quiz_data = generate_quiz_questions(
                subject=subject_name,
                topic=topic_name,
                class_level=class_level,
                difficulty=difficulty,
                questions_count=questions_count,
                language=language,
                deep_search=(deep_search == 'deep')
            )

            # Гарантируем результат даже при частичных сбоях внешних источников
            if not isinstance(quiz_data, dict) or not quiz_data.get('questions'):
                quiz_data = generate_quiz_local(
                    subject=subject_name,
                    topic=topic_name,
                    class_level=class_level,
                    difficulty=difficulty,
                    questions_count=questions_count,
                )

            return JsonResponse({'success': True, 'quiz': quiz_data})
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Quiz generation error: {error_details}")

            # Последний fallback: возвращаем локальную викторину вместо ошибки 500
            try:
                fallback_quiz = generate_quiz_local(
                    subject=subject_name,
                    topic=topic_name,
                    class_level=class_level,
                    difficulty=difficulty,
                    questions_count=questions_count,
                )
                return JsonResponse({
                    'success': True,
                    'quiz': fallback_quiz,
                    'warning': 'Произошла ошибка ИИ/интернет-генерации, использованы локальные шаблоны.'
                })
            except Exception:
                pass

            return JsonResponse({
                'success': False,
                'error': str(e),
                'details': error_details if settings.DEBUG else 'Ошибка генерации викторины'
            }, status=500)

    if not request.user.is_authenticated:
        return redirect(f"/accounts/login/?next={request.path}")

    # Проверка доступности OpenAI
    openai_enabled = _is_openai_enabled()

    return render(request, 'teacher/quiz_generator.html', {
        'openai_enabled': openai_enabled
    })


def generate_quiz_questions(subject, topic, class_level, difficulty, questions_count, language='russian', deep_search=False):
    """Генерация вопросов викторины на основе параметров"""
    # Принудительно русский язык
    language = 'russian'

    # Для русского языка используем быстрый и стабильный поток:
    # OpenAI (если доступен) -> локальные шаблоны.
    # Интернет-источники и построчный перевод отключены в этом режиме,
    # чтобы избежать долгих внешних запросов и 500 из-за timeout.

    search_mode = "УГЛУБЛЕННЫЙ - ищи информацию из РАЗНЫХ источников, охватывая разные аспекты темы" if deep_search else "стандартный"
    detail_level = "подробные с фактами из разных источников" if deep_search else "краткие но информативные"

    # Попытка генерации через OpenAI API
    if _is_openai_enabled() and language == 'russian':
        try:
            # Определение уровня сложности
            difficulty_map = {
                'easy': 'easy',
                'medium': 'medium',
                'hard': 'advanced/challenging'
            }

            prompt = f"""
            Создай УВЛЕКАТЕЛЬНУЮ и ПОЗНАВАТЕЛЬНУЮ викторину из {questions_count} вопросов для уровня "{class_level or 'школьники'}" по предмету "{subject}".
            Тема: {topic}
            Сложность: {difficulty_map.get(difficulty, 'medium')}
            Режим поиска: {search_mode}

            ВАЖНО: 
            - Все тексты должны быть НА РУССКОМ языке
            - Используй РЕАЛЬНЫЕ ФАКТЫ и актуальную информацию{' ИЗ РАЗНЫХ ИСТОЧНИКОВ (книги, статьи, исследования)' if deep_search else ''}
            - Вопросы должны быть интересными и проверять понимание{' РАЗНЫХ АСПЕКТОВ темы' if deep_search else ''}
            - Варианты ответов должны быть правдоподобными
            - Объяснения должны быть {detail_level}
            - Для multiple_choice используй 4 варианта ответа
            - Избегай очевидных вариантов типа "все перечисленное"
            {f'- ОХВАТЫВАЙ разные стороны темы: историю, применение, интересные факты' if deep_search else ''}

            Сделай смесь типов вопросов:
            - multiple_choice (один правильный ответ, 4 варианта)
            - true_false (верно/неверно)
            - short_answer (краткий ответ)

            Для каждого вопроса верни:
            1. question_text (интересный вопрос с реальными фактами)
            2. question_type (multiple_choice, true_false, short_answer)
            3. options (только для multiple_choice, 4 варианта)
            4. correct_answer (индекс для multiple_choice, true/false для true_false, строка для short_answer)
            5. explanation (объяснение с фактами)
            6. points (всегда 1)

            Верни ТОЛЬКО JSON-массив объектов.
            Без markdown, без комментариев, без дополнительного текста.
            """

            quiz_json = _openai_chat_completion(
                messages=[
                    {"role": "system", "content": "Ты опытный преподаватель с доступом к актуальным знаниям. Создавай викторины с реальными фактами, интересными деталями и познавательным контентом. Отвечай только валидным JSON на русском языке."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2500,
                temperature=0.8,
            )

            # Попытка парсинга JSON
            try:
                questions = json.loads(quiz_json)
                return {
                    'title': f'Викторина: {topic}',
                    'description': f'Увлекательная викторина с реальными фактами и знаниями по теме "{topic}" из глобальных источников',
                    'questions': questions,
                    'generated_by': 'openai_internet'
                }
            except json.JSONDecodeError:
                print(f"JSON parsing error: {quiz_json}")
                # Fallback to local generation

        except Exception as e:
            print(f"OpenAI API error: {e}")
            # Fallback to local generation
    
    # Для русского языка после всех попыток — локальные шаблоны (гарантированно русский)
    if language == 'russian':
        return generate_quiz_local(subject, topic, class_level, difficulty, questions_count)

    # Локальная генерация (fallback)
    return generate_quiz_local(subject, topic, class_level, difficulty, questions_count)


def _get_opentdb_category(subject: str):
    """Подбор категории Open Trivia DB по школьному предмету."""
    subject_key = (subject or '').lower()
    mapping = {
        'матем': 19,
        'алгебр': 19,
        'геометр': 19,
        'хим': 17,
        'физ': 17,
        'биол': 17,
        'географ': 22,
        'истор': 23,
        'литерат': 10,
        'англ': 10,
        'русск': 9,
        'информ': 18,
    }
    for key, category in mapping.items():
        if key in subject_key:
            return category
    return None


def _normalize_opentdb_question(item):
    """Преобразование вопроса Open Trivia DB в формат проекта."""
    q_type = (item.get('type') or 'multiple').strip()
    question_text = unescape(item.get('question', '')).strip()
    correct_answer = unescape(item.get('correct_answer', '')).strip()
    incorrect_answers = [unescape(ans).strip() for ans in item.get('incorrect_answers', [])]

    if not question_text or not correct_answer:
        return None

    if q_type == 'boolean':
        correct_bool = correct_answer.lower() == 'true'
        explanation = f"Правильный ответ: {'Верно' if correct_bool else 'Неверно'}."
        return {
            'question_text': question_text,
            'question_type': 'true_false',
            'options': None,
            'correct_answer': correct_bool,
            'explanation': explanation,
            'points': 1,
        }

    options = incorrect_answers + [correct_answer]
    random.shuffle(options)
    correct_index = options.index(correct_answer)
    explanation = f"Правильный ответ: {correct_answer}."

    return {
        'question_text': question_text,
        'question_type': 'multiple_choice',
        'options': options,
        'correct_answer': correct_index,
        'explanation': explanation,
        'points': 1,
    }


def _contains_cyrillic(text):
    return bool(re.search(r'[А-Яа-яЁё]', text or ''))


def _quiz_is_russian(questions):
    if not questions:
        return False

    # Строгая проверка: ориентируемся на язык самого вопроса,
    # а не на пояснение (оно может быть русским даже при английском вопросе).
    russian_count = 0
    for q in questions:
        question_text = str(q.get('question_text', '') or '')
        if _contains_cyrillic(question_text):
            russian_count += 1

    # Требуем русский текст у большинства вопросов (лучше полностью).
    return russian_count >= max(1, int(len(questions) * 0.8))


def _translate_text_to_russian(text):
    """Переводит текст на русский через публичный API (fallback без OpenAI)."""
    if not text:
        return text

    value = str(text).strip()
    if not value or _contains_cyrillic(value):
        return value

    try:
        api_url = "https://api.mymemory.translated.net/get?" + urlencode({
            'q': value,
            'langpair': 'en|ru',
        })
        with urlopen(api_url, timeout=8) as response:
            payload = json.loads(response.read().decode('utf-8'))
        translated = (payload.get('responseData') or {}).get('translatedText', '')
        translated = unescape((translated or '').strip())
        return translated or value
    except Exception:
        return value


def _translate_questions_to_russian(questions):
    """Переводит вопросы на русский: OpenAI, затем fallback через публичный API."""
    if not questions:
        return None

    # 1) Качественный перевод через OpenAI (если доступен)
    if _is_openai_enabled():
        try:
            prompt = (
                "Переведи массив вопросов викторины на русский язык. "
                "Сохрани структуру JSON и типы данных: question_type, points, индексы correct_answer, bool значения. "
                "Переводи только текстовые поля question_text, options, explanation и строковые ответы. "
                "Верни только JSON-массив.\n\n"
                f"Входной JSON:\n{json.dumps(questions, ensure_ascii=False)}"
            )

            translated_json = _openai_chat_completion(
                messages=[
                    {
                        "role": "system",
                        "content": "Ты помощник преподавателя. Возвращай только корректный JSON без дополнительного текста.",
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=2500,
                temperature=0.2,
            )

            translated = json.loads(translated_json)
            if isinstance(translated, list) and translated:
                return translated
        except Exception:
            pass

    # 2) Fallback-перевод без OpenAI
    translated_questions = []
    for q in questions:
        item = dict(q)
        item['question_text'] = _translate_text_to_russian(item.get('question_text', ''))
        item['explanation'] = _translate_text_to_russian(item.get('explanation', ''))

        options = item.get('options')
        if isinstance(options, list):
            item['options'] = [_translate_text_to_russian(opt) for opt in options]

        answer = item.get('correct_answer')
        if isinstance(answer, str):
            item['correct_answer'] = _translate_text_to_russian(answer)

        translated_questions.append(item)

    if translated_questions and _quiz_is_russian(translated_questions):
        return translated_questions

    return None


def generate_quiz_from_internet(subject, topic, difficulty, questions_count, deep_search=False):
    """Генерация викторины из открытого интернет-API Open Trivia DB."""
    requested_count = max(1, min(int(questions_count or 5), 25))
    fetch_count = requested_count * 2 if deep_search else requested_count
    params = {
        'amount': max(1, min(fetch_count, 50)),
    }

    category = _get_opentdb_category(subject)
    if category:
        params['category'] = category

    difficulty_key = (difficulty or '').lower().strip()
    if difficulty_key in {'easy', 'medium', 'hard'}:
        params['difficulty'] = difficulty_key

    url = f"https://opentdb.com/api.php?{urlencode(params)}"

    try:
        with urlopen(url, timeout=8) as response:
            payload = json.loads(response.read().decode('utf-8'))
    except (URLError, TimeoutError, json.JSONDecodeError, ValueError):
        return None

    if payload.get('response_code') != 0:
        return None

    raw_questions = payload.get('results') or []
    questions = []
    for item in raw_questions:
        normalized = _normalize_opentdb_question(item)
        if normalized:
            questions.append(normalized)

    if not questions:
        return None

    # В deep_search стараемся повысить релевантность к теме
    topic_text = (topic or '').strip().lower()
    if deep_search and topic_text:
        topic_keywords = [w for w in re.split(r'\W+', topic_text) if len(w) >= 4]
        if topic_keywords:
            filtered = []
            for q in questions:
                merged = ' '.join(
                    [
                        str(q.get('question_text', '')),
                        str(q.get('explanation', '')),
                        ' '.join(q.get('options') or []),
                    ]
                ).lower()
                if any(keyword in merged for keyword in topic_keywords):
                    filtered.append(q)
            if len(filtered) >= min(3, requested_count):
                questions = filtered

    questions = questions[:requested_count]

    title_topic = (topic or subject or 'Общая тема').strip()
    return {
        'title': f'Викторина: {title_topic}',
        'description': f'Увлекательная викторина, собранная из интернет-источников по теме "{title_topic}".',
        'questions': questions,
        'generated_by': 'internet',
    }


def generate_quiz_local(subject, topic, class_level, difficulty, questions_count):
    """Локальная генерация викторины на основе улучшенных шаблонов"""
    import random
    from .quiz_templates import QUIZ_TEMPLATES, get_subject_key
    
    topic_safe = topic or subject or "Общая тема"
    subject_key = get_subject_key(subject)
    
    subject_templates = QUIZ_TEMPLATES.get(subject_key, QUIZ_TEMPLATES['default'])
    
    questions = []
    question_types = ['multiple_choice', 'true_false', 'short_answer']
    
    # Собираем все доступные вопросы
    all_questions = []
    for q_type in question_types:
        if q_type in subject_templates:
            for template in subject_templates[q_type]:
                q = template.copy()
                q['question_type'] = q_type
                q['points'] = 1
                all_questions.append(q)
    
    # Перемешиваем и выбираем нужное количество
    random.shuffle(all_questions)
    questions = all_questions[:questions_count]
    
    # Если вопросов не хватает, дублируем
    while len(questions) < questions_count:
        questions.extend(all_questions[:questions_count - len(questions)])
    
    return {
        'title': f'Викторина: {topic_safe}',
        'description': f'Обучающая викторина по теме "{topic_safe}" для уровня "{class_level or "школьники"}" ({questions_count} вопросов)',
        'questions': questions[:questions_count],
        'generated_by': 'local'
    }