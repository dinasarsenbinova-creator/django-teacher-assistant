# Функция определения победителей викторины

## Описание
По окончании викторины система автоматически определяет трех лучших участников на основе:
1. **Процента выполнения** (главный критерий) - чем выше, тем лучше
2. **Времени выполнения** (критерий тай-брейк) - при равном проценте выбирается тот, кто быстрее прошел

## Как это работает

### Backend (Python/Django)

#### Функция `_get_quiz_winners(quiz)` в [teacher/views.py](teacher/views.py)

```python
def _get_quiz_winners(quiz):
    """
    Определяет трех победителей викторины.
    Критерии сортировки:
    1. Процент выполнения (выше лучше)
    2. Время выполнения (меньше лучше)
    """
    attempts = quiz.attempts.all()
    
    if not attempts.exists():
        return []
    
    # Группируем попытки по студентам и берем лучший результат каждого
    participants_map = {}
    for attempt in attempts:
        name = attempt.student_name or 'Неизвестный'
        if name not in participants_map:
            participants_map[name] = attempt
        else:
            # Обновляем если найдена лучшая попытка
            existing = participants_map[name]
            if attempt.percentage > existing.percentage:
                participants_map[name] = attempt
            elif attempt.percentage == existing.percentage and attempt.time_spent < existing.time_spent:
                participants_map[name] = attempt
    
    # Сортируем по проценту (убывание) и времени (возрастание)
    winners = sorted(
        participants_map.values(),
        key=lambda x: (-x.percentage, x.time_spent)
    )[:3]
    
    return winners
```

#### Обновленная функция `quiz_participants(request, pk)` 

Передает `winners` в контекст шаблона:

```python
def quiz_participants(request, pk):
    """Список участников викторины и их результаты."""
    quiz = get_object_or_404(Quiz, pk=pk, teacher=request.user)
    participants, attempts = _build_quiz_participants_data(quiz)
    winners = _get_quiz_winners(quiz)  # ← Новая строка

    context = {
        'quiz': quiz,
        'attempts': attempts,
        'participants': participants,
        'participants_count': len(participants),
        'attempts_count': attempts.count(),
        'winners': winners,  # ← Передаем в контекст
    }
    return render(request, 'teacher/quiz_participants.html', context)
```

### Frontend (HTML/CSS)

#### Шаблон победителей в [quiz_participants.html](teacher/templates/teacher/quiz_participants.html)

Отображение оформлено в виде трех карточек с эмодзи-кубками:

**1-е место (🥇 Золотой кубок)**
- Увеличен размер (transform: scale(1.05))
- Золотой цвет текста (#ffd700)
- Поздравление: "Поздравляем! 🎉 Вы лучший!"

**2-е место (🥈 Серебряный кубок)**
- Серебристый цвет (#c0c0c0)
- Поздравление: "Отличный результат! 👏 Очень хорошо!"

**3-е место (🥉 Бронзовый кубок)**
- Бронзовый цвет (#cd7f32)
- Поздравление: "Хороший результат! 👍 Продолжайте так!"

Каждая карточка показывает:
- ФИ студента
- Баллы (текущие/максимум)
- Процент выполнения
- Время выполнения (в секундах)

### Структура данных QuizAttempt

Использует существующие поля модели:
```python
class QuizAttempt(models.Model):
    ...
    student_name = models.CharField(max_length=200)
    score = models.IntegerField(default=0)
    max_score = models.IntegerField(default=0)
    percentage = models.FloatField(default=0.0)
    time_spent = models.IntegerField(default=0)  # в секундах
    completed_at = models.DateTimeField(auto_now_add=True)
```

## Пример отображения

При посещении страницы участников викторины (URL: `/teacher/quiz/<id>/participants/`):

```
🏆 Победители 🏆
┌─────────────────┬─────────────────┬─────────────────┐
│       🥇        │       🥈        │       🥉        │
│   1 место       │   2 место       │   3 место       │
│                 │                 │                 │
│ Иван Петров     │ Мария Сидорова  │ Петр Иванов     │
│ Баллы: 9/10     │ Баллы: 8/10     │ Баллы: 7/10     │
│ Результат: 90%  │ Результат: 80%  │ Результат: 70%  │
│ Время: 145с     │ Время: 210с     │ Время: 298с     │
│                 │                 │                 │
│ Поздравляем! 🎉 │ Отличный! 👏   │ Хороший! 👍     │
│ Вы лучший!      │ Очень хорошо!   │ Продолжайте!    │
└─────────────────┴─────────────────┴─────────────────┘
```

## Интеграция с существующей системой

✅ Работает с существующей моделью `QuizAttempt`
✅ Интегрирована в страницу участников викторины
✅ Использует существующие поля (percentage, time_spent, score, max_score)
✅ Совместима с live-обновлением данных (5-секундный polling)
✅ Показывает только при наличии попыток (`{% if winners %}`)

## Файлы, которые были изменены

1. **[teacher/views.py](teacher/views.py)**
   - Добавлена функция `_get_quiz_winners(quiz)`
   - Обновлена функция `quiz_participants(request, pk)` для передачи winners в контекст
   - Обновлена функция `_build_quiz_participants_data()` для отслеживания best_time

2. **[teacher/templates/teacher/quiz_participants.html](teacher/templates/teacher/quiz_participants.html)**
   - Добавлена секция с победителями после заголовка
   - 3 карточки с эмодзи-кубками и поздравлениями
   - CSS стили для оформления и градиентного фона

## Тестирование

Для тестирования:
1. Создайте викторину с несколькими вопросами
2. Дайте студентам/друзьям пройти викторину несколько раз с разными результатами
3. Откройте страницу "Участники" викторины
4. Увидите топ-3 победителей с кубками и поздравлениями

**Проверяемые сценарии:**
- ✅ Без попыток - раздел не отображается
- ✅ 1 попытка - показывает 1 победителя
- ✅ 2-3 попытки - показывает только присутствующих
- ✅ Множество попыток - выбирает лучший результат каждого студента
- ✅ Равные проценты - тай-брейк по времени работает

## Будущие улучшения

- Кэширование расчета победителей (если много попыток)
- Экспорт результатов в CSV/PDF
- Сертификат для победителей
- Повторные награды за участие в разных викторинах
- Отправка уведомлений победителям
