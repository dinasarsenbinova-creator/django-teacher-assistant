from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Subject(models.Model):
    """Предмет, который может создавать/редактировать педагог"""
    name = models.CharField(max_length=150, unique=True, verbose_name="Название предмета")
    description = models.TextField(blank=True, verbose_name="Описание")
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_subjects",
        verbose_name="Создал",
    )

    class Meta:
        verbose_name = "Предмет"
        verbose_name_plural = "Предметы"

    def __str__(self):
        return self.name


class StudentGroup(models.Model):
    """Группа студентов колледжа"""
    name = models.CharField(max_length=150, verbose_name="Название группы")
    year = models.IntegerField(null=True, blank=True, verbose_name="Год набора")
    # Простая реализация: список студентов как многострочное поле (один студент в строке)
    students = models.TextField(blank=True, verbose_name="Студенты (по одной строке)")
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_groups",
        verbose_name="Создал",
    )

    class Meta:
        verbose_name = "Группа студентов"
        verbose_name_plural = "Группы студентов"

    def __str__(self):
        return self.name


class Curriculum(models.Model):
    """Рабочая программа"""
    title = models.CharField(max_length=200, verbose_name="Название программы")
    subject = models.ForeignKey(
        "Subject",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="curriculums",
        verbose_name="Предмет",
    )
    class_level = models.CharField(
        max_length=10,
        verbose_name="Класс",
        choices=[
            ("1", "1 класс"),
            ("2", "2 класс"),
            ("3", "3 класс"),
            ("4", "4 класс"),
            ("5", "5 класс"),
            ("6", "6 класс"),
            ("7", "7 класс"),
            ("8", "8 класс"),
            ("9", "9 класс"),
            ("10", "10 класс"),
            ("11", "11 класс"),
        ],
    )
    student_group = models.ForeignKey(
        "StudentGroup",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="curriculums",
        verbose_name="Группа студентов",
    )
    year = models.IntegerField(verbose_name="Учебный год")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Рабочая программа"
        verbose_name_plural = "Рабочие программы"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({self.class_level})"


class Topic(models.Model):
    """Темы рабочей программы"""
    curriculum = models.ForeignKey(
        Curriculum,
        on_delete=models.CASCADE,
        related_name="topics",
        verbose_name="Рабочая программа",
    )
    title = models.CharField(max_length=200, verbose_name="Название темы")
    description = models.TextField(blank=True, verbose_name="Описание")
    order = models.IntegerField(default=0, verbose_name="Порядок")
    hours = models.IntegerField(default=1, verbose_name="Количество часов")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Тема"
        verbose_name_plural = "Темы"
        ordering = ["curriculum", "order"]

    def __str__(self):
        return self.title


class Schedule(models.Model):
    """Расписание занятий"""
    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="schedules",
        verbose_name="Педагог",
    )
    subject = models.ForeignKey(
        "Subject",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="schedules",
        verbose_name="Предмет",
    )
    class_name = models.ForeignKey(
        "StudentGroup",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="schedules",
        verbose_name="Группа",
    )
    day_of_week = models.IntegerField(
        choices=[
            (0, "Понедельник"),
            (1, "Вторник"),
            (2, "Среда"),
            (3, "Четверг"),
            (4, "Пятница"),
            (5, "Суббота"),
            (6, "Воскресенье"),
        ],
        verbose_name="День недели",
    )
    start_time = models.TimeField(verbose_name="Время начала")
    end_time = models.TimeField(verbose_name="Время окончания")
    room = models.CharField(max_length=50, blank=True, verbose_name="Кабинет")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Расписание"
        verbose_name_plural = "Расписания"
        ordering = ["day_of_week", "start_time"]

    def __str__(self):
        return f"{self.subject} - {self.class_name} ({self.get_day_of_week_display()})"


