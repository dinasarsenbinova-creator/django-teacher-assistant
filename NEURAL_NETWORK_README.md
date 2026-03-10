# 🧠 Нейросетевая система предсказания оценок

## 📋 Описание

Полнофункциональная система на основе нейросетей (TensorFlow/Keras) для предсказания оценок студентов в образовательной платформе Django. Система анализирует исторические данные студентов (оценки, тесты, домашние задания, посещаемость) и предсказывает будущие оценки с указанием уверенности предсказания.

## ✨ Основные возможности

### 1. **Обучение моделей**
   - Автоматический сбор данных студентов из БД
   - Обучение глубокой нейросети на 6 входных признаках
   - Сохранение обученных моделей в файл
   - Отслеживание точности (MAE) и метрик обучения

### 2. **Предсказание оценок**
   - Предсказание оценок студентов (1-5) с вероятностью
   - Использование множественных параметров: история оценок, тесты, ДЗ, посещаемость
   - Анализ тренда улучшения/снижения успеваемости
   - Сохранение предсказаний в БД для проверки точности

### 3. **Аналитика и статистика**
   - Панель управления с общей статистикой моделей
   - Детальный анализ каждого студента
   - Проверка точности предсказаний
   - Визуализация тренда успеваемости
   - Рейтинг моделей по точности

### 4. **Интеграция с Django**
   - Полная интеграция с админ-панелью Django
   - Web интерфейс для управления моделями
   - REST-подобные AJAX эндпоинты
   - Management команды для автоматизации

## 🗂️ Структура реализации

### Файлы ядра системы

| Файл | Описание | Размер |
|------|---------|---------|
| [teacher/neural_network.py](teacher/neural_network.py) | Классы для работы с нейросетью | 650+ строк |
| [teacher/neural_network_views.py](teacher/neural_network_views.py) | Views и AJAX эндпоинты | 350+ строк |
| [teacher/models.py](teacher/models.py) | Django модели (добавлены) | 60+ строк |
| [teacher/admin.py](teacher/admin.py) | Админ-панель (добавлено) | 50+ строк |

### Templates (6 HTML файлов)

1. **dashboard.html** - Главная панель управления нейросетями
2. **train.html** - Интерфейс обучения модели с прогресс-баром
3. **student_analysis.html** - Детальный анализ студента с прогнозом
4. **model_list.html** - Список обученных моделей
5. **model_detail.html** - Детали модели и архитектура
6. **model_statistics.html** - Статистика и метрики модели
7. **prediction_list.html** - Все предсказания с сортировкой

### Management команды (2 файла)

1. **train_neural_network.py** - Обучение модели
   ```bash
   python manage.py train_neural_network <curriculum_id> --epochs=100 --batch-size=8
   ```

2. **predict_grade.py** - Предсказание оценки студента
   ```bash
   python manage.py predict_grade "Иван Петров" <curriculum_id> --save
   ```

## 🧮 Архитектура нейросети

```
Входные данные (6 признаков)
        ↓
[Dense(32) → ReLU → Dropout(0.2)]
        ↓
[Dense(16) → ReLU → Dropout(0.2)]
        ↓
[Dense(8) → ReLU]
        ↓
[Dense(1) → Sigmoid]
        ↓
Выход: Оценка 1-5
```

### Входные признаки:
1. **Средняя историческая оценка** - История оценок студента
2. **Посещаемость** - Процент посещаемости занятий
3. **Выполнение ДЗ** - Процент выполненных домашних заданий
4. **Результаты тестов** - Средний балл тестирования
5. **Участие в классе** - Активность студента
6. **Тренд улучшения** - Направление изменения успеваемости

## 📊 Django модели

### NeuralNetworkModel
```python
- name: CharField                    # Название модели
- subject: ForeignKey(Subject)       # Предмет
- curriculum: ForeignKey(Curriculum) # Учебная программа
- teacher: ForeignKey(User)          # Педагог-владелец
- accuracy: FloatField               # Точность (MAE)
- training_samples: IntegerField     # Количество примеров
- is_active: BooleanField            # Активна ли модель
- created_at, updated_at: DateTime   # Даты
```

