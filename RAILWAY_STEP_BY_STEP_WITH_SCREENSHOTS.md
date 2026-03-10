# Railway: пошаговый деплой Django (с иллюстрациями)

Ниже инструкция именно для вашего проекта `django-teacher-assistant`.

## 0) Что уже должно быть готово

- Репозиторий на GitHub: https://github.com/dinasarsenbinova-creator/django-teacher-assistant.git
- В проекте есть: `Procfile`, `railway.json`, `requirements.txt`, прод-настройки в `mysite/settings.py`

---

## 1) Вход в Railway

1. Откройте Railway: https://railway.app
2. Нажмите **Login with GitHub**
3. Разрешите доступ к вашему GitHub-аккаунту

---

## 2) Создание проекта из GitHub

1. Нажмите **New Project**
2. Выберите **Deploy from GitHub repo**
3. Выберите репозиторий **django-teacher-assistant**

Официальная страница с таким потоком:
- https://docs.railway.com/guides/django#deploy-from-a-github-repo

---

## 3) Добавление PostgreSQL

1. Внутри проекта нажмите **+ New** (или Create)
2. Выберите **Database** → **Add PostgreSQL**
3. Дождитесь статуса `Running`

Документация:
- https://docs.railway.com/guides/django#deploy-from-a-github-repo

---

## 4) Переменные окружения (самый важный шаг)

Откройте ваш Django service → вкладка **Variables** → **Raw Editor** и добавьте:

```env
DJANGO_SECRET_KEY=ykz4l)((g-lv23ql7#-925ra!x&*k@vnw4ob&3@0kf&5nm8w(g
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=${{RAILWAY_PUBLIC_DOMAIN}}
PUBLIC_BASE_URL=https://${{RAILWAY_PUBLIC_DOMAIN}}
```

Если используете OpenAI в проекте, добавьте:

```env
OPENAI_API_KEY=ваш_ключ
```

Подсказка по переменным Railway:
- https://docs.railway.com/variables/reference

---

## 5) Публичный домен

1. Откройте Django service
2. Перейдите в **Settings** → **Networking**
3. Нажмите **Generate Domain**
4. Скопируйте домен вида `xxxx.up.railway.app`

Документация:
- https://docs.railway.com/networking/public-networking

---

## 6) Перезапуск деплоя

После добавления переменных:

1. Откройте вкладку **Deployments**
2. Нажмите **Redeploy** (или Deploy)
3. Дождитесь статуса `SUCCESS`

Проверка логов:
- В **Logs** не должно быть ошибок `ModuleNotFoundError`, `DisallowedHost`, `OperationalError`.

---

## 7) Создание администратора Django

В Railway для вашего Django service откройте Shell/Console и выполните:

```bash
python manage.py createsuperuser
```

После этого войдите в админку:
- `https://ваш-домен/admin/`

---

## 8) Проверка сайта

Откройте:

- Главная: `https://ваш-домен/`
- Учитель: `https://ваш-домен/teacher/`
- Админка: `https://ваш-домен/admin/`

---

## Иллюстрации (официальные скриншоты Railway)

### A) Пример запущенного Django-приложения

![Django app screenshot](https://res.cloudinary.com/railway/image/upload/v1729121823/docs/quick-start/django_app.png)

Источник:
- https://docs.railway.com/guides/django

### B) Архитектура проекта (app + database)

![Django architecture screenshot](https://res.cloudinary.com/railway/image/upload/f_auto,q_auto/v1731604331/docs/quick-start/deployed_django_app_architecture.png)

Источник:
- https://docs.railway.com/guides/django

---

## Частые ошибки и быстрые решения

1. **Application failed to respond**
   - Проверьте, что старт-команда корректна (`gunicorn mysite.wsgi:application`)
   - Проверьте логи запуска

2. **DisallowedHost**
   - Убедитесь, что `DJANGO_ALLOWED_HOSTS=${{RAILWAY_PUBLIC_DOMAIN}}`

3. **Ошибка сборки из-за TensorFlow**
   - На бесплатном плане большой ML-стек может не пройти по лимитам
   - Временно держите `tensorflow` отключенным в `requirements.txt`

4. **Статика не грузится**
   - Проверьте WhiteNoise и `collectstatic` в build/deploy шагах

---

## Мини-чеклист

- [ ] Проект создан из GitHub
- [ ] PostgreSQL добавлен
- [ ] Переменные окружения добавлены
- [ ] Домен сгенерирован
- [ ] Деплой успешный
- [ ] `createsuperuser` выполнен
- [ ] Сайт открывается по публичному URL