class Lesson(models.Model):
    """План урока и материалы"""
    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="lessons",
        verbose_name="Педагог",
    )
    topic = models.ForeignKey(
        Topic,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="lessons",
        verbose_name="Тема",
    )
    curriculum = models.ForeignKey(
        Curriculum,
        on_delete=models.CASCADE,
        related_name="lessons",
        verbose_name="Рабочая программа",
    )
    title = models.CharField(max_length=200, verbose_name="Название урока")
    date = models.DateField(verbose_name="Дата урока")
    class_name = models.ForeignKey(
        "StudentGroup",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="lessons",
        verbose_name="Группа",
    )
    subject = models.ForeignKey(
        "Subject",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="lessons",
        verbose_name="Предмет",
    )
    objectives = models.TextField(blank=True, verbose_name="Цели и задачи")
    materials = models.TextField(blank=True, verbose_name="Материалы и ресурсы")
    content = models.TextField(blank=True, verbose_name="Содержание урока")
    homework = models.TextField(blank=True, verbose_name="Домашнее задание")
    notes = models.TextField(blank=True, verbose_name="Примечания")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"
        ordering = ["-date"]

    def __str__(self):
        return f"{self.title} ({self.date})"


class Grade(models.Model):
    """Оценки учащихся"""
    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="grades",
        verbose_name="Педагог",
    )
    curriculum = models.ForeignKey(
        Curriculum,
        on_delete=models.CASCADE,
        related_name="grades",
        verbose_name="Рабочая программа",
    )
    student_name = models.CharField(max_length=200, verbose_name="ФИО студента")
    class_name = models.ForeignKey(
        "StudentGroup",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="grades",
        verbose_name="Группа",
    )
    subject = models.ForeignKey(
        "Subject",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="grades",
        verbose_name="Предмет",
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="grades",
        verbose_name="Урок",
    )
    grade = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Оценка",
    )
    comment = models.TextField(blank=True, verbose_name="Комментарий")
    date = models.DateField(auto_now_add=True, verbose_name="Дата оценки")
    grade_type = models.CharField(
        max_length=50,
        choices=[
            ("homework", "Домашнее задание"),
            ("classwork", "Классная работа"),
            ("test", "Контрольная работа"),
            ("exam", "Экзамен"),
            ("other", "Прочее"),
        ],
        default="classwork",
        verbose_name="Тип работы",
    )

    class Meta:
        verbose_name = "Оценка"
        verbose_name_plural = "Оценки"
        ordering = ["-date", "student_name"]

    def __str__(self):
        subj = self.subject.name if self.subject else ""
        grp = self.class_name.name if self.class_name else self.class_name
        return f"{self.student_name} - {self.grade} ({subj})"


class Test(models.Model):
    """Тесты и контрольные работы"""
    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="tests",
        verbose_name="Педагог",
    )
    curriculum = models.ForeignKey(
        Curriculum,
        on_delete=models.CASCADE,
        related_name="tests",
        verbose_name="Рабочая программа",
    )
    topic = models.ForeignKey(
        Topic,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tests",
        verbose_name="Тема",
    )
    title = models.CharField(max_length=200, verbose_name="Название")
    description = models.TextField(blank=True, verbose_name="Описание")
    test_type = models.CharField(
        max_length=50,
        choices=[
            ("test", "Тест"),
            ("control_work", "Контрольная работа"),
            ("quiz", "Викторина"),
            ("exam", "Экзамен"),
            ("survey", "Опрос"),
        ],
        default="test",
        verbose_name="Тип проверки",
    )
    subject = models.ForeignKey(
        "Subject",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tests",
        verbose_name="Предмет",
    )
    class_name = models.ForeignKey(
        "StudentGroup",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tests",
        verbose_name="Группа",
    )
    content = models.TextField(verbose_name="Содержание (вопросы/задания)")
    answer_key = models.TextField(blank=True, verbose_name="Ключ ответов")
    max_score = models.IntegerField(default=100, verbose_name="Максимальный балл")
    duration_minutes = models.IntegerField(
        default=45, verbose_name="Продолжительность (минут)"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Тест/Контрольная работа"
        verbose_name_plural = "Тесты/Контрольные работы"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({self.get_test_type_display()})"


class TestResult(models.Model):
    """Результаты тестирования"""
    test = models.ForeignKey(
        Test,
        on_delete=models.CASCADE,
        related_name="results",
        verbose_name="Тест",
    )
    student_name = models.CharField(max_length=200, verbose_name="ФИО ученика")
    score = models.IntegerField(
        validators=[MinValueValidator(0)], verbose_name="Набранный балл"
    )
    percentage = models.FloatField(default=0.0, verbose_name="Процент выполнения")
    comments = models.TextField(blank=True, verbose_name="Комментарии")
    date_completed = models.DateTimeField(auto_now_add=True, verbose_name="Дата сдачи")

    class Meta:
        verbose_name = "Результат теста"
        verbose_name_plural = "Результаты тестов"
        ordering = ["-date_completed"]

    def save(self, *args, **kwargs):
        if self.test.max_score > 0:
            self.percentage = (self.score / self.test.max_score) * 100
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student_name} - {self.score}/{self.test.max_score}"


