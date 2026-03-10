# 🚀 Инструкция по деплою Django приложения

## Вариант 1: Railway (Рекомендуется)

### Шаг 1: Подготовка
1. Создайте аккаунт на [railway.app](https://railway.app)
2. Подключите GitHub аккаунт
3. Загрузите проект на GitHub

### Шаг 2: Деплой
1. Нажмите "New Project" → "Deploy from GitHub repo"
2. Выберите ваш репозиторий
3. Railway автоматически определит Django проект

### Шаг 3: Настройка базы данных
1. Нажмите "+ New" → "Database" → "Add PostgreSQL"
2. Railway автоматически установит DATABASE_URL

### Шаг 4: Переменные окружения
Добавьте в настройках проекта:
```
DJANGO_SECRET_KEY=<сгенерируйте случайный ключ>
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=<ваш-домен>.railway.app
PUBLIC_BASE_URL=https://<ваш-домен>.railway.app
OPENAI_API_KEY=<ваш ключ OpenAI, если используете>
```

### Шаг 5: Создание суперпользователя
В Railway CLI:
```bash
railway run python manage.py createsuperuser
```

---

## Вариант 2: Render.com

### Шаг 1: Подготовка
1. Создайте аккаунт на [render.com](https://render.com)
2. Загрузите проект на GitHub

### Шаг 2: Создание Web Service
1. New → Web Service
2. Подключите GitHub репозиторий
3. Настройки:
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
   - **Start Command**: `gunicorn mysite.wsgi:application`

### Шаг 3: Создание PostgreSQL базы
1. New → PostgreSQL
2. Скопируйте Internal Database URL

### Шаг 4: Переменные окружения
```
DJANGO_SECRET_KEY=<случайный ключ>
DJANGO_DEBUG=False
DATABASE_URL=<скопированный URL>
DJANGO_ALLOWED_HOSTS=<ваш-домен>.onrender.com
PUBLIC_BASE_URL=https://<ваш-домен>.onrender.com
OPENAI_API_KEY=<ваш ключ>
```

---

## ⚠️ Важные замечания

### TensorFlow и нейросети
**ВНИМАНИЕ**: TensorFlow занимает много места (~500MB) и может превысить лимиты бесплатных планов.

**Решения:**
1. **Отключить нейросети**: Закомментируйте `tensorflow` в requirements.txt
2. **Использовать платный план**: Railway/Render Pro поддерживают TensorFlow
3. **Альтернатива**: Использовать отдельный сервис для ML (например, AWS Lambda)

### База данных
- Локально используется SQLite, в продакшене - PostgreSQL
- Данные автоматически мигрируются при деплое
- Создайте суперпользователя после деплоя

### Статические файлы
- Обрабатываются через WhiteNoise
- Автоматически собираются при деплое

---

## 🔑 Генерация SECRET_KEY

```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## 🧪 Тестирование локально перед деплоем

```bash
# Установите переменные
set DJANGO_DEBUG=False
set DJANGO_SECRET_KEY=test-key
set DJANGO_ALLOWED_HOSTS=localhost

# Соберите статику
python manage.py collectstatic

# Запустите с gunicorn (нужен WSL или Git Bash)
gunicorn mysite.wsgi
```

---

## 📝 Чек-лист перед деплоем

- [ ] Код загружен на GitHub
- [ ] `.env` добавлен в `.gitignore`
- [ ] SECRET_KEY вынесен в переменные окружения
- [ ] DEBUG=False в продакшене
- [ ] ALLOWED_HOSTS настроены правильно
- [ ] База данных PostgreSQL создана
- [ ] Статические файлы собираются корректно
- [ ] Миграции применены
- [ ] Суперпользователь создан

---

## 🆘 Решение проблем

### Ошибка при установке TensorFlow
Закомментируйте в requirements.txt:
```
# tensorflow>=2.12.0  # Отключено для бесплатного хостинга
```

### Ошибка статических файлов
```bash
python manage.py collectstatic --noinput
```

### Ошибка миграций
```bash
python manage.py migrate --run-syncdb
```

---

## 📞 Полезные ссылки

- [Railway документация](https://docs.railway.app)
- [Render документация](https://render.com/docs)
- [Django deployment checklist](https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/)
