# 🧠 Нейросетевая система для Django сайта

## ⚡ Быстрый старт (1 минута)

```bash
pip install tensorflow scikit-learn numpy
python manage.py migrate
python manage.py runserver
# Откройте: http://localhost:8000/teacher/neural_network/dashboard/
```

## 📚 Документация

### 🚀 Начните с этих документов (в порядке приоритета):

1. **[QUICK_START.md](QUICK_START.md)** ⭐ (5 минут)
   - За 5 минут до первого предсказания
   - Примеры команд
   - Решение проблем

2. **[NEURAL_NETWORK_SUMMARY.md](NEURAL_NETWORK_SUMMARY.md)** (10 минут)
   - Что было создано
   - Статус и готовность
   - Ключевые компоненты

3. **[DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)** (5 минут)
   - Навигация по всей документации
   - Быстрая навигация по задачам

### 📖 Полная документация:

- [NEURAL_NETWORK_README.md](NEURAL_NETWORK_README.md) - Полный обзор системы
- [NEURAL_NETWORK_GUIDE.md](NEURAL_NETWORK_GUIDE.md) - Подробное руководство
- [NEURAL_NETWORK_INSTALLATION.md](NEURAL_NETWORK_INSTALLATION.md) - Установка и настройка
- [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) - Структура проекта
- [CHANGELOG.md](CHANGELOG.md) - Полный список изменений
- [FINAL_CHECKLIST.md](FINAL_CHECKLIST.md) - Финальная проверка

## 🎯 Что это?

Полнофункциональная система на базе **TensorFlow/Keras** для **предсказания оценок студентов** на основе их исторических данных.

### Основные возможности:
✅ Обучение нейросетей на данных студентов  
✅ Предсказание оценок (1-5)  
✅ Web интерфейс + CLI  
✅ Проверка точности  
✅ Админ-панель Django  

## 🚀 Первые команды

```bash
# Обучить модель
python manage.py train_neural_network 1 --epochs=100

# Получить предсказание
python manage.py predict_grade "Иван Петров" 1 --save

# Открыть веб-интерфейс
http://localhost:8000/teacher/neural_network/dashboard/
```

## 📦 Что было добавлено?

```
✅ 2 новых Python модуля (1000+ строк кода)
✅ 7 HTML шаблонов
✅ 2 Management команды
✅ 2 Django модели
✅ 1 миграция БД
✅ 9 URL маршрутов
✅ 6 документов
```

## 💡 Примеры

### Через веб-интерфейс
1. Откройте http://localhost:8000/teacher/neural_network/dashboard/
2. Нажмите "Обучить модель"
3. Установите параметры обучения
4. Получите предсказания

### Через команду
```bash
python manage.py train_neural_network 1
python manage.py predict_grade "Студент" 1 --save
```

### Программно
```python
from teacher.neural_network import StudentPerformancePredictor

predictor = StudentPerformancePredictor()
prediction = predictor.predict(
    grades_history=[4, 3, 4],
    test_scores=[85, 90]
)
```

## 🔍 Где найти что?

| Что ищу | Где найти |
|---------|----------|
| Быстрый старт | [QUICK_START.md](QUICK_START.md) |
| Что было создано | [NEURAL_NETWORK_SUMMARY.md](NEURAL_NETWORK_SUMMARY.md) |
| Полное руководство | [NEURAL_NETWORK_GUIDE.md](NEURAL_NETWORK_GUIDE.md) |
| Установка | [NEURAL_NETWORK_INSTALLATION.md](NEURAL_NETWORK_INSTALLATION.md) |
| Исходный код (ядро) | [teacher/neural_network.py](teacher/neural_network.py) |
| Web интерфейс | [teacher/neural_network_views.py](teacher/neural_network_views.py) |
| Django модели | [teacher/models.py](teacher/models.py) |
| Структура проекта | [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) |
| Изменения | [CHANGELOG.md](CHANGELOG.md) |

## ✅ Требования

```
Python 3.8+
Django 4.2+
TensorFlow 2.12+
scikit-learn 1.3+
NumPy 1.24+
```

## 🎓 Для разных пользователей

**👤 Новичок?** → Прочитайте [QUICK_START.md](QUICK_START.md) (5 мин)

**👨‍💻 Разработчик?** → Изучите [NEURAL_NETWORK_GUIDE.md](NEURAL_NETWORK_GUIDE.md) (30 мин)

**👨‍💼 Администратор?** → Следуйте [NEURAL_NETWORK_INSTALLATION.md](NEURAL_NETWORK_INSTALLATION.md) (20 мин)

## 🚀 Статус

| Компонент | Статус |
|-----------|--------|
| Нейросеть | ✅ Готова |
| Web интерфейс | ✅ Готов |
| CLI команды | ✅ Готовы |
| Документация | ✅ Полная |
| Миграции | ✅ Готовы |
| Админ-панель | ✅ Готова |

**Версия:** 1.0.0  
**Статус:** Production Ready ✓

## 🤝 Интеграция

Система полностью интегрирована с существующим Django проектом:
- Использует существующие модели Django
- Работает с существующей БД
- Интегрирована в админ-панель
- Расширяет существующий функционал

## 📞 Помощь

1. **Не работает?** → [QUICK_START.md](QUICK_START.md#🔧-решение-частых-проблем)
2. **Вопросы?** → [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)
3. **Код?** → [teacher/neural_network.py](teacher/neural_network.py)

---

## 🎉 Готово к использованию!

**Начните здесь:** [QUICK_START.md](QUICK_START.md)

Система полностью создана, интегрирована и документирована. Все готово!