class NeuralNetworkModel(models.Model):
    """
    Хранилище обученных нейросетевых моделей
    для предсказания оценок студентов
    """
    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="nn_models",
        verbose_name="Педагог",
    )
    subject = models.ForeignKey(
        "Subject",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="nn_models",
        verbose_name="Предмет",
    )
    curriculum = models.ForeignKey(
        "Curriculum",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="nn_models",
        verbose_name="Рабочая программа",
    )
    name = models.CharField(max_length=200, verbose_name="Название модели")
    description = models.TextField(blank=True, verbose_name="Описание")
    model_file = models.FileField(
        upload_to="nn_models/%Y/%m/%d/",
        verbose_name="Файл модели"
    )
    is_active = models.BooleanField(default=True, verbose_name="Активна")
    accuracy = models.FloatField(default=0.0, verbose_name="Точность (MAE)")
    training_samples = models.IntegerField(default=0, verbose_name="Количество примеров обучения")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    last_trained = models.DateTimeField(null=True, blank=True, verbose_name="Последнее обучение")

    class Meta:
        verbose_name = "Нейросетевая модель"
        verbose_name_plural = "Нейросетевые модели"
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.name} ({self.subject})"


class GradePrediction(models.Model):
    """
    Предсказания оценок студентов на основе нейросети
    """
    student_name = models.CharField(max_length=200, verbose_name="ФИО студента")
    subject = models.ForeignKey(
        "Subject",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="predictions",
        verbose_name="Предмет",
    )
    curriculum = models.ForeignKey(
        "Curriculum",
        on_delete=models.CASCADE,
        related_name="predictions",
        verbose_name="Рабочая программа",
    )
    nn_model = models.ForeignKey(
        NeuralNetworkModel,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="predictions",
        verbose_name="Нейросетевая модель",
    )
    predicted_grade = models.FloatField(verbose_name="Предсказанная оценка")
    confidence = models.FloatField(verbose_name="Уверенность (%)")
    average_grade = models.FloatField(verbose_name="Средняя оценка студента")
    attendance = models.FloatField(verbose_name="Посещаемость (%)")
    test_average = models.FloatField(verbose_name="Средний балл теста")
    homework_completion = models.FloatField(verbose_name="Выполнение ДЗ (%)")
    prediction_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата предсказания")
    actual_grade = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Фактическая оценка"
    )
    is_accurate = models.BooleanField(null=True, blank=True, verbose_name="Точное предсказание")

    class Meta:
        verbose_name = "Предсказание оценки"
        verbose_name_plural = "Предсказания оценок"
        ordering = ["-prediction_date"]

    def save(self, *args, **kwargs):
        if self.actual_grade is not None:
            predicted_rounded = round(self.predicted_grade)
            self.is_accurate = abs(predicted_rounded - self.actual_grade) <= 0.5
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student_name} - {self.predicted_grade:.2f} ({self.subject})"


class Quiz(models.Model):
    """Викторина - набор вопросов для проверки знаний"""
    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="quizzes",
        verbose_name="Педагог",
    )
    curriculum = models.ForeignKey(
        Curriculum,
        on_delete=models.CASCADE,
        related_name="quizzes",
        verbose_name="Рабочая программа",
    )
    topic = models.ForeignKey(
        Topic,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="quizzes",
        verbose_name="Тема",
    )
    title = models.CharField(max_length=200, verbose_name="Название викторины")
    description = models.TextField(blank=True, verbose_name="Описание")
    subject = models.ForeignKey(
        "Subject",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="quizzes",
        verbose_name="Предмет",
    )
    class_name = models.ForeignKey(
        "StudentGroup",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="quizzes",
        verbose_name="Группа",
    )
    difficulty = models.CharField(
        max_length=20,
        choices=[
            ("easy", "Легкий"),
            ("medium", "Средний"),
            ("hard", "Сложный"),
        ],
        default="medium",
        verbose_name="Уровень сложности",
    )
    time_limit = models.IntegerField(
        default=15,
        verbose_name="Ограничение времени (минуты)",
        help_text="0 - без ограничения"
    )
    is_active = models.BooleanField(default=True, verbose_name="Активна")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Викторина"
        verbose_name_plural = "Викторины"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def get_questions_count(self):
        """Количество вопросов в викторине"""
        return self.questions.count()

    def get_total_points(self):
        """Общее количество баллов"""
        return sum(question.points for question in self.questions.all())


