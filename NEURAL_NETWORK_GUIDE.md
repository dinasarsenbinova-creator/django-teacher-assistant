# Руководство по нейросетевым моделям Django сайта

## Обзор

Система нейросетевых моделей предназначена для **предсказания оценок студентов** на основе их исторических данных и показателей успеваемости.

## Компоненты

### 1. Модуль нейросети (`teacher/neural_network.py`)

Содержит два основных класса:

#### `StudentPerformancePredictor`
Класс для обучения и использования нейросетевой модели.

**Методы:**
- `build_model()` - Создание архитектуры нейросети
- `train(training_data, epochs, batch_size)` - Обучение модели
- `predict()` - Предсказание оценки студента
- `save_model()` - Сохранение обученной модели
- `load_model()` - Загрузка сохраненной модели

**Пример использования:**
```python
from teacher.neural_network import StudentPerformancePredictor

# Инициализация
predictor = StudentPerformancePredictor()

# Обучение на данных
training_data = [
    {
        'grades': [4, 3, 4, 5],
        'test_scores': [85, 90, 88],
        'attendance': 95,
        'homework_done': 8,
        'homework_total': 10,
        'expected_grade': 4.0
    },
    # ... еще примеры
]

history = predictor.train(training_data, epochs=100)

# Предсказание
prediction = predictor.predict(
    grades_history=[4, 3, 4],
    test_scores=[85, 90],
    attendance=95,
    homework_done=8,
    homework_total=10
)

print(f"Предсказанная оценка: {prediction['predicted_grade']}")
print(f"Уверенность: {prediction['confidence']*100}%")
```

#### `StudentAnalyzer`
Класс для сбора и анализа данных студента.

**Методы:**
- `collect_student_data()` - Сбор данных из БД
- `get_trend_analysis()` - Анализ тренда успеваемости
- `get_performance_summary()` - Сводка по производительности

### 2. Django модели

#### `NeuralNetworkModel`
Хранит метаинформацию об обученных моделях:
- `name` - Название модели
- `subject` - Предмет
- `curriculum` - Учебная программа
- `accuracy` - Точность (MAE)
- `training_samples` - Количество студентов, на которых обучалась
- `is_active` - Активна ли модель
- `last_trained` - Дата последнего обучения

#### `GradePrediction`
Хранит предсказания оценок студентов:
- `student_name` - ФИО студента
- `predicted_grade` - Предсказанная оценка
- `confidence` - Уверенность предсказания
- `actual_grade` - Фактическая оценка (для проверки)
- `is_accurate` - Была ли предсказание точным

### 3. Views и URLs

#### Основные маршруты:

| Путь | Функция | Назначение |
|------|---------|-----------|
| `/teacher/neural_network/dashboard/` | `neural_network_dashboard()` | Панель управления нейросетями |
| `/teacher/neural_network/train/<id>/` | `train_neural_network()` | Обучение модели на курсе |
| `/teacher/neural_network/predict/<student>/<curriculum>/` | `predict_student_grade()` | Предсказание оценки студента |
| `/teacher/neural_network/student/<student>/<curriculum>/` | `student_analysis()` | Анализ студента |
| `/teacher/neural_network/models/` | `NeuralNetworkModelListView` | Список всех моделей |
| `/teacher/neural_network/predictions/` | `GradePredictionListView` | Список всех предсказаний |

## Архитектура нейросети

```
Input: 6 признаков
  ↓
Dense(32) + ReLU + Dropout(0.2)
  ↓
Dense(16) + ReLU + Dropout(0.2)
  ↓
Dense(8) + ReLU
  ↓
Dense(1) + Sigmoid
  ↓
Output: Оценка (1-5)
```

### Входные признаки:

1. **previous_grades_avg** - Средняя оценка студента (нормализованная)
2. **attendance_percentage** - Процент посещаемости (0-1)
3. **homework_completion** - Процент выполненных ДЗ (0-1)
4. **test_performance** - Средний балл тестов (0-1)
5. **class_participation** - Участие в классе (0-1)
6. **improvement_trend** - Тренд улучшения (0-1)

## Использование

### Шаг 1: Обучение модели

1. Перейти в `/teacher/neural_network/dashboard/`
2. Выбрать курс
3. Нажать "Обучить модель"
4. Выбрать параметры обучения (эпохи, размер батча)
5. Нажать "Начать обучение"

**Результат:** Модель обучается на данных всех студентов курса и сохраняется в БД.

### Шаг 2: Предсказание оценок

После обучения модель автоматически используется для предсказания оценок студентов:

```python
# Автоматический процесс в views
prediction = predictor.predict(...)
grade_prediction = GradePrediction.objects.create(
    student_name=student_name,
    predicted_grade=prediction['predicted_grade'],
    confidence=prediction['confidence'] * 100,
    # ... другие поля
)
```

### Шаг 3: Проверка точности

Когда получена фактическая оценка студента:

