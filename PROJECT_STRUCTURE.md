# 📁 Структура проекта с нейросетевой системой

## Обзор файлов

```
django_site/
│
├─ 📄 README.md                           # Основное описание
├─ 📄 QUICK_START.md                      # ⭐ Быстрый старт (начните отсюда!)
├─ 📄 NEURAL_NETWORK_README.md            # Обзор NN системы
├─ 📄 NEURAL_NETWORK_GUIDE.md             # Подробное руководство
├─ 📄 NEURAL_NETWORK_INSTALLATION.md      # Установка и настройка
│
├─ requirements.txt                       # Зависимости (+ TensorFlow)
├─ manage.py                              # Django management
├─ db.sqlite3                             # База данных
│
├─ mysite/                                # Основная конфигурация Django
│  ├─ settings.py
│  ├─ urls.py
│  ├─ wsgi.py
│  └─ __init__.py
│
├─ core/                                  # Ядро приложения
│  ├─ apps.py
│  ├─ views.py
│  ├─ urls.py
│  ├─ templates/
│  │  └─ core/
│  │     ├─ base.html
│  │     └─ home.html
│  └─ __init__.py
│
├─ main/                                  # Основное приложение
│  ├─ apps.py
│  ├─ views.py
│  ├─ urls.py
│  ├─ static/main/
│  ├─ templates/main/
│  │  └─ index.html
│  └─ __init__.py
│
└─ teacher/                               # 🧠 Приложение педагога (основное)
   │
   ├─ 🧠 НЕЙРОСЕТЕВЫЕ МОДУЛИ
   ├─ neural_network.py                 # ⭐ Основной модуль нейросети
   │  ├─ class StudentPerformancePredictor    # Обучение и предсказание
   │  │  ├─ build_model()                     # Построение архитектуры
   │  │  ├─ train()                           # Обучение модели
   │  │  ├─ predict()                         # Предсказание оценки
   │  │  ├─ save_model()                      # Сохранение
   │  │  └─ load_model()                      # Загрузка
   │  └─ class StudentAnalyzer                # Анализ данных
   │     ├─ collect_student_data()
   │     ├─ get_trend_analysis()
   │     └─ get_performance_summary()
   │
   ├─ neural_network_views.py           # ⭐ Views для NN
   │  ├─ neural_network_dashboard()           # Главная панель
   │  ├─ train_neural_network()               # Обучение через форму
   │  ├─ predict_student_grade()              # AJAX предсказание
   │  ├─ student_analysis()                   # Анализ студента
   │  ├─ confirm_student_grade()              # Подтверждение оценки
   │  ├─ model_statistics()                   # Статистика модели
   │  ├─ NeuralNetworkModelListView           # ListView моделей
   │  ├─ NeuralNetworkModelDetailView         # DetailView модели
   │  └─ GradePredictionListView              # ListView предсказаний
   │
   │ 📚 СТАНДАРТНЫЕ МОДУЛИ
   ├─ models.py                         # Django модели
   │  ├─ Subject                             # Предметы
   │  ├─ StudentGroup                        # Группы студентов
   │  ├─ Curriculum                          # Рабочие программы
   │  ├─ Topic                               # Темы программы
   │  ├─ Schedule                            # Расписание
   │  ├─ Lesson                              # План уроков
   │  ├─ Grade                               # Оценки
   │  ├─ Test                                # Тесты/Контрольные
   │  ├─ TestResult                          # Результаты тестов
   │  ├─ NeuralNetworkModel          ⭐ NEW # Модели нейросети
   │  └─ GradePrediction             ⭐ NEW # Предсказания оценок
   │
   ├─ views.py                          # Стандартные views
   ├─ admin.py                          # Админ-панель (+ NN модели)
   ├─ urls.py                           # Маршруты (+ NN маршруты)
   ├─ apps.py
   │
   │ 🎨 TEMPLATES
   ├─ templates/teacher/
   │  │
   │  ├─ 🧠 НЕЙРОСЕТЕВЫЕ ШАБЛОНЫ
   │  ├─ neural_network/
   │  │  ├─ dashboard.html              ⭐ Панель управления
   │  │  ├─ train.html                  ⭐ Обучение модели
   │  │  ├─ student_analysis.html       ⭐ Анализ студента
   │  │  ├─ model_list.html             ⭐ Список моделей
   │  │  ├─ model_detail.html           ⭐ Детали модели
   │  │  ├─ model_statistics.html       ⭐ Статистика
   │  │  └─ prediction_list.html        ⭐ Предсказания
   │  │
   │  ├─ 📚 СТАНДАРТНЫЕ ШАБЛОНЫ
   │  ├─ base.html
   │  ├─ dashboard.html
   │  ├─ curriculum_list.html
   │  ├─ curriculum_detail.html
   │  ├─ curriculum_form.html
   │  ├─ grade_list.html
   │  ├─ grade_form.html
   │  ├─ lesson_list.html
   │  ├─ lesson_detail.html
   │  ├─ lesson_form.html
   │  ├─ test_list.html
   │  ├─ test_detail.html
   │  ├─ test_form.html
   │  ├─ schedule_list.html
   │  ├─ schedule_form.html
   │  ├─ quick_add_modal.html
   │  └─ teachers neiro/
   │
   │ 📊 МИГРАЦИИ
   ├─ migrations/
   │  ├─ 0001_initial.py
   │  ├─ 0002_alter_testresult_score.py
   │  ├─ 0003_alter_grade_student_name_studentgroup_and_more.py
   │  ├─ 0004_alter_fields_to_fks.py
   │  ├─ 0005_neural_network_models.py  ⭐ NEW (NN модели)
   │  └─ __init__.py
   │
   │ ⚙️ MANAGEMENT КОМАНДЫ
   ├─ management/commands/
   │  ├─ convert_strings_to_fk.py
   │  ├─ train_neural_network.py        ⭐ NEW (Обучение)
   │  ├─ predict_grade.py               ⭐ NEW (Предсказание)
   │  └─ __pycache__/
   │
   │ 📦 PYCACHE
   ├─ __pycache__/
   └─ __init__.py
```

