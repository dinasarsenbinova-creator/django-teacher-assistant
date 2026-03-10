# Структура приложения Ассистент педагога

## 📁 Полная иерархия файлов

```
django_site/
├── .venv/                              # Виртуальное окружение Python
├── db.sqlite3                          # База данных SQLite
├── manage.py                           # Управление Django проектом
│
├── mysite/                             # Конфигурация Django проекта
│   ├── __init__.py
│   ├── settings.py                     # Основные настройки
│   ├── urls.py                         # Главные URL маршруты
│   └── wsgi.py                         # WSGI конфиг для развертывания
│
├── teacher/                            # ГЛАВНОЕ ПРИЛОЖЕНИЕ
│   ├── __init__.py
│   ├── admin.py                        # Админ-интерфейс Django
│   ├── apps.py                         # Конфигурация приложения
│   ├── models.py                       # 8 моделей данных
│   ├── views.py                        # 15+ представлений
│   ├── urls.py                         # URL маршруты приложения
│   │
│   ├── templates/
│   │   └── teacher/
│   │       ├── base.html               # Базовый шаблон (навигация)
│   │       ├── dashboard.html          # Главная панель управления
│   │       │
│   │       ├── curriculum_list.html    # Список программ
│   │       ├── curriculum_detail.html  # Детали программы
│   │       ├── curriculum_form.html    # Форма программы
│   │       │
│   │       ├── schedule_list.html      # Список расписания
│   │       ├── schedule_form.html      # Форма расписания
│   │       │
│   │       ├── lesson_list.html        # Список уроков
│   │       ├── lesson_detail.html      # Детали урока
│   │       ├── lesson_form.html        # Форма урока
│   │       │
│   │       ├── grade_list.html         # Журнал оценок
│   │       ├── grade_form.html         # Форма оценки
│   │       │
│   │       ├── test_list.html          # Список тестов
│   │       ├── test_detail.html        # Детали теста
│   │       └── test_form.html          # Форма теста
│   │
│   ├── migrations/
│   │   ├── __init__.py
│   │   ├── 0001_initial.py             # Начальные таблицы БД
│   │   └── 0002_alter_testresult_score.py  # Изменение полей
│   │
│   └── README.md                       # Документация приложения
│
├── core/                               # Дополнительное приложение
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── views.py
│   ├── urls.py
│   ├── models.py
│   ├── templates/
│   │   └── core/
│   │       └── home.html
│   └── static/
│       └── main/
│
├── main/                               # Вспомогательное приложение
│   ├── __init__.py
│   ├── urls.py
│   ├── views.py
│   ├── templates/
│   │   └── main/
│   │       └── index.html
│   └── static/
│       └── main/
│
├── requirements.txt                    # Зависимости Python
├── setup.bat                           # Быстрый старт (Windows)
├── setup.sh                            # Быстрый старт (Linux/Mac)
├── load_test_data.py                   # Загрузка тестовых данных
├── check_setup.py                      # Проверка установки
│
├── README.md                           # Основная документация
├── README_TEACHER.md                   # Подробное описание функций
├── USER_GUIDE.md                       # Руководство пользователя
└── PROJECT_INFO.py                     # Информация о проекте
```

## 📊 Подробное описание каждого модуля

### 🎯 teacher/models.py

Содержит 8 основных моделей:

```python
1. Curriculum (Рабочая программа)
   ├── title: CharField(200)
   ├── subject: CharField(100)
   ├── class_level: CharField(10) - выбор класса
   ├── year: IntegerField
   ├── created_at: DateTimeField (автоматич)
   └── updated_at: DateTimeField (автоматич)

2. Topic (Тема программы)
   ├── curriculum: ForeignKey(Curriculum)
   ├── title: CharField(200)
   ├── description: TextField
   ├── order: IntegerField
   ├── hours: IntegerField
   └── created_at: DateTimeField

3. Schedule (Расписание)
   ├── teacher: ForeignKey(User)
   ├── subject: CharField(100)
   ├── class_name: CharField(50)
   ├── day_of_week: IntegerField (0-6)
   ├── start_time: TimeField
   ├── end_time: TimeField
   ├── room: CharField(50)
   └── created_at: DateTimeField

4. Lesson (Урок)
   ├── teacher: ForeignKey(User)
   ├── curriculum: ForeignKey(Curriculum)
   ├── topic: ForeignKey(Topic, nullable)
   ├── title: CharField(200)
   ├── date: DateField
   ├── class_name: CharField(50)
   ├── subject: CharField(100)
   ├── objectives: TextField
   ├── materials: TextField
   ├── content: TextField
   ├── homework: TextField
   ├── notes: TextField
   ├── created_at: DateTimeField
   └── updated_at: DateTimeField

5. Grade (Оценка)
   ├── teacher: ForeignKey(User)
   ├── curriculum: ForeignKey(Curriculum)
   ├── student_name: CharField(200)
   ├── class_name: CharField(50)
   ├── subject: CharField(100)
   ├── lesson: ForeignKey(Lesson, nullable)
   ├── grade: IntegerField (1-5)
   ├── comment: TextField
   ├── date: DateField (автоматич)
   ├── grade_type: CharField(50) - выбор типа
   └── (фильтры: по дате, типу, классу)

6. Test (Тест/Контрольная работа)
   ├── teacher: ForeignKey(User)
   ├── curriculum: ForeignKey(Curriculum)
   ├── topic: ForeignKey(Topic, nullable)
   ├── title: CharField(200)
   ├── description: TextField
   ├── test_type: CharField(50) - тип теста
   ├── subject: CharField(100)
   ├── class_name: CharField(50)
   ├── content: TextField - вопросы/задания
   ├── answer_key: TextField
   ├── max_score: IntegerField
   ├── duration_minutes: IntegerField
   ├── created_at: DateTimeField
   └── updated_at: DateTimeField

7. TestResult (Результат теста)
   ├── test: ForeignKey(Test)
   ├── student_name: CharField(200)
   ├── score: IntegerField (≥0)
   ├── percentage: FloatField (автоматич расчет)
   ├── comments: TextField
   └── date_completed: DateTimeField
```

