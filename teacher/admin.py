from django.contrib import admin
from .models import (
    Curriculum,
    Topic,
    Schedule,
    Lesson,
    Grade,
    Test,
    TestResult,
    Subject,
    StudentGroup,
    NeuralNetworkModel,
    GradePrediction,
    Quiz,
    QuizQuestion,
    QuizAttempt,
)


@admin.register(Curriculum)
class CurriculumAdmin(admin.ModelAdmin):
    list_display = ["title", "subject", "class_level", "year", "created_at"]
    list_filter = ["class_level", "year", "subject"]
    search_fields = ["title", "subject__name"]
    ordering = ["-created_at"]


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ["title", "curriculum", "order", "hours", "created_at"]
    list_filter = ["curriculum", "curriculum__subject"]
    search_fields = ["title", "curriculum__title"]
    ordering = ["curriculum", "order"]


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = [
        "subject",
        "class_name",
        "get_day_of_week",
        "start_time",
        "end_time",
        "room",
    ]
    list_filter = ["day_of_week", "subject", "class_name"]
    search_fields = ["subject__name", "class_name__name", "room"]
    ordering = ["day_of_week", "start_time"]

    def get_day_of_week(self, obj):
        return obj.get_day_of_week_display()

    get_day_of_week.short_description = "День недели"


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ["title", "subject", "class_name", "date", "topic", "curriculum"]
    list_filter = ["date", "subject", "class_name", "curriculum"]
    search_fields = ["title", "subject__name", "class_name__name"]
    ordering = ["-date"]
    fieldsets = (
        ("Основная информация", {"fields": ("title", "curriculum", "topic")}),
        ("Класс и предмет", {"fields": ("subject", "class_name", "date")}),
        (
            "Содержание",
            {
                "fields": (
                    "objectives",
                    "content",
                    "materials",
                    "homework",
                )
            },
        ),
        ("Примечания", {"fields": ("notes",), "classes": ("collapse",)}),
    )


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = [
        "student_name",
        "subject",
        "class_name",
        "grade",
        "grade_type",
        "date",
    ]
    list_filter = ["date", "subject", "class_name", "grade_type", "grade"]
    search_fields = ["student_name", "subject__name", "class_name__name"]
    ordering = ["-date", "student_name"]
    fieldsets = (
        ("Ученик и предмет", {"fields": ("student_name", "subject", "class_name")}),
        ("Оценка", {"fields": ("grade", "grade_type", "lesson")}),
        ("Комментарий", {"fields": ("comment",)}),
    )


@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ["title", "test_type", "subject", "class_name", "max_score", "created_at"]
    list_filter = ["test_type", "subject", "class_name", "created_at"]
    search_fields = ["title", "subject__name", "class_name__name"]
    ordering = ["-created_at"]
    fieldsets = (
        ("Основная информация", {"fields": ("title", "test_type", "curriculum")}),
        ("Предмет и класс", {"fields": ("subject", "class_name", "topic")}),
        (
            "Содержание",
            {
                "fields": (
                    "description",
                    "content",
                    "answer_key",
                )
            },
        ),
        (
            "Параметры",
            {"fields": ("max_score", "duration_minutes")},
        ),
    )


@admin.register(TestResult)
class TestResultAdmin(admin.ModelAdmin):
    list_display = ["student_name", "test", "score", "percentage", "date_completed"]
    list_filter = ["date_completed", "test", "percentage"]
    search_fields = ["student_name", "test__title"]
    ordering = ["-date_completed"]
    readonly_fields = ["percentage", "date_completed"]


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ["name", "created_by"]
    search_fields = ["name"]


@admin.register(StudentGroup)
class StudentGroupAdmin(admin.ModelAdmin):
    list_display = ["name", "year", "created_by"]
    search_fields = ["name"]
    readonly_fields = ["created_by"]


