"""
Модуль нейросетей для предсказания оценок студентов
Использует TensorFlow/Keras для построения и обучения моделей
"""

import numpy as np
import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import warnings

warnings.filterwarnings('ignore')

try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers, Sequential
    from tensorflow.keras.optimizers import Adam
    from sklearn.preprocessing import MinMaxScaler
    from sklearn.model_selection import train_test_split
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False


class StudentPerformancePredictor:
    """
    Нейросетевая модель для предсказания оценок студентов
    на основе исторических данных и параметров обучения.
    """

    def __init__(self, model_path: str = None):
        """
        Инициализация предиктора.

        Args:
            model_path: Путь для сохранения/загрузки модели
        """
        self.model = None
        self.scaler = MinMaxScaler() if TF_AVAILABLE else None
        self.model_path = model_path
        self.is_trained = False
        self.feature_names = [
            'previous_grades_avg',
            'attendance_percentage',
            'homework_completion',
            'test_performance',
            'class_participation',
            'improvement_trend'
        ]

    def _prepare_features(self, grades_history: List[int],
                         test_scores: List[float],
                         attendance: float,
                         homework_done: int,
                         homework_total: int,
                         class_participation: float = 0.7) -> np.ndarray:
        """
        Подготовка признаков для модели.

        Args:
            grades_history: История оценок студента
            test_scores: Баллы из тестов (0-100)
            attendance: Процент посещаемости (0-100)
            homework_done: Количество выполненных домашних заданий
            homework_total: Общее количество домашних заданий
            class_participation: Уровень участия в классе (0-1)

        Returns:
            Массив признаков для модели
        """
        # Средняя оценка
        previous_avg = np.mean(grades_history) if grades_history else 3.0
        previous_avg = np.clip(previous_avg, 1, 5) / 5  # Нормализация

        # Успешность домашних заданий
        homework_completion = (homework_done / homework_total) if homework_total > 0 else 0.5

        # Успешность в тестах (нормализация с 0-100 на 0-1)
        test_perf = np.mean(test_scores) / 100 if test_scores else 0.5
        test_perf = np.clip(test_perf, 0, 1)

        # Нормализация посещаемости
        attendance_norm = attendance / 100

        # Тренд улучшения (если есть данные)
        improvement = 0.5
        if len(grades_history) >= 2:
            recent = np.mean(grades_history[-3:]) if len(grades_history) >= 3 else grades_history[-1]
            earlier = np.mean(grades_history[:-3]) if len(grades_history) >= 3 else grades_history[0]
            improvement = (recent - earlier) / 5 + 0.5  # Смещение в диапазон ~0-1

        improvement = np.clip(improvement, 0, 1)
        class_participation = np.clip(class_participation, 0, 1)

        return np.array([
            previous_avg,
            attendance_norm,
            homework_completion,
            test_perf,
            class_participation,
            improvement
        ])

    def build_model(self, input_dim: int = 6) -> 'Sequential':
        """
        Построение нейросетевой модели.

        Args:
            input_dim: Количество входных признаков

        Returns:
            Скомпилированная модель Keras
        """
        if not TF_AVAILABLE:
            return None

        model = Sequential([
            layers.Input(shape=(input_dim,)),
            layers.Dense(32, activation='relu'),
            layers.Dropout(0.2),
            layers.Dense(16, activation='relu'),
            layers.Dropout(0.2),
            layers.Dense(8, activation='relu'),
            layers.Dense(1, activation='sigmoid')  # Выход 0-1, затем масштабируется до 1-5
        ])

        model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='mse',
            metrics=['mae']
        )

        return model

    def train(self, training_data: List[Dict], epochs: int = 50, batch_size: int = 16) -> Dict:
        """
        Обучение модели на исторических данных.

        Args:
            training_data: Список словарей с данными студентов
            epochs: Количество эпох обучения
            batch_size: Размер батча

        Returns:
            История обучения
        """
        if not TF_AVAILABLE:
            return {
                'error': 'TensorFlow не установлен. Установите: pip install tensorflow scikit-learn'
            }

        X = []
        y = []

        for data in training_data:
            features = self._prepare_features(
                grades_history=data.get('grades', []),
                test_scores=data.get('test_scores', []),
                attendance=data.get('attendance', 80),
                homework_done=data.get('homework_done', 0),
                homework_total=data.get('homework_total', 1),
                class_participation=data.get('participation', 0.7)
            )
            X.append(features)

            # Целевая переменная - ожидаемая оценка (1-5)
            target_grade = data.get('expected_grade', 3.0)
            y.append(np.clip(target_grade, 1, 5) / 5)  # Нормализация

        X = np.array(X)
        y = np.array(y)

        # Нормализация признаков
        X = self.scaler.fit_transform(X)

        # Разделение на тренировочную и валидационную выборки
        X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2)

        if self.model is None:
            self.model = self.build_model(input_dim=X.shape[1])

        history = self.model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=epochs,
            batch_size=batch_size,
            verbose=0
        )

        self.is_trained = True
        return {
            'loss': float(history.history['loss'][-1]),
            'val_loss': float(history.history['val_loss'][-1]),
            'mae': float(history.history['mae'][-1]),
            'val_mae': float(history.history['val_mae'][-1]),
            'epochs': epochs
        }

    def predict(self, grades_history: List[int],
               test_scores: List[float],
               attendance: float = 80,
               homework_done: int = 0,
               homework_total: int = 1,
               class_participation: float = 0.7) -> Dict:
        """
        Предсказание оценки студента.

        Args:
            grades_history: История оценок
            test_scores: Баллы из тестов
            attendance: Процент посещаемости
            homework_done: Выполненные домашние задания
            homework_total: Всего домашних заданий
            class_participation: Участие в классе

        Returns:
            Словарь с предсказанной оценкой и уверенностью
        """
        if not TF_AVAILABLE or not self.is_trained:
            return {
                'error': 'Модель не обучена или TensorFlow недоступен',
                'predicted_grade': None,
                'confidence': None
            }

        features = self._prepare_features(
            grades_history=grades_history,
            test_scores=test_scores,
            attendance=attendance,
            homework_done=homework_done,
            homework_total=homework_total,
            class_participation=class_participation
        )

        # Нормализация признаков
        features_normalized = self.scaler.transform([features])

        # Предсказание
        prediction = self.model.predict(features_normalized, verbose=0)[0][0]

        # Денормализация оценки (0-1 -> 1-5)
        predicted_grade = 1 + prediction * 4  # 1-5 шкала
        predicted_grade = np.clip(predicted_grade, 1, 5)

        # Уверенность основана на близости к целым числам
        grade_floor = np.floor(predicted_grade)
        grade_ceil = np.ceil(predicted_grade)
        remainder = predicted_grade - grade_floor

        confidence = max(1 - abs(remainder - 0.5), 0.5)  # 50-100%

        return {
            'predicted_grade': float(np.round(predicted_grade, 2)),
            'confidence': float(confidence),
            'grade_range': f'{int(grade_floor)} - {int(grade_ceil)}',
            'features_used': {
                'previous_average': float(np.mean(grades_history)) if grades_history else 3.0,
                'attendance': attendance,
                'homework_completion': (homework_done / homework_total) * 100 if homework_total > 0 else 0,
                'test_average': float(np.mean(test_scores)) if test_scores else 0
            }
        }

    def save_model(self, path: str = None):
        """Сохранение обученной модели"""
        if not TF_AVAILABLE or self.model is None:
            return False

        path = path or self.model_path
        if not path:
            return False

        try:
            self.model.save(f'{path}.h5')
            # Сохранение scaler
            scaler_data = {
                'scale_': self.scaler.scale_.tolist(),
                'min_': self.scaler.min_.tolist()
            }
            with open(f'{path}_scaler.json', 'w') as f:
                json.dump(scaler_data, f)
            return True
        except Exception as e:
            print(f'Ошибка при сохранении модели: {e}')
            return False

    def load_model(self, path: str = None):
        """Загрузка обученной модели"""
        if not TF_AVAILABLE:
            return False

        path = path or self.model_path
        if not path:
            return False

        try:
            self.model = keras.models.load_model(f'{path}.h5')
            with open(f'{path}_scaler.json', 'r') as f:
                scaler_data = json.load(f)
            self.scaler.scale_ = np.array(scaler_data['scale_'])
            self.scaler.min_ = np.array(scaler_data['min_'])
            self.is_trained = True
            return True
        except Exception as e:
            print(f'Ошибка при загрузке модели: {e}')
            return False