### GradePrediction
```python
- student_name: CharField            # ФИО студента
- predicted_grade: FloatField        # Предсказанная оценка (1-5)
- confidence: FloatField             # Уверенность (0-100%)
- actual_grade: IntegerField         # Фактическая оценка (для проверки)
- is_accurate: BooleanField          # Была ли точна
- average_grade, attendance, etc     # Контекстные показатели
```

## 🔗 URL маршруты

```
/teacher/neural_network/dashboard/              → Панель управления
/teacher/neural_network/models/                 → Список моделей
/teacher/neural_network/models/<id>/            → Детали модели
/teacher/neural_network/models/<id>/statistics/ → Статистика модели
/teacher/neural_network/train/<curriculum_id>/ → Обучение
/teacher/neural_network/predictions/            → Список предсказаний
/teacher/neural_network/student/<name>/<id>/   → Анализ студента
/teacher/predict/<name>/<curriculum_id>/       → AJAX: Предсказание
/teacher/confirm-grade/                        → AJAX: Подтверждение оценки
```

## 📦 Зависимости

```txt
Django>=4.2
tensorflow>=2.12.0
scikit-learn>=1.3.0
numpy>=1.24.0
```

## 🚀 Быстрый старт

### 1. Установка
```bash
pip install tensorflow scikit-learn numpy
python manage.py migrate
```

### 2. Обучение модели
```bash
python manage.py train_neural_network 1 --epochs=100
```

### 3. Предсказание оценки
```bash
python manage.py predict_grade "Студент ФИ" 1 --save
```

### 4. Открыть в браузере
```
http://localhost:8000/teacher/neural_network/dashboard/
```

## 📈 Примеры использования

### Программный интерфейс

```python
from teacher.neural_network import StudentPerformancePredictor

predictor = StudentPerformancePredictor()
predictor.train([...])  # Обучение
prediction = predictor.predict(  # Предсказание
    grades_history=[4, 3, 4],
    test_scores=[85, 90],
    attendance=95
)
print(f"Оценка: {prediction['predicted_grade']}")  # 3.85
```

### Web интерфейс

1. Обучение через форму с параметрами
2. Просмотр прогрессбара обучения в реальном времени
3. Анализ студента с визуализацией тренда
4. Подтверждение предсказаний при получении реальных оценок

## 📊 Статистика проекта

| Метрика | Значение |
|---------|---------|
| Строк кода | 1500+ |
| Django моделей | 2 (новых) |
| Views функций | 8 |
| HTML шаблонов | 7 |
| Management команд | 2 |
| URL маршрутов | 9 |

## ✅ Особенности

✓ Полная интеграция с Django ORM  
✓ Автоматическое сохранение и загрузка моделей  
✓ Нормализация входных данных  
✓ Обработка ошибок и валидация  
✓ CSRF защита для AJAX  
✓ Пагинация списков  
✓ Фильтры в админ-панели  
✓ Детальная документация  

## 📚 Документация

- [NEURAL_NETWORK_GUIDE.md](NEURAL_NETWORK_GUIDE.md) - Подробное руководство
- [NEURAL_NETWORK_INSTALLATION.md](NEURAL_NETWORK_INSTALLATION.md) - Установка и настройка
- [Inline документация](teacher/neural_network.py) - Доскомент функций

## 🔮 Будущие улучшения

- [ ] LSTM модели для временных рядов
- [ ] Множественные модели для разных классов
- [ ] Визуализация графиков TensorBoard
- [ ] Экспорт в Excel/PDF
- [ ] Уведомления о низких прогнозах
- [ ] A/B тестирование моделей
- [ ] Автоматическое переобучение

## ⚙️ Технические детали

**Язык:** Python 3.8+  
**Framework:** Django 4.2+  
**ML Framework:** TensorFlow 2.12+  
**БД:** SQLite/PostgreSQL  
**Frontend:** Bootstrap 5, AJAX  

## 📝 Лицензия

Использует open-source библиотеки:
- TensorFlow (Apache 2.0)
- scikit-learn (BSD 3-Clause)
- Django (BSD 3-Clause)

---

**Создано:** 2024  
**Версия:** 1.0.0  
**Статус:** Production Ready ✓
