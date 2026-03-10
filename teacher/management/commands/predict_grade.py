from django.core.management.base import BaseCommand
from teacher.models import (
    Curriculum, Grade, TestResult, NeuralNetworkModel,
    GradePrediction, Subject
)
from teacher.neural_network import StudentPerformancePredictor, StudentAnalyzer
import numpy as np


class Command(BaseCommand):
    help = 'Предсказать оценку студента используя обученную модель'

    def add_arguments(self, parser):
        parser.add_argument('student_name', type=str, help='ФИО студента')
        parser.add_argument('curriculum_id', type=int, help='ID учебной программы')
        parser.add_argument('--model-id', type=int, default=None, help='ID нейросетевой модели')
        parser.add_argument('--save', action='store_true', help='Сохранить предсказание в БД')

    def handle(self, *args, **options):
        student_name = options['student_name']
        curriculum_id = options['curriculum_id']
        model_id = options['model_id']
        save_prediction = options['save']

        try:
            curriculum = Curriculum.objects.get(id=curriculum_id)
        except Curriculum.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Программа с ID {curriculum_id} не найдена'))
            return

        # Получение модели
        if model_id:
            try:
                nn_model = NeuralNetworkModel.objects.get(id=model_id, curriculum=curriculum, is_active=True)
            except NeuralNetworkModel.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Активная модель с ID {model_id} не найдена'))
                return
        else:
            nn_model = NeuralNetworkModel.objects.filter(
                curriculum=curriculum,
                is_active=True
            ).order_by('-last_trained').first()

            if not nn_model:
                self.stdout.write(self.style.ERROR(f'Нет обученной модели для этой программы'))
                return

        self.stdout.write(f'Студент: {student_name}')
        self.stdout.write(f'Программа: {curriculum.title}')
        self.stdout.write(f'Модель: {nn_model.name}')

        # Сбор данных студента
        grades = Grade.objects.filter(curriculum=curriculum, student_name=student_name)
        tests = TestResult.objects.filter(
            student_name=student_name,
            test__curriculum=curriculum
        )

        grades_list = list(grades.values_list('grade', flat=True))
        test_scores = list(tests.values_list('percentage', flat=True))

        if not grades_list:
            self.stdout.write(self.style.WARNING(f'Нет оценок для студента {student_name}'))
            return

        homework_done = grades.filter(grade_type='homework').count()
        homework_total = max(grades.count(), 1)
        attendance = min(100, len(grades_list) * 10)

        self.stdout.write(f'\nДанные студента:')
        self.stdout.write(f'  Оценок: {len(grades_list)} (от {min(grades_list)} до {max(grades_list)})')
        self.stdout.write(f'  Средняя оценка: {np.mean(grades_list):.2f}')
        self.stdout.write(f'  Тестов: {len(test_scores)}')
        self.stdout.write(f'  Средний балл теста: {np.mean(test_scores):.1f}%' if test_scores else '  Тестов: 0')
        self.stdout.write(f'  Посещаемость: {attendance:.1f}%')
        self.stdout.write(f'  ДЗ выполнено: {homework_done}/{homework_total}')

        # Загрузка модели
        model_path = f'nn_models/{nn_model.id}_model'
        predictor = StudentPerformancePredictor()

        try:
            predictor.load_model(model_path)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ошибка загрузки модели: {e}'))
            return

        # Предсказание
        prediction = predictor.predict(
            grades_history=grades_list,
            test_scores=test_scores,
            attendance=attendance,
            homework_done=homework_done,
            homework_total=homework_total,
            class_participation=0.7
        )

        if 'error' in prediction:
            self.stdout.write(self.style.ERROR(f'Ошибка предсказания: {prediction["error"]}'))
            return

        # Вывод результатов
        self.stdout.write(self.style.SUCCESS(f'\n✓ Предсказание выполнено'))
        self.stdout.write(f'  Предсказанная оценка: {prediction["predicted_grade"]:.2f}')
        self.stdout.write(f'  Диапазон: {prediction["grade_range"]}')
        self.stdout.write(f'  Уверенность: {prediction["confidence"]*100:.1f}%')

        # Сохранение в БД если требуется
        if save_prediction:
            grade_prediction = GradePrediction.objects.create(
                student_name=student_name,
                subject=curriculum.subject,
                curriculum=curriculum,
                nn_model=nn_model,
                predicted_grade=prediction['predicted_grade'],
                confidence=prediction['confidence'] * 100,
                average_grade=np.mean(grades_list),
                attendance=attendance,
                test_average=np.mean(test_scores) if test_scores else 0,
                homework_completion=(homework_done / homework_total * 100) if homework_total > 0 else 0
            )
            self.stdout.write(self.style.SUCCESS(f'\nПредсказание сохранено (ID: {grade_prediction.id})'))