@admin.register(NeuralNetworkModel)
class NeuralNetworkModelAdmin(admin.ModelAdmin):
    list_display = ["name", "subject", "is_active", "accuracy", "training_samples", "last_trained"]
    list_filter = ["is_active", "subject", "created_at", "updated_at"]
    search_fields = ["name", "subject__name", "description"]
    ordering = ["-updated_at"]
    readonly_fields = ["created_at", "updated_at", "accuracy", "training_samples"]
    fieldsets = (
        ("Основная информация", {"fields": ("name", "description", "is_active")}),
        ("Предмет и программа", {"fields": ("subject", "curriculum")}),
        ("Педагог", {"fields": ("teacher",)}),
        ("Модель", {"fields": ("model_file",)}),
        ("Статистика", {"fields": ("accuracy", "training_samples", "last_trained")}),
        ("Дата", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )


@admin.register(GradePrediction)
class GradePredictionAdmin(admin.ModelAdmin):
    list_display = [
        "student_name",
        "subject",
        "predicted_grade",
        "confidence",
        "actual_grade",
        "is_accurate",
        "prediction_date"
    ]
    list_filter = [
        "prediction_date",
        "subject",
        "is_accurate",
        "confidence",
        "curriculum"
    ]
    search_fields = ["student_name", "subject__name"]
    ordering = ["-prediction_date"]
    readonly_fields = [
        "predicted_grade",
        "confidence",
        "average_grade",
        "attendance",
        "test_average",
        "homework_completion",
        "prediction_date",
        "is_accurate"
    ]
    fieldsets = (
        ("Студент и предмет", {"fields": ("student_name", "subject", "curriculum")}),
        ("Предсказание", {"fields": ("nn_model", "predicted_grade", "confidence")}),
        (
            "Показатели студента",
            {
                "fields": (
                    "average_grade",
                    "attendance",
                    "test_average",
                    "homework_completion",
                )
            },
        ),
        ("Проверка точности", {"fields": ("actual_grade", "is_accurate")}),
        ("Дата", {"fields": ("prediction_date",), "classes": ("collapse",)}),
    )


class QuizQuestionInline(admin.TabularInline):
    """Inline для вопросов викторины"""
    model = QuizQuestion
    extra = 1
    fields = ['order', 'question_text', 'question_type', 'points']
    ordering = ['order']


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    """Администрирование викторин"""
    list_display = ['title', 'teacher', 'subject', 'difficulty', 'is_active', 'created_at']
    list_filter = ['difficulty', 'is_active', 'subject', 'created_at']
    search_fields = ['title', 'description', 'teacher__username']
    ordering = ['-created_at']
    inlines = [QuizQuestionInline]
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('teacher', 'title', 'description', 'is_active')
        }),
        ('Привязка к курсу', {
            'fields': ('curriculum', 'topic', 'subject', 'class_name')
        }),
        ('Параметры', {
            'fields': ('difficulty', 'time_limit')
        }),
    )


@admin.register(QuizQuestion)
class QuizQuestionAdmin(admin.ModelAdmin):
    """Администрирование вопросов викторины"""
    list_display = ['quiz', 'question_text_short', 'question_type', 'points', 'order']
    list_filter = ['question_type', 'quiz']
    search_fields = ['question_text', 'quiz__title']
    ordering = ['quiz', 'order']
    
    def question_text_short(self, obj):
        """Сокращённый текст вопроса"""
        return obj.question_text[:50] + '...' if len(obj.question_text) > 50 else obj.question_text
    question_text_short.short_description = 'Вопрос'


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    """Администрирование попыток викторины"""
    list_display = ['quiz', 'student_name', 'score', 'max_score', 'percentage', 'completed_at']
    list_filter = ['is_completed', 'quiz', 'completed_at']
    search_fields = ['student_name', 'quiz__title']
    ordering = ['-completed_at']
    readonly_fields = ['score', 'max_score', 'percentage', 'completed_at']