class QuizQuestion(models.Model):
    """Вопрос викторины"""
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name="questions",
        verbose_name="Викторина",
    )
    question_text = models.TextField(verbose_name="Текст вопроса")
    question_type = models.CharField(
        max_length=20,
        choices=[
            ("single_choice", "Один правильный ответ"),
            ("multiple_choice", "Несколько правильных ответов"),
            ("true_false", "Верно/Неверно"),
            ("short_answer", "Короткий ответ"),
            ("essay", "Эссе"),
        ],
        default="single_choice",
        verbose_name="Тип вопроса",
    )
    options = models.JSONField(
        blank=True,
        null=True,
        verbose_name="Варианты ответов",
        help_text="Для вопросов с вариантами: список строк"
    )
    correct_answer = models.JSONField(
        verbose_name="Правильный ответ",
        help_text="Для single_choice: индекс правильного ответа, для multiple_choice: список индексов, для true_false: true/false, для других: текст ответа"
    )
    explanation = models.TextField(
        blank=True,
        verbose_name="Пояснение",
        help_text="Объяснение правильного ответа"
    )
    points = models.IntegerField(default=1, verbose_name="Баллы за вопрос")
    order = models.IntegerField(default=0, verbose_name="Порядок")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Вопрос викторины"
        verbose_name_plural = "Вопросы викторины"
        ordering = ["quiz", "order"]

    def __str__(self):
        return f"{self.quiz.title} - Вопрос {self.order + 1}"

    def is_correct_answer(self, user_answer):
        """Проверяет правильность ответа пользователя"""
        if self.question_type in ['single_choice', 'multiple_choice']:
            # Для выбора ответов сравниваем списки
            if isinstance(user_answer, list) and isinstance(self.correct_answer, list):
                return sorted(user_answer) == sorted(self.correct_answer)
            return user_answer == self.correct_answer
        elif self.question_type == 'true_false':
            return str(user_answer).lower() == str(self.correct_answer).lower()
        else:
            # Для текстовых ответов - простое сравнение (можно улучшить)
            return str(user_answer).strip().lower() == str(self.correct_answer).strip().lower()


class QuizAttempt(models.Model):
    """Попытка прохождения викторины"""
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name="attempts",
        verbose_name="Викторина",
    )
    student_name = models.CharField(max_length=200, verbose_name="ФИО студента")
    class_name = models.ForeignKey(
        "StudentGroup",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="quiz_attempts",
        verbose_name="Группа",
    )
    answers = models.JSONField(
        verbose_name="Ответы",
        help_text="Словарь: question_id -> ответ"
    )
    score = models.IntegerField(default=0, verbose_name="Набранные баллы")
    max_score = models.IntegerField(default=0, verbose_name="Максимальные баллы")
    percentage = models.FloatField(default=0.0, verbose_name="Процент выполнения")
    time_spent = models.IntegerField(
        default=0,
        verbose_name="Время выполнения (секунды)"
    )
    completed_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата завершения")
    is_completed = models.BooleanField(default=False, verbose_name="Завершена")

    class Meta:
        verbose_name = "Попытка викторины"
        verbose_name_plural = "Попытки викторин"
        ordering = ["-completed_at"]

    def __str__(self):
        return f"{self.student_name} - {self.quiz.title}"

    def calculate_score(self):
        """Рассчитывает баллы за викторину"""
        total_score = 0
        max_score = 0

        for question in self.quiz.questions.all():
            max_score += question.points
            user_answer = self.answers.get(str(question.id))
            if user_answer is not None and question.is_correct_answer(user_answer):
                total_score += question.points

        self.score = total_score
        self.max_score = max_score
        if max_score > 0:
            self.percentage = (total_score / max_score) * 100
        self.save()

        return total_score, max_score
