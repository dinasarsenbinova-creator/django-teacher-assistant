# Установка и настройка нейросетевых моделей

## Требования

- Python 3.8+
- Django 4.2+
- Pip или другой менеджер пакетов Python

## Шаг 1: Установка зависимостей

```bash
# Перейти в директорию проекта
cd p:\workspace\django_site

# Установить TensorFlow и зависимости для нейросетей
pip install tensorflow>=2.12.0 scikit-learn>=1.3.0 numpy>=1.24.0

# Или установить все из requirements.txt
pip install -r requirements.txt
```

### Опционально: Установка GPU поддержки (NVIDIA CUDA)

Для ускорения обучения моделей на графических картах:

```bash
# Установить CUDA версию TensorFlow
pip install tensorflow[and-cuda]
```

## Шаг 2: Применение миграций

```bash
# Создать новые таблицы в БД
python manage.py migrate

# Если возникают ошибки, попробуйте:
python manage.py makemigrations teacher
python manage.py migrate
```

## Шаг 3: Сбор статических файлов

```bash
python manage.py collectstatic --noinput
```

## Шаг 4: Создание суперпользователя (если еще не создан)

```bash
python manage.py createsuperuser
```

## Проверка установки

### 1. Запустить тестовый сервер

```bash
python manage.py runserver
```

Перейти на http://localhost:8000/admin и проверить, что админ-панель работает.

### 2. Проверить наличие моделей

```python
python manage.py shell

# В интерпретаторе Python:
from teacher.models import NeuralNetworkModel, GradePrediction
print("NeuralNetworkModel:", NeuralNetworkModel.objects.count())
print("GradePrediction:", GradePrediction.objects.count())
exit()
```

### 3. Тест импорта нейросети

```python
python manage.py shell

# В интерпретаторе Python:
from teacher.neural_network import StudentPerformancePredictor, StudentAnalyzer
predictor = StudentPerformancePredictor()
print("✓ Импорт успешен!")
exit()
```

## Использование

### Способ 1: Через веб-интерфейс

1. Перейти на http://localhost:8000/teacher/
2. Авторизоваться как педагог
3. Открыть "Нейросетевые модели" в боковом меню
4. Выбрать курс и нажать "Обучить модель"

### Способ 2: Через Django management команды

#### Обучение модели

```bash
python manage.py train_neural_network 1 --epochs=100 --batch-size=8 --teacher-id=1
```

Параметры:
- `1` - ID учебной программы (Curriculum)
- `--epochs` - Количество эпох обучения (по умолчанию 100)
- `--batch-size` - Размер батча (по умолчанию 8)
- `--teacher-id` - ID педагога (опционально)

**Пример:**
```bash
python manage.py train_neural_network 1 --epochs=50 --batch-size=16
```

#### Предсказание оценки студента

```bash
python manage.py predict_grade "Иван Петров" 1 --model-id=1 --save
```

Параметры:
- `"Иван Петров"` - ФИО студента
- `1` - ID учебной программы
- `--model-id` - ID модели (опционально, будет выбрана последняя)
- `--save` - Сохранить предсказание в БД

**Пример:**
```bash
python manage.py predict_grade "Мария Сидорова" 1 --save
```

### Способ 3: Программно в коде

```python
from teacher.neural_network import StudentPerformancePredictor, StudentAnalyzer
from teacher.models import Curriculum, Grade, TestResult

# Получить данные
curriculum = Curriculum.objects.get(id=1)
grades = Grade.objects.filter(curriculum=curriculum)
tests = TestResult.objects.filter(test__curriculum=curriculum)

# Обучить модель
training_data = [
    {
        'grades': [4, 3, 4],
        'test_scores': [85, 90],
        'attendance': 95,
        'homework_done': 8,
        'homework_total': 10,
        'expected_grade': 3.67
    }
]

predictor = StudentPerformancePredictor()
history = predictor.train(training_data, epochs=100)

# Предсказать оценку
prediction = predictor.predict(
    grades_history=[4, 3, 4],
    test_scores=[85, 90],
    attendance=95,
    homework_done=8,
    homework_total=10
)

print(f"Предсказанная оценка: {prediction['predicted_grade']}")
```

