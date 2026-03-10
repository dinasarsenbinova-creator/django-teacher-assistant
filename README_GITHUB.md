# 🎓 Django Teacher Assistant

Веб-приложение для автоматизации работы учителя: управление учебными планами, создание викторин, генерация домашних заданий и анализ успеваемости с помощью нейросетей.

## ✨ Возможности

- 📚 Управление учебными планами и уроками
- 📝 Создание и проведение викторин для студентов
- 🤖 Генерация домашних заданий через OpenAI
- 🧠 Предсказание оценок студентов с помощью нейронных сетей (TensorFlow)
- 👥 Управление группами студентов
- 📊 Анализ успеваемости

## 🚀 Деплой

Подробная инструкция в [DEPLOY_INSTRUCTIONS.md](DEPLOY_INSTRUCTIONS.md)

### Быстрый старт с Railway:
1. Форкните этот репозиторий
2. Зарегистрируйтесь на [railway.app](https://railway.app)
3. New Project → Deploy from GitHub repo
4. Добавьте PostgreSQL базу данных
5. Настройте переменные окружения (см. `.env.example`)

## 💻 Локальная разработка

### Требования
- Python 3.11+
- Django 4.2+

### Установка

```bash
# Клонируйте репозиторий
git clone <your-repo-url>
cd django_site

# Создайте виртуальное окружение (Windows)
python -m venv .venv
.venv\Scripts\activate

# Установите зависимости
pip install -r requirements.txt

# Примените миграции
python manage.py migrate

# Создайте суперпользователя
python manage.py createsuperuser

# Запустите сервер
python manage.py runserver
```

Откройте http://127.0.0.1:8000/teacher/

## 🔧 Настройка

Скопируйте `.env.example` в `.env` и настройте:

```bash
DJANGO_SECRET_KEY=ваш-секретный-ключ
DJANGO_DEBUG=True
OPENAI_API_KEY=ваш-ключ-openai  # Опционально
```

## 📦 Технологии

- **Backend**: Django 4.2
- **Database**: SQLite (локально), PostgreSQL (продакшен)
- **ML**: TensorFlow 2.12, scikit-learn
- **AI**: OpenAI API для генерации заданий
- **Deployment**: Railway/Render ready

## ⚠️ Примечания

- TensorFlow требует ~500MB, может превысить лимиты бесплатного хостинга
- Для продакшена рекомендуется отключить TensorFlow или использовать платный план
- OpenAI API требует ключ для генерации домашних заданий

## 📝 Лицензия

MIT License

## 👨‍💻 Автор

Проект для автоматизации работы учителей