## 📊 Статистика добавленных файлов

### Новые основные файлы (⭐ NEW)

| Файл | Строк | Описание |
|------|-------|---------|
| neural_network.py | 650+ | Ядро нейросети |
| neural_network_views.py | 350+ | Views и AJAX |
| 0005_neural_network_models.py | 100+ | Миграция БД |
| admin.py (добавлено) | 50+ | Админ NN моделей |
| urls.py (добавлено) | 40+ | URL маршруты |

### Новые HTML шаблоны (⭐ NEW)

| Файл | Строк | Описание |
|------|-------|---------|
| dashboard.html | 200+ | Панель управления |
| train.html | 180+ | Обучение модели |
| student_analysis.html | 280+ | Анализ студента |
| model_list.html | 120+ | Список моделей |
| model_detail.html | 150+ | Детали модели |
| model_statistics.html | 200+ | Статистика |
| prediction_list.html | 180+ | Список предсказаний |

### Management команды (⭐ NEW)

| Файл | Строк | Описание |
|------|-------|---------|
| train_neural_network.py | 120+ | Обучение через CLI |
| predict_grade.py | 100+ | Предсказание через CLI |

### Документация (⭐ NEW)

| Файл | Описание |
|------|---------|
| NEURAL_NETWORK_README.md | 📖 Обзор проекта |
| NEURAL_NETWORK_GUIDE.md | 📘 Полное руководство |
| NEURAL_NETWORK_INSTALLATION.md | 📕 Установка и настройка |
| QUICK_START.md | 🚀 Быстрый старт |

## 🔄 Измененные файлы

### models.py (+60 строк)
- Добавлена модель `NeuralNetworkModel`
- Добавлена модель `GradePrediction`

### admin.py (+50 строк)
- Регистрация `NeuralNetworkModelAdmin`
- Регистрация `GradePredictionAdmin`

### urls.py (+40 строк)
- Импорт `neural_network_views`
- 9 новых маршрутов для NN функционала

### requirements.txt (+3 строки)
- tensorflow>=2.12.0
- scikit-learn>=1.3.0
- numpy>=1.24.0

## 📈 Общая статистика

| Метрика | Значение |
|---------|----------|
| Новых строк кода | 1500+ |
| Новых файлов | 13 |
| Django моделей | 2 |
| Views функций | 8 |
| Class-based views | 3 |
| HTML шаблонов | 7 |
| Management команд | 2 |
| URL маршрутов | 9 |
| Документация | 4 файла |

## 🎯 Ключевые компоненты системы

### 1. Ядро нейросети
- **Файл:** `neural_network.py`
- **Классы:** `StudentPerformancePredictor`, `StudentAnalyzer`
- **Функции:** 10+ методов
- **Линий кода:** 650+

### 2. Веб-интерфейс
- **Файл:** `neural_network_views.py`
- **Views:** 8 функций и 3 класса
- **Маршруты:** 9 URL
- **Шаблоны:** 7 HTML файлов
- **Линий кода:** 700+

### 3. Данные и хранилище
- **Модели:** 2 новые Django модели
- **Миграция:** 1 файл миграции
- **Таблицы:** 2 новые таблицы БД
- **Поля:** 20+ полей в моделях

### 4. Автоматизация
- **Management команды:** 2 команды
- **CLI интерфейс:** 2 интерфейса
- **Функции:** Обучение, предсказание

## 🔗 Зависимости между компонентами

```
neural_network.py
    ↓
neural_network_views.py ← models.py (NeuralNetworkModel, GradePrediction)
    ↓
templates/ (7 HTML файлов)
    ↓
admin.py (регистрация моделей)
    ↓
urls.py (маршруты)

management/commands/
    ├─ train_neural_network.py → neural_network.py
    └─ predict_grade.py → neural_network.py
```

## 🚀 Точка входа для новых разработчиков

**Рекомендуемый порядок изучения:**

1. **[QUICK_START.md](QUICK_START.md)** - Быстрый старт за 5 минут
2. **[NEURAL_NETWORK_README.md](NEURAL_NETWORK_README.md)** - Обзор архитектуры
3. **[neural_network.py](neural_network.py)** - Исходный код (хорошо задокументирован)
4. **[neural_network_views.py](neural_network_views.py)** - Web функционал
5. **[NEURAL_NETWORK_GUIDE.md](NEURAL_NETWORK_GUIDE.md)** - Полная документация

## 📦 Требования для запуска

```
Python 3.8+
Django 4.2+
TensorFlow 2.12+
scikit-learn 1.3+
NumPy 1.24+
```

## ✅ Готово к использованию!

Система полностью интегрирована и готова к использованию. Начните с [QUICK_START.md](QUICK_START.md)!