## Структура файлов

```
django_site/
├── teacher/
│   ├── neural_network.py              # Основной модуль с классами нейросети
│   ├── neural_network_views.py        # Views для работы с нейросетями
│   ├── models.py                      # Django модели (включая NN модели)
│   ├── admin.py                       # Админ-панель для NN моделей
│   ├── urls.py                        # URLs для NN эндпоинтов
│   ├── management/
│   │   └── commands/
│   │       ├── train_neural_network.py  # Команда для обучения
│   │       └── predict_grade.py         # Команда для предсказания
│   ├── templates/
│   │   └── teacher/
│   │       └── neural_network/
│   │           ├── dashboard.html            # Главная панель
│   │           ├── train.html                # Страница обучения
│   │           ├── student_analysis.html     # Анализ студента
│   │           ├── model_list.html           # Список моделей
│   │           ├── model_detail.html         # Детали модели
│   │           ├── model_statistics.html     # Статистика модели
│   │           └── prediction_list.html      # Список предсказаний
│   └── migrations/
│       └── 0005_neural_network_models.py     # Миграция для NN моделей
├── requirements.txt                   # Зависимости проекта
├── NEURAL_NETWORK_GUIDE.md            # Подробное руководство
└── README.md                          # Основной README
```

## Файлы моделей

Обученные модели сохраняются в директории:
```
media/nn_models/YYYY/MM/DD/
```

Каждая модель состоит из двух файлов:
- `{model_id}_model.h5` - Веса и архитектура нейросети (TensorFlow)
- `{model_id}_model_scaler.json` - Параметры нормализации данных

## Устранение проблем

### Проблема: "No module named 'tensorflow'"

**Решение:**
```bash
pip install tensorflow
```

### Проблема: "OutOfMemory при обучении"

**Решение:** Уменьшите размер батча:
```bash
python manage.py train_neural_network 1 --batch-size=4 --epochs=50
```

### Проблема: Модель не предсказывает

**Решение:** Проверьте, что модель обучена и активна:
```python
from teacher.models import NeuralNetworkModel
models = NeuralNetworkModel.objects.filter(is_active=True)
print(models)  # Должен вывести список моделей
```

### Проблема: Низкая точность модели

**Решение:**
1. Убедитесь, что у вас достаточно студентов (минимум 20-30)
2. Проверьте корректность данных оценок
3. Переобучите модель с большим количеством эпох
4. Проверьте, что все оценки в диапазоне 1-5

## Оптимизация

### Для быстрого обучения:

```bash
# Меньше эпох, больше примеров в батче
python manage.py train_neural_network 1 --epochs=50 --batch-size=32
```

### Для лучшей точности:

```bash
# Больше эпох, меньший батч
python manage.py train_neural_network 1 --epochs=200 --batch-size=4
```

## Безопасность

- Модели сохраняются в `media/` директории (защитите от доступа)
- Предсказания видны только педагогам
- Данные студентов используются только для обучения, не передаются третьим лицам

## Лицензирование

Этот код использует:
- TensorFlow (Apache 2.0)
- scikit-learn (BSD 3-Clause)
- Django (BSD 3-Clause)
- NumPy (BSD 3-Clause)

## Поддержка и вопросы

Для более подробной информации см. [NEURAL_NETWORK_GUIDE.md](NEURAL_NETWORK_GUIDE.md)

## Тестирование

Создан набор примеров данных для тестирования:

```bash
# Загрузить тестовые данные
python load_test_data.py
```

После этого вы сможете:
1. Обучить модель: `python manage.py train_neural_network 1`
2. Сделать предсказание: `python manage.py predict_grade "Иван Петров" 1 --save`
3. Проверить результаты в админ-панели