```python
# AJAX запрос для подтверждения
POST /teacher/confirm-grade/
{
    "prediction_id": 123,
    "actual_grade": 4
}
```

Система автоматически проверит, совпадает ли предсказание с фактической оценкой.

## Интеграция с Django панелью администратора

Модели зарегистрированы в админ-панели:

```python
# teacher/admin.py
@admin.register(NeuralNetworkModel)
class NeuralNetworkModelAdmin(admin.ModelAdmin):
    ...

@admin.register(GradePrediction)
class GradePredictionAdmin(admin.ModelAdmin):
    ...
```

### Возможности админ-панели:

- Просмотр обученных моделей
- Фильтрация по предмету, курсу, дате
- Просмотр всех предсказаний
- Проверка точности моделей
- Редактирование фактических оценок

## Метрики и статистика

Для каждой модели отслеживаются:

- **Accuracy Rate** - Процент точных предсказаний
- **MAE (Mean Absolute Error)** - Средняя абсолютная ошибка
- **Average Confidence** - Средняя уверенность предсказаний
- **Training Samples** - Количество примеров обучения

## Технические требования

### Установка зависимостей:

```bash
pip install tensorflow>=2.12.0 scikit-learn>=1.3.0 numpy>=1.24.0
```

### Аппаратные требования:

- **Минимум:** CPU (обучение медленнее)
- **Рекомендуется:** GPU (CUDA совместимая NVIDIA карта для быстрого обучения)

### Системные требования:

- Python 3.8+
- Django 4.2+
- TensorFlow 2.12+

## Ограничения и особенности

1. **Размер модели:** Модель сохраняется как файл в `media/nn_models/`
2. **Обучение:** На 100 студентах обучение занимает ~30-60 секунд (зависит от CPU/GPU)
3. **Точность:** Начальная точность ~60-70%, улучшается с добавлением данных
4. **Диапазон оценок:** Модель обучена на шкале 1-5

## Примеры использования в коде

### Обучение модели программно:

```python
from teacher.models import Grade, TestResult, Curriculum
from teacher.neural_network import StudentPerformancePredictor, StudentAnalyzer

# Получить данные курса
curriculum = Curriculum.objects.get(id=1)
grades = Grade.objects.filter(curriculum=curriculum)
test_results = TestResult.objects.filter(test__curriculum=curriculum)

# Собрать данные по студентам
training_data = []
for student_name in grades.values_list('student_name', flat=True).distinct():
    data = StudentAnalyzer.collect_student_data(student_name, grades, test_results)
    training_data.append({
        'grades': data['grades'],
        'test_scores': data['test_scores'],
        'attendance': data['attendance'],
        'homework_done': data['homework_done'],
        'homework_total': data['homework_total'],
        'expected_grade': np.mean(data['grades'])
    })

# Обучить модель
predictor = StudentPerformancePredictor()
history = predictor.train(training_data, epochs=100)
```

### Получение предсказания для студента:

```python
from teacher.models import GradePrediction
from teacher.neural_network import StudentPerformancePredictor

# Загрузить модель
predictor = StudentPerformancePredictor()
predictor.load_model('path/to/model')

# Получить данные студента
student_data = StudentAnalyzer.collect_student_data(
    'Иван Петров',
    Grade.objects.all(),
    TestResult.objects.all()
)

# Предсказать
prediction = predictor.predict(
    grades_history=student_data['grades'],
    test_scores=student_data['test_scores'],
    attendance=student_data['attendance'],
    homework_done=student_data['homework_done'],
    homework_total=student_data['homework_total']
)

# Сохранить предсказание
GradePrediction.objects.create(
    student_name='Иван Петров',
    subject_id=1,
    curriculum_id=1,
    predicted_grade=prediction['predicted_grade'],
    confidence=prediction['confidence'] * 100,
    **{k: student_data[k] for k in ['average_grade', 'attendance', 'test_average', 'homework_completion']}
)
```

## Решение проблем

### TensorFlow недоступен

```python
# Установить TensorFlow
pip install tensorflow scikit-learn numpy

# Или для CPU версии (меньше размер)
pip install tensorflow-cpu scikit-learn numpy
```

### Модель не обучается

- Убедитесь, что в курсе есть оценки студентов (минимум 5-10 студентов)
- Проверьте, что `expected_grade` в training_data правильно установлен
- Увеличьте количество эпох обучения

### Низкая точность

- Добавьте больше студентов/примеров для обучения
- Убедитесь, что данные оценок корректны
- Переобучите модель с новыми данными
- Проверьте, что все признаки правильно нормализованы

## Будущие улучшения

- [ ] Поддержка LSTM для анализа временных рядов
- [ ] Обучение отдельных моделей для разных классов
- [ ] Визуализация точности модели (графики)
- [ ] Экспорт предсказаний в Excel
- [ ] Уведомления о студентах с низким прогнозом
- [ ] A/B тестирование различных архитектур нейросетей

## Контакты и поддержка

Для вопросов и предложений по развитию системы нейросетей обратитесь к разработчику.