### 📝 teacher/views.py

Представления (Views):

```python
Функции:
- dashboard(request)                    # Главная панель
  └── Показывает статистику и быстрые действия

Классы представлений (CBV):

Curriculum:
- CurriculumListView                    # Список программ
- CurriculumDetailView                  # Детали программы
- CurriculumCreateView                  # Создание программы
- CurriculumUpdateView                  # Редактирование программы

Schedule:
- ScheduleListView                      # Список расписания
- ScheduleCreateView                    # Создание расписания

Lesson:
- LessonListView                        # Список уроков
- LessonCreateView                      # Создание урока
- LessonDetailView                      # Детали урока
- LessonUpdateView                      # Редактирование урока

Grade:
- GradeListView                         # Список оценок (журнал)
- GradeCreateView                       # Добавление оценки

Test:
- TestListView                          # Список тестов
- TestCreateView                        # Создание теста
- TestDetailView                        # Детали теста
- TestUpdateView                        # Редактирование теста

Всего: 1 функция + 14 классов = 15 представлений
```

### 🌐 teacher/urls.py

Маршруты приложения (примеры):

```
/teacher/                               → dashboard
/teacher/curriculum/                    → curriculum_list
/teacher/curriculum/create/             → curriculum_create
/teacher/curriculum/<id>/               → curriculum_detail
/teacher/curriculum/<id>/edit/          → curriculum_update
/teacher/schedule/                      → schedule_list
/teacher/schedule/create/               → schedule_create
/teacher/lessons/                       → lesson_list
/teacher/lessons/create/                → lesson_create
/teacher/lessons/<id>/                  → lesson_detail
/teacher/lessons/<id>/edit/             → lesson_update
/teacher/grades/                        → grade_list
/teacher/grades/add/                    → grade_create
/teacher/tests/                         → test_list
/teacher/tests/create/                  → test_create
/teacher/tests/<id>/                    → test_detail
/teacher/tests/<id>/edit/               → test_update
```

### 🎨 Шаблоны (Templates)

**base.html** (850 строк):
- Навигация с логотипом
- Боковое меню
- Стилизация и CSS
- Блок сообщений об ошибках

**dashboard.html** (150 строк):
- Карточки статистики
- Таблицы с данными
- Быстрые действия
- Адаптивная сетка

**Шаблоны списков** (list.html):
- Таблицы с фильтрацией
- Пагинация
- Кнопки действий
- Поиск

**Шаблоны форм** (form.html):
- Поля ввода
- Выпадающие списки
- Текстовые области
- Валидация

**Шаблоны деталей** (detail.html):
- Красивое отображение данных
- Информационные карточки
- Связанные объекты
- Кнопки редактирования

### 🔧 Утилиты

**load_test_data.py** (150 строк):
- Создание тестового пользователя (teacher/password123)
- Рабочая программа "Математика 5 класс"
- 4 темы с часами
- 5 расписаний
- 4 плана уроков
- 15 оценок для 5 учеников
- 3 теста с результатами

**check_setup.py** (170 строк):
- Проверка БД
- Проверка пользователей
- Проверка установленных приложений
- Красивый вывод статистики
- Инструкции по запуску

**setup.bat / setup.sh**:
- Автоматическое виртуальное окружение
- Установка зависимостей
- Миграции БД
- Загрузка данных

### 📚 Документация

**README.md**: Быстрый старт  
**README_TEACHER.md**: Подробное описание  
**USER_GUIDE.md**: Руководство пользователя  
**PROJECT_INFO.py**: Информация о проекте  
**teacher/README.md**: Документация приложения  

## 🔄 Связи между моделями

```
Curriculum (программа)
├── Topic (темы)
│   ├── Lesson (уроки)
│   │   └── Grade (оценки)
│   └── Test (тесты)
│       └── TestResult (результаты)
├── Lesson (уроки)
│   └── Grade (оценки)
├── Grade (оценки)
└── Test (тесты)

User (педагог) → Schedule, Lesson, Grade, Test
```

## 💾 Хранение данных

- **Формат БД**: SQLite (db.sqlite3)
- **Объем**: ~500 KB с тестовыми данными
- **Таблицы**: 12 основных + 4 системные = 16 таблиц
- **Индексы**: автоматические для ID и ForeignKey

## 🚀 Производительность

- SQL запросы оптимизированы (select_related для внешних ключей)
- Пагинация на 20-50 записей
- Кэширование функций для быстрого доступа
- Минимальный CSS без фреймворков (~3 KB)

## 🔒 Защита данных

- Требуется аутентификация для всех представлений
- Защита от CSRF-атак ({% csrf_token %})
- Валидация данных на сервере
- Данные привязаны к пользователю

---

**Структура спроектирована для простоты и масштабируемости** ✨