class StudentAnalyzer:
    """
    Анализатор для сбора и анализа данных студента
    из Django моделей.
    """

    @staticmethod
    def collect_student_data(student_name: str, grades_qs, test_results_qs) -> Dict:
        """
        Сбор данных студента из базы данных.

        Args:
            student_name: Имя студента
            grades_qs: QuerySet оценок Django
            test_results_qs: QuerySet результатов тестов Django

        Returns:
            Словарь с собранными данными студента
        """
        # Фильтрация по имени студента
        student_grades = grades_qs.filter(student_name=student_name).order_by('date')
        student_tests = test_results_qs.filter(student_name=student_name).order_by('date_completed')

        # Извлечение оценок
        grades_list = list(student_grades.values_list('grade', flat=True))

        # Извлечение результатов тестов (преобразование в проценты)
        test_scores = []
        for result in student_tests:
            if hasattr(result, 'percentage'):
                test_scores.append(result.percentage)

        # Расчет посещаемости (на основе количества оценок за последний месяц)
        one_month_ago = datetime.now() - timedelta(days=30)
        recent_grades = student_grades.filter(date__gte=one_month_ago)
        attendance = min(100, len(recent_grades) * 10)  # Примерный расчет

        # Подсчет выполненных домашних заданий
        homework_grades = student_grades.filter(grade_type='homework')
        homework_done = homework_grades.count()
        homework_total = max(homework_done, 1)  # Минимум 1

        return {
            'student_name': student_name,
            'grades': grades_list,
            'test_scores': test_scores,
            'attendance': attendance,
            'homework_done': homework_done,
            'homework_total': homework_total,
            'recent_grades_count': len(recent_grades),
            'total_grades': len(grades_list),
            'latest_grade': grades_list[-1] if grades_list else None,
            'average_grade': np.mean(grades_list) if grades_list else 0
        }

    @staticmethod
    def get_trend_analysis(grades_list: List[int]) -> Dict:
        """
        Анализ тренда успеваемости.

        Args:
            grades_list: Список оценок

        Returns:
            Словарь с анализом тренда
        """
        if len(grades_list) < 2:
            return {'trend': 'insufficient_data', 'change': 0}

        recent = np.mean(grades_list[-3:]) if len(grades_list) >= 3 else grades_list[-1]
        earlier = np.mean(grades_list[:-3]) if len(grades_list) >= 3 else grades_list[0]
        change = recent - earlier

        if change > 0.3:
            trend = 'improving'
        elif change < -0.3:
            trend = 'declining'
        else:
            trend = 'stable'

        return {
            'trend': trend,
            'change': float(change),
            'recent_average': float(recent),
            'earlier_average': float(earlier)
        }

    @staticmethod
    def get_performance_summary(student_data: Dict) -> Dict:
        """
        Получение сводки по производительности студента.

        Args:
            student_data: Данные студента

        Returns:
            Словарь со сводкой
        """
        grades = student_data.get('grades', [])
        test_scores = student_data.get('test_scores', [])

        return {
            'average_grade': float(np.mean(grades)) if grades else 0,
            'average_test_score': float(np.mean(test_scores)) if test_scores else 0,
            'highest_grade': int(max(grades)) if grades else 0,
            'lowest_grade': int(min(grades)) if grades else 0,
            'total_assessments': len(grades) + len(test_scores),
            'recent_performance': 'good' if grades and np.mean(grades[-3:]) >= 4 else
                                  'satisfactory' if grades and np.mean(grades[-3:]) >= 3 else 'needs_improvement'
        }
