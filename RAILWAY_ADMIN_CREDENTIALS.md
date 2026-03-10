# 🔐 Данные для входа в админку Railway

После деплоя автоматически создается администратор:

**URL админки:** https://ваш-домен.up.railway.app/admin/

**По умолчанию:**
- **Username:** `admin`
- **Password:** `admin123`

⚠️ **ВАЖНО:** Сразу после первого входа смените пароль в админке!

---

## Как изменить учетные данные

В Railway → Variables добавьте:
```
DJANGO_SUPERUSER_USERNAME=ваш_логин
DJANGO_SUPERUSER_PASSWORD=ваш_пароль
DJANGO_SUPERUSER_EMAIL=ваш_email
```

После добавления переменных, сделайте Redeploy.
