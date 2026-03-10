# 🚀 Быстрый старт нейросетевой системы

## За 5 минут до первого предсказания

### Шаг 1: Установка зависимостей (1 минута)

```bash
cd p:\workspace\django_site
pip install tensorflow scikit-learn numpy
```

### Шаг 2: Применение миграций (1 минута)

```bash
python manage.py migrate
```

### Шаг 3: Запуск сервера (1 минута)

```bash
python manage.py runserver
```

### Шаг 4: Создание тестовых данных (2 минуты)

**Вариант A:** Если у вас уже есть студенты и оценки в системе, переходите к шагу 5.

**Вариант B:** Загрузить примеры данных:
```bash
python load_test_data.py
```

### Шаг 5: Открыть в браузере

Перейти на: **http://localhost:8000/teacher/neural_network/dashboard/**

## 🎯 Первое обучение модели

### Вариант 1: Через веб-интерфейс (рекомендуется)

1. Открыть http://localhost:8000/teacher/neural_network/dashboard/
2. Авторизоваться как педагог
3. Нажать "Все модели" → выбрать курс
4. В рабочей программе нажать "Обучить модель"
5. Установить параметры:
   - Эпохи: **100** (по умолчанию)
   - Размер батча: **8** (по умолчанию)
6. Нажать "Начать обучение"
7. Ждать (обычно 30-60 секунд)
8. Увидеть результат!

### Вариант 2: Через командную строку

```bash
# Обучить модель на программе с ID=1
python manage.py train_neural_network 1

# С параметрами
python manage.py train_neural_network 1 --epochs=150 --batch-size=4
```

## 📊 Первое предсказание

### Вариант 1: Через командную строку

```bash
# Получить список студентов
python manage.py shell
from teacher.models import Grade
students = Grade.objects.values_list('student_name', flat=True).distinct()
for s in students:
    print(s)
exit()

# Предсказать оценку студента
python manage.py predict_grade "Иван Петров" 1 --save
```

### Вариант 2: Через веб-интерфейс

1. В панели управления нейросетями → "Предсказания"
2. Выбрать студента и курс
3. Система автоматически предсказает оценку
4. Введите фактическую оценку для проверки точности

## 🧪 Тестирование

### 1. Проверить, что модель обучена

```bash
python manage.py shell
from teacher.models import NeuralNetworkModel
print(NeuralNetworkModel.objects.count())  # Должно быть > 0
exit()
```

### 2. Проверить предсказания

```bash
python manage.py shell
from teacher.models import GradePrediction
predictions = GradePrediction.objects.all()
for p in predictions[:5]:
    print(f"{p.student_name}: {p.predicted_grade:.2f} (уверенность: {p.confidence:.0f}%)")
exit()
```

### 3. Проверить точность

Открыть админ-панель: http://localhost:8000/admin/

- Перейти на "Предсказания оценок"
- Ввести фактические оценки для проверки
- Система автоматически рассчитает точность

## 📈 Основные маршруты

| URL | Описание |
|-----|---------|
| `/teacher/neural_network/dashboard/` | 📊 Главная панель |
| `/teacher/neural_network/models/` | 🧠 Все модели |
| `/teacher/neural_network/predictions/` | 📈 Все предсказания |
| `/teacher/neural_network/student/<имя>/<id>/` | 👤 Анализ студента |
| `/admin/teacher/neuralnetworkmodel/` | ⚙️ Админ модели |
| `/admin/teacher/gradeprediction/` | ⚙️ Админ предсказания |

## 🔧 Решение частых проблем

### ❌ Ошибка: "No module named 'tensorflow'"

```bash
pip install tensorflow
```

### ❌ Ошибка при миграции

```bash
python manage.py makemigrations teacher
python manage.py migrate
```

### ❌ Модель не обучается

Убедитесь что:
- В курсе есть оценки студентов (минимум 3-5)
- Оценки в диапазоне 1-5
- Тестовые данные загружены (`python load_test_data.py`)

### ❌ Низкая точность модели

```bash
# Переобучить с большим количеством эпох
python manage.py train_neural_network 1 --epochs=200 --batch-size=4
```

## 💡 Советы

1. **Для лучшей точности:** Убедитесь, что у вас 20+ студентов с оценками
2. **Для быстрого обучения:** Уменьшите количество эпох до 50
3. **Для экспериментов:** Используйте сначала малые датасеты
4. **Для мониторинга:** Проверяйте админ-панель на точность предсказаний

## 📚 Документация

- 📖 **[NEURAL_NETWORK_README.md](NEURAL_NETWORK_README.md)** - Обзор системы
- 📘 **[NEURAL_NETWORK_GUIDE.md](NEURAL_NETWORK_GUIDE.md)** - Подробное руководство
- 📕 **[NEURAL_NETWORK_INSTALLATION.md](NEURAL_NETWORK_INSTALLATION.md)** - Установка

## 🎓 Примеры кода

### Обучение модели в Python

```python
from teacher.neural_network import StudentPerformancePredictor
from teacher.models import Grade, TestResult, Curriculum

curriculum = Curriculum.objects.get(id=1)

# Собрать данные (упрощенно)
training_data = [{
    'grades': [4, 3, 4, 5],
    'test_scores': [85, 90, 88],
    'attendance': 95,
    'homework_done': 8,
    'homework_total': 10,
    'expected_grade': 4.0
}]

# Обучить
predictor = StudentPerformancePredictor()
history = predictor.train(training_data, epochs=100)

# Предсказать
prediction = predictor.predict(
    grades_history=[4, 3, 4],
    test_scores=[85, 90],
    attendance=95,
    homework_done=8,
    homework_total=10
)

print(f"Предсказание: {prediction['predicted_grade']}")
print(f"Уверенность: {prediction['confidence']*100}%")
```

### Анализ студента

```python
from teacher.neural_network import StudentAnalyzer

# Собрать данные студента
student_data = StudentAnalyzer.collect_student_data(
    'Иван Петров',
    Grade.objects.all(),
    TestResult.objects.all()
)

# Анализ тренда
trend = StudentAnalyzer.get_trend_analysis(student_data['grades'])
print(f"Тренд: {trend['trend']}")

# Сводка
summary = StudentAnalyzer.get_performance_summary(student_data)
print(f"Средняя оценка: {summary['average_grade']}")
```

## ✅ Контрольный список

- [ ] Установлены зависимости (`pip install tensorflow ...`)
- [ ] Применены миграции (`python manage.py migrate`)
- [ ] Загружены тестовые данные (`python load_test_data.py`)
- [ ] Сервер запущен (`python manage.py runserver`)
- [ ] Дашборд открыт (http://localhost:8000/teacher/neural_network/dashboard/)
- [ ] Модель обучена (`python manage.py train_neural_network 1`)
- [ ] Первое предсказание получено (`python manage.py predict_grade ...`)
- [ ] Точность проверена в админ-панели

## 🎉 Готово!

Система нейросетей полностью готова к использованию. Начните с предсказания оценок и отслеживайте точность моделей в панели управления!

---

**Нужна помощь?** Смотрите полную документацию в [NEURAL_NETWORK_GUIDE.md](NEURAL_NETWORK_GUIDE.md)

**Хотите узнать больше?** Исходный код хорошо задокументирован в [teacher/neural_network.py](teacher/neural_network.py)
