from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from teacher.models import Curriculum, Grade, TestResult, NeuralNetworkModel
from teacher.neural_network import StudentPerformancePredictor, StudentAnalyzer
from datetime import datetime
import numpy as np


class Command(BaseCommand):
    help = 'Обучить нейросетевую модель для предсказания оценок'

    def add_arguments(self, parser):
        parser.add_argument('curriculum_id', type=int, help='ID учебной программы')
        parser.add_argument('--epochs', type=int, default=100, help='Количество эпох обучения')
        parser.add_argument('--batch-size', type=int, default=8, help='Размер батча')
        parser.add_argument('--teacher-id', type=int, default=None, help='ID педагога')

    def handle(self, *args, **options):
        curriculum_id = options['curriculum_id']
        epochs = options['epochs']
        batch_size = options['batch_size']
        teacher_id = options['teacher_id']

        try:
            curriculum = Curriculum.objects.get(id=curriculum_id)
        except Curriculum.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Программа с ID {curriculum_id} не найдена'))
            return

        # Фильтрация по педагогу если указан
        grades_qs = Grade.objects.filter(curriculum=curriculum)
        if teacher_id:
            teacher = User.objects.get(id=teacher_id)
            grades_qs = grades_qs.filter(teacher=teacher)
        else:
            teacher = grades_qs.first().teacher if grades_qs.exists() else None

        if not grades_qs.exists():
            self.stdout.write(self.style.ERROR('Нет оценок для этой программы'))
            return

        self.stdout.write(f'Обучение модели для программы: {curriculum.title}')
        self.stdout.write(f'Параметры: эпохи={epochs}, размер батча={batch_size}')

        # Сбор данных
        students = grades_qs.values_list('student_name', flat=True).distinct()
        training_data = []

        self.stdout.write(f'Сбор данных {len(students)} студентов...')

        for student_name in students:
            student_grades = grades_qs.filter(student_name=student_name)
            student_tests = TestResult.objects.filter(
                student_name=student_name,
                test__curriculum=curriculum
            )

            grades_list = list(student_grades.values_list('grade', flat=True))
            test_scores = list(student_tests.values_list('percentage', flat=True))

            if len(grades_list) == 0:
                continue

            homework_done = student_grades.filter(grade_type='homework').count()
            homework_total = max(student_grades.count(), 1)
            attendance = min(100, len(grades_list) * 10)

            training_record = {
                'student_name': student_name,
                'grades': grades_list,
                'test_scores': test_scores,
                'attendance': attendance,
                'homework_done': homework_done,
                'homework_total': homework_total,
                'participation': 0.7,
                'expected_grade': np.mean(grades_list) if grades_list else 3.0
            }
            training_data.append(training_record)

        if len(training_data) < 2:
            self.stdout.write(self.style.ERROR('Недостаточно данных для обучения (минимум 2 студента)'))
            return

        # Обучение модели
        self.stdout.write(f'Обучение на {len(training_data)} примерах...')
        predictor = StudentPerformancePredictor()
        history = predictor.train(training_data, epochs=epochs, batch_size=batch_size)

        if 'error' in history:
            self.stdout.write(self.style.ERROR(f'Ошибка обучения: {history["error"]}'))
            return

        # Сохранение модели
        model_name = f'{curriculum.title} - {datetime.now().strftime("%Y-%m-%d %H:%M")}'
        model_path = f'nn_models/{curriculum_id}_model'

        predictor.save_model(model_path)

        # Сохранение в БД
        nn_model = NeuralNetworkModel.objects.create(
            teacher=teacher,
            subject=curriculum.subject,
            curriculum=curriculum,
            name=model_name,
            description=f'Модель обучена на {len(training_data)} студентах',
            is_active=True,
            accuracy=history.get('val_mae', 0),
            training_samples=len(training_data),
            last_trained=datetime.now()
        )

        self.stdout.write(self.style.SUCCESS(f'Модель успешно обучена!'))
        self.stdout.write(f'ID модели: {nn_model.id}')
        self.stdout.write(f'Точность (MAE): {history.get("val_mae", 0):.4f}')
        self.stdout.write(f'Примеров обучения: {len(training_data)}')
        self.stdout.write(f'История потерь:')
        self.stdout.write(f'  Loss: {history.get("loss", 0):.4f}')
        self.stdout.write(f'  Val Loss: {history.get("val_loss", 0):.4f}')
        self.stdout.write(f'  MAE: {history.get("mae", 0):.4f}')
        self.stdout.write(f'  Val MAE: {history.get("val_mae", 0):.4f}')
