from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Avg, Max
from django.db import models
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse, reverse_lazy
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta
from .models import Curriculum, Topic, Schedule, Lesson, Grade, Test, TestResult, Subject, StudentGroup, Quiz, QuizQuestion, QuizAttempt


@login_required
def dashboard(request):
    """Главная страница панели управления педагога"""
    teacher = request.user

    # Получение основных данных
    today = datetime.today().date()
    upcoming_lessons = Lesson.objects.filter(
        teacher=teacher, date__gte=today
    ).order_by("date")[:5]

    today_schedule = Schedule.objects.filter(
        teacher=teacher, day_of_week=today.weekday()
    ).order_by("start_time")

    curricula = Curriculum.objects.filter(lessons__teacher=teacher).distinct()[:3]

    recent_grades = Grade.objects.filter(teacher=teacher).order_by("-date")[:10]

    recent_tests = Test.objects.filter(teacher=teacher).order_by("-created_at")[:5]

    context = {
        "upcoming_lessons": upcoming_lessons,
        "today_schedule": today_schedule,
        "curricula": curricula,
        "recent_grades": recent_grades,
        "recent_tests": recent_tests,
    }

    return render(request, "teacher/dashboard.html", context)


class CurriculumListView(LoginRequiredMixin, ListView):
    """Список рабочих программ"""

    model = Curriculum
    template_name = "teacher/curriculum_list.html"
    context_object_name = "curricula"
    paginate_by = 10

    def get_queryset(self):
        return Curriculum.objects.annotate(lesson_count=Count("lessons")).order_by(
            "-created_at"
        )


class CurriculumDetailView(LoginRequiredMixin, DetailView):
    """Детальный просмотр рабочей программы"""

    model = Curriculum
    template_name = "teacher/curriculum_detail.html"
    context_object_name = "curriculum"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["topics"] = self.object.topics.order_by("order")
        context["lessons"] = self.object.lessons.order_by("-date")
        context["tests"] = self.object.tests.order_by("-created_at")
        return context


class CurriculumCreateView(LoginRequiredMixin, CreateView):
    """Создание рабочей программы"""

    model = Curriculum
    template_name = "teacher/curriculum_form.html"
    fields = ["title", "subject", "student_group", "year"]
    success_url = reverse_lazy("teacher:curriculum_list")


class CurriculumUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование рабочей программы"""

    model = Curriculum
    template_name = "teacher/curriculum_form.html"
    fields = ["title", "subject", "student_group", "year"]
    success_url = reverse_lazy("teacher:curriculum_list")


class CurriculumDeleteView(LoginRequiredMixin, DeleteView):
    """Удаление рабочей программы"""
    model = Curriculum
    template_name = "teacher/curriculum_confirm_delete.html"
    success_url = reverse_lazy("teacher:curriculum_list")


class ScheduleListView(LoginRequiredMixin, ListView):
    """Список расписания"""

    model = Schedule
    template_name = "teacher/schedule_list.html"
    context_object_name = "schedules"

    def get_queryset(self):
        return Schedule.objects.filter(teacher=self.request.user).order_by(
            "day_of_week", "start_time"
        )


class ScheduleCreateView(LoginRequiredMixin, CreateView):
    """Создание расписания"""

    model = Schedule
    template_name = "teacher/schedule_form.html"
    fields = ["subject", "class_name", "day_of_week", "start_time", "end_time", "room"]
    success_url = reverse_lazy("teacher:schedule_list")

    def form_valid(self, form):
        form.instance.teacher = self.request.user
        return super().form_valid(form)


class LessonListView(LoginRequiredMixin, ListView):
    """Список планов уроков"""

    model = Lesson
    template_name = "teacher/lesson_list.html"
    context_object_name = "lessons"
    paginate_by = 20

    def get_queryset(self):
        return Lesson.objects.filter(teacher=self.request.user).order_by("-date")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["curricula"] = Curriculum.objects.filter(
            lessons__teacher=self.request.user
        ).distinct()
        return context


class LessonCreateView(LoginRequiredMixin, CreateView):
    """Создание плана урока"""

    model = Lesson
    template_name = "teacher/lesson_form.html"
    fields = [
        "curriculum",
        "topic",
        "title",
        "date",
        "class_name",
        "subject",
        "objectives",
        "materials",
        "content",
        "homework",
        "notes",
    ]
    success_url = reverse_lazy("teacher:lesson_list")

    def form_valid(self, form):
        form.instance.teacher = self.request.user
        return super().form_valid(form)


class LessonDetailView(LoginRequiredMixin, DetailView):
    """Детальный просмотр плана урока"""

    model = Lesson
    template_name = "teacher/lesson_detail.html"
    context_object_name = "lesson"


class LessonUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование плана урока"""

    model = Lesson
    template_name = "teacher/lesson_form.html"
    fields = [
        "curriculum",
        "topic",
        "title",
        "date",
        "class_name",
        "subject",
        "objectives",
        "materials",
        "content",
        "homework",
        "notes",
    ]
    success_url = reverse_lazy("teacher:lesson_list")


class LessonDeleteView(LoginRequiredMixin, DeleteView):
    """Удаление урока"""
    model = Lesson
    template_name = "teacher/lesson_confirm_delete.html"
    success_url = reverse_lazy("teacher:lesson_list")
    
    def get_queryset(self):
        """Пользователь может удалять только свои уроки"""
        return super().get_queryset().filter(teacher=self.request.user)


class GradeListView(LoginRequiredMixin, ListView):
    """Список оценок (журнал)"""

    model = Grade
    template_name = "teacher/grade_list.html"
    context_object_name = "grades"
    paginate_by = 50

    def get_queryset(self):
        queryset = Grade.objects.filter(teacher=self.request.user).order_by(
            "-date", "student_name"
        )

        # Фильтрация по классу
        class_name = self.request.GET.get("class_name")
        if class_name:
            queryset = queryset.filter(class_name=class_name)

        # Фильтрация по предмету
        subject = self.request.GET.get("subject")
        if subject:
            queryset = queryset.filter(subject=subject)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["classes"] = (
            Grade.objects.filter(teacher=self.request.user)
            .values_list("class_name", flat=True)
            .distinct()
        )
        context["subjects"] = (
            Grade.objects.filter(teacher=self.request.user)
            .values_list("subject", flat=True)
            .distinct()
        )
        return context


class GradeCreateView(LoginRequiredMixin, CreateView):
    """Добавление оценки"""

    model = Grade
    template_name = "teacher/grade_form.html"
    fields = [
        "student_name",
        "class_name",
        "subject",
        "grade",
        "grade_type",
        "lesson",
        "comment",
        "curriculum",
    ]
    success_url = reverse_lazy("teacher:grade_list")

    def form_valid(self, form):
        form.instance.teacher = self.request.user
        return super().form_valid(form)


class TestListView(LoginRequiredMixin, ListView):
    """Список тестов и контрольных работ"""

    model = Test
    template_name = "teacher/test_list.html"
    context_object_name = "tests"
    paginate_by = 20

    def get_queryset(self):
        return Test.objects.filter(teacher=self.request.user).order_by("-created_at")


class TestCreateView(LoginRequiredMixin, CreateView):
    """Создание теста/контрольной работы"""

    model = Test
    template_name = "teacher/test_form.html"
    fields = [
        "curriculum",
        "topic",
        "title",
        "description",
        "test_type",
        "subject",
        "class_name",
        "content",
        "answer_key",
        "max_score",
        "duration_minutes",
    ]
    success_url = reverse_lazy("teacher:test_list")

    def form_valid(self, form):
        form.instance.teacher = self.request.user
        return super().form_valid(form)


class TestDetailView(LoginRequiredMixin, DetailView):
    """Детальный просмотр теста"""

    model = Test
    template_name = "teacher/test_detail.html"
    context_object_name = "test"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["results"] = self.object.results.order_by("-date_completed")
        return context


class TestUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование теста"""

    model = Test
    template_name = "teacher/test_form.html"
    fields = [
        "curriculum",
        "topic",
        "title",
        "description",
        "test_type",
        "subject",
        "class_name",
        "content",
        "answer_key",
        "max_score",
        "duration_minutes",
    ]
    success_url = reverse_lazy("teacher:test_list")


@login_required
@require_POST
def update_grade_ajax(request, grade_id):
    """AJAX endpoint для быстрого обновления оценки в реальном времени"""
    try:
        grade = Grade.objects.get(id=grade_id, teacher=request.user)
        
        # Обновляем только если передано в POST
        if 'grade' in request.POST:
            grade.grade = request.POST.get('grade')
        if 'comment' in request.POST:
            grade.comment = request.POST.get('comment')
        if 'grade_type' in request.POST:
            grade.grade_type = request.POST.get('grade_type')
        
        grade.save()
        
        return JsonResponse({
            'success': True,
            'grade': grade.grade,
            'comment': grade.comment,
            'grade_type': grade.get_grade_type_display()
        })
    except Grade.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Grade not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
@require_POST
def update_lesson_ajax(request, lesson_id):
    """AJAX endpoint для быстрого обновления урока в реальном времени"""
    try:
        lesson = Lesson.objects.get(id=lesson_id, teacher=request.user)
        
        # Обновляем только переданные поля
        updatable_fields = ['title', 'date', 'objectives', 'materials', 'content', 'homework', 'notes']
        for field in updatable_fields:
            if field in request.POST:
                setattr(lesson, field, request.POST.get(field))
        
        lesson.save()
        
        return JsonResponse({
            'success': True,
            'title': lesson.title,
            'date': lesson.date.strftime('%d.%m.%Y') if lesson.date else '',
            'objectives': lesson.objectives,
            'content': lesson.content
        })
    except Lesson.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Lesson not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@require_POST
def create_group_ajax(request):
    """AJAX endpoint для создания группы студентов в реальном времени"""
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'error': 'Требуется авторизация',
            'login_url': f"/accounts/login/?next={request.path}",
        }, status=401)

    try:
        name = request.POST.get('name', '').strip()
        if not name:
            return JsonResponse({'success': False, 'error': 'Название группы не может быть пусто'}, status=400)
        
        year = request.POST.get('year', None)
        
        group, created = StudentGroup.objects.get_or_create(
            name=name,
            defaults={'year': year, 'created_by': request.user}
        )
        
        return JsonResponse({
            'success': True,
            'id': group.id,
            'name': group.name,
            'year': group.year,
            'created': created
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@require_POST
def create_topic_ajax(request):
    """AJAX endpoint для создания темы в реальном времени"""
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'error': 'Требуется авторизация',
            'login_url': f"/accounts/login/?next={request.path}",
        }, status=401)

    try:
        title = request.POST.get('title', '').strip()
        curriculum_id = request.POST.get('curriculum_id', None)
        
        if not title:
            return JsonResponse({'success': False, 'error': 'Название темы не может быть пусто'}, status=400)
        
        if not curriculum_id:
            return JsonResponse({'success': False, 'error': 'Программа не указана'}, status=400)
        
        curriculum = Curriculum.objects.get(pk=curriculum_id)
        
        # Найти максимальный порядок
        max_order = Topic.objects.filter(curriculum=curriculum).aggregate(Max('order'))['order__max'] or 0
        
        topic = Topic.objects.create(
            curriculum=curriculum,
            title=title,
            description=request.POST.get('description', ''),
            order=max_order + 1,
            hours=int(request.POST.get('hours', 1))
        )
        
        return JsonResponse({
            'success': True,
            'id': topic.id,
            'title': topic.title,
            'order': topic.order,
            'hours': topic.hours,
            'created': True
        })
    except Curriculum.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Программа не найдена'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@require_POST
def create_subject_ajax(request):
    """AJAX endpoint для создания предмета в реальном времени"""
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'error': 'Требуется авторизация',
            'login_url': f"/accounts/login/?next={request.path}",
        }, status=401)

    try:
        name = request.POST.get('name', '').strip()
        
        if not name:
            return JsonResponse({'success': False, 'error': 'Название предмета не может быть пусто'}, status=400)
        
        # Проверить, существует ли уже предмет с таким именем
        if Subject.objects.filter(name__iexact=name).exists():
            return JsonResponse({'success': False, 'error': 'Предмет с таким названием уже существует'}, status=400)
        
        subject = Subject.objects.create(
            name=name,
            description=request.POST.get('description', ''),
            created_by=request.user
        )
        
        return JsonResponse({
            'success': True,
            'id': subject.id,
            'name': subject.name,
            'created': True
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


# ============= Просмотр и управление группами и предметами =============

class StudentGroupListView(LoginRequiredMixin, ListView):
    """Список групп студентов"""
    model = StudentGroup
    template_name = "teacher/student_group_list.html"
    context_object_name = "groups"
    paginate_by = 10


class StudentGroupCreateView(LoginRequiredMixin, CreateView):
    """Создание группы студентов"""
    model = StudentGroup
    template_name = "teacher/student_group_form.html"
    fields = ["name", "year", "students"]
    success_url = reverse_lazy("teacher:student_group_list")
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class StudentGroupUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование группы студентов"""
    model = StudentGroup
    template_name = "teacher/student_group_form.html"
    fields = ["name", "year", "students"]
    success_url = reverse_lazy("teacher:student_group_list")


class StudentGroupDeleteView(LoginRequiredMixin, DeleteView):
    """Удаление группы студентов"""
    model = StudentGroup
    success_url = reverse_lazy("teacher:student_group_list")
    template_name = "teacher/student_group_confirm_delete.html"


class SubjectListView(LoginRequiredMixin, ListView):
    """Список предметов"""
    model = Subject
    template_name = "teacher/subject_list.html"
    context_object_name = "subjects"
    paginate_by = 10


class SubjectCreateView(LoginRequiredMixin, CreateView):
    """Создание предмета"""
    model = Subject
    template_name = "teacher/subject_form.html"
    fields = ["name", "description"]
    success_url = reverse_lazy("teacher:subject_list")
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class SubjectUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование предмета"""
    model = Subject
    template_name = "teacher/subject_form.html"
    fields = ["name", "description"]
    success_url = reverse_lazy("teacher:subject_list")


class SubjectDeleteView(LoginRequiredMixin, DeleteView):
    """Удаление предмета"""
    model = Subject
    success_url = reverse_lazy("teacher:subject_list")
    template_name = "teacher/subject_confirm_delete.html"


# ============= Темы для рабочих программ =============

class TopicListView(LoginRequiredMixin, ListView):
    """Список тем для конкретной программы"""
    model = Topic
    template_name = "teacher/topic_list.html"
    context_object_name = "topics"
    paginate_by = 15

    def get_queryset(self):
        self.curriculum = get_object_or_404(Curriculum, pk=self.kwargs['curriculum_id'])
        return Topic.objects.filter(curriculum=self.curriculum).order_by('order')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['curriculum'] = self.curriculum
        return context


class TopicCreateView(LoginRequiredMixin, CreateView):
    """Создание новой темы"""
    model = Topic
    template_name = "teacher/topic_form.html"
    fields = ["title", "description", "order", "hours"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['curriculum'] = get_object_or_404(Curriculum, pk=self.kwargs['curriculum_id'])
        return context

    def form_valid(self, form):
        form.instance.curriculum_id = self.kwargs['curriculum_id']
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("teacher:topic_list", kwargs={'curriculum_id': self.kwargs['curriculum_id']})


class TopicUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование темы"""
    model = Topic
    template_name = "teacher/topic_form.html"
    fields = ["title", "description", "order", "hours"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['curriculum'] = self.object.curriculum
        return context

    def get_success_url(self):
        return reverse_lazy("teacher:topic_list", kwargs={'curriculum_id': self.object.curriculum.id})


class TopicDeleteView(LoginRequiredMixin, DeleteView):
    """Удаление темы"""
    model = Topic
    template_name = "teacher/topic_confirm_delete.html"

    def get_success_url(self):
        return reverse_lazy("teacher:topic_list", kwargs={'curriculum_id': self.object.curriculum.id})


# ==================== Quiz Views ====================

class QuizListView(LoginRequiredMixin, ListView):
    """Список викторин педагога"""
    model = Quiz
    template_name = "teacher/quiz_list.html"
    context_object_name = "quizzes"
    paginate_by = 20

    def get_queryset(self):
        return Quiz.objects.filter(teacher=self.request.user).order_by('-created_at')


class QuizDetailView(LoginRequiredMixin, DetailView):
    """Детальная информация о викторине"""
    model = Quiz
    template_name = "teacher/quiz_detail.html"
    context_object_name = "quiz"

    def get_queryset(self):
        return Quiz.objects.filter(teacher=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['questions'] = self.object.questions.all().order_by('order')
        context['attempts'] = self.object.attempts.all().order_by('-completed_at')[:10]
        return context


class QuizCreateView(LoginRequiredMixin, CreateView):
    """Создание викторины"""
    model = Quiz
    template_name = "teacher/quiz_form.html"
    fields = ['title', 'description', 'curriculum', 'topic', 'subject', 'class_name', 'difficulty', 'time_limit']
    success_url = reverse_lazy("teacher:quiz_list")

    def form_valid(self, form):
        form.instance.teacher = self.request.user
        return super().form_valid(form)


class QuizUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование викторины"""
    model = Quiz
    template_name = "teacher/quiz_form.html"
    fields = ['title', 'description', 'curriculum', 'topic', 'subject', 'class_name', 'difficulty', 'time_limit', 'is_active']
    success_url = reverse_lazy("teacher:quiz_list")

    def get_queryset(self):
        return Quiz.objects.filter(teacher=self.request.user)


class QuizDeleteView(LoginRequiredMixin, DeleteView):
    """Удаление викторины"""
    model = Quiz
    template_name = "teacher/quiz_confirm_delete.html"
    success_url = reverse_lazy("teacher:quiz_list")

    def get_queryset(self):
        return Quiz.objects.filter(teacher=self.request.user)


@login_required
def take_quiz(request, pk=None, quiz_id=None):
    """Прохождение викторины (пошаговая)"""
    target_id = pk if pk is not None else quiz_id
    if target_id is None:
        messages.error(request, "Викторина не указана.")
        return redirect('teacher:quiz_list')

    quiz = Quiz.objects.filter(pk=target_id).first()
    if quiz is None:
        messages.error(request, f"Викторина с ID {target_id} не найдена. Выберите викторину из списка.")
        return redirect('teacher:quiz_list')

    # В режиме преподавателя проходить викторину может только владелец
    if quiz.teacher_id != request.user.id:
        messages.error(request, "У вас нет доступа к этой викторине.")
        return redirect('teacher:quiz_list')

    questions = list(quiz.questions.all().order_by('order'))
    
    # DEBUG: Check questions loading
    print(f"\n=== QUIZ LOADING DEBUG ===")
    print(f"Quiz ID: {quiz.id}, Title: {quiz.title}")
    print(f"Questions count: {len(questions)}")
    if questions:
        q = questions[0]
        print(f"First question ID: {q.id}")
        print(f"First question text: {q.question_text}")
        print(f"First question type: {q.question_type}")
        print(f"First question options: {q.options}")
        print(f"First question options type: {type(q.options)}")
    print(f"========================\n")
    
    if not questions:
        return redirect('teacher:quiz_detail', pk=quiz.id)

    # Получаем или создаем сессию для попытки
    session_key = f'quiz_attempt_{quiz.id}'
    
    if request.method == 'POST':
        # Получаем текущие данные из сессии
        attempt_data = request.session.get(session_key, {
            'student_name': request.POST.get('student_name', request.user.username),
            'answers': {},
            'current_question': 0
        })
        
        # Сохраняем ответ на текущий вопрос
        current_q_index = attempt_data.get('current_question', 0)
        if current_q_index < len(questions):
            question = questions[current_q_index]
            answer_key = f'question_{question.id}'
            if answer_key in request.POST:
                answer_value = request.POST[answer_key]
                # Преобразуем ответ в правильный формат
                if question.question_type == 'true_false':
                    answer_value = answer_value == 'true'
                elif question.question_type in ['single_choice', 'multiple_choice']:
                    try:
                        answer_value = int(answer_value)
                    except (ValueError, TypeError):
                        pass
                attempt_data['answers'][str(question.id)] = answer_value
        
        # Переходим к следующему вопросу
        attempt_data['current_question'] = current_q_index + 1
        
        # Если это был последний вопрос - создаем попытку и показываем результат
        if attempt_data['current_question'] >= len(questions):
            attempt = QuizAttempt.objects.create(
                quiz=quiz,
                student_name=attempt_data['student_name'],
                class_name=quiz.class_name,
                answers=attempt_data['answers'],
                is_completed=True
            )
            attempt.calculate_score()
            
            # Очищаем сессию
            if session_key in request.session:
                del request.session[session_key]
            
            return redirect('teacher:quiz_result', attempt_id=attempt.id)
        
        # Сохраняем прогресс в сессии
        request.session[session_key] = attempt_data
        request.session.modified = True
        
        # Перенаправляем на ту же страницу для отображения следующего вопроса
        return redirect('teacher:quiz_take', pk=quiz.id)
    
    # GET запрос - показываем текущий вопрос
    attempt_data = request.session.get(session_key, {
        'student_name': request.user.username,
        'answers': {},
        'current_question': 0
    })
    
    current_q_index = attempt_data.get('current_question', 0)
    
    # Если это первый вопрос и имя еще не задано
    if current_q_index == 0 and 'student_name' not in attempt_data:
        request.session[session_key] = attempt_data
    
    if current_q_index >= len(questions):
        # Если каким-то образом зашли сюда после завершения
        if session_key in request.session:
            del request.session[session_key]
        return redirect('teacher:quiz_detail', pk=quiz.id)
    
    current_question = questions[current_q_index]
    
    # DEBUG: Check questions loading
    print(f"\n=== QUIZ LOADING DEBUG ===")
    print(f"Quiz ID: {quiz.id}, Title: {quiz.title}")
    print(f"Questions count: {len(questions)}")
    print(f"Current question index: {current_q_index}")
    print(f"Current question ID: {current_question.id}")
    print(f"Current question text: {current_question.question_text}")
    print(f"Current question type: {current_question.question_type}")
    print(f"Current question options: {current_question.options}")
    print(f"Current question options type: {type(current_question.options)}")
    if current_question.options:
        print(f"Current question options length: {len(current_question.options)}")
    print(f"========================\n")
    
    # Debug logging - send to template
    debug_info = {
        'id': current_question.id,
        'text': current_question.question_text,
        'type': current_question.question_type,
        'options': current_question.options,
        'options_type': str(type(current_question.options)),
        'options_len': len(current_question.options) if current_question.options else 0,
    }
    
    context = {
        'quiz': quiz,
        'question': current_question,
        'questions': questions,
        'question_number': current_q_index + 1,
        'total_questions': len(questions),
        'student_name': attempt_data.get('student_name', request.user.username),
        'is_first_question': current_q_index == 0,
        'debug_info': debug_info,
    }
    return render(request, 'teacher/quiz_take.html', context)


@login_required
def quiz_result(request, attempt_id):
    """Результаты прохождения викторины"""
    attempt = get_object_or_404(QuizAttempt, pk=attempt_id)

    context = {
        'attempt': attempt,
        'quiz': attempt.quiz,
    }
    return render(request, 'teacher/quiz_result.html', context)


def take_quiz_student(request, pk):
    """Публичное прохождение викторины для студентов (пошаговая)"""
    quiz = get_object_or_404(Quiz, pk=pk, is_active=True)
    questions = list(quiz.questions.all().order_by('order'))
    
    if not questions:
        return redirect('teacher:quiz_list')

    # Получаем или создаем сессию для попытки
    session_key = f'quiz_attempt_public_{quiz.id}'
    
    if request.method == 'POST':
        # Получаем текущие данные из сессии
        attempt_data = request.session.get(session_key, {
            'student_name': request.POST.get('student_name', 'Студент'),
            'answers': {},
            'current_question': 0
        })
        
        # Сохраняем ответ на текущий вопрос
        current_q_index = attempt_data.get('current_question', 0)
        if current_q_index < len(questions):
            question = questions[current_q_index]
            answer_key = f'question_{question.id}'
            if answer_key in request.POST:
                answer_value = request.POST[answer_key]
                # Преобразуем ответ в правильный формат
                if question.question_type == 'true_false':
                    answer_value = answer_value == 'true'
                elif question.question_type in ['single_choice', 'multiple_choice']:
                    try:
                        answer_value = int(answer_value)
                    except (ValueError, TypeError):
                        pass
                attempt_data['answers'][str(question.id)] = answer_value
        
        # Переходим к следующему вопросу
        attempt_data['current_question'] = current_q_index + 1
        
        # Если это был последний вопрос - создаем попытку и показываем результат
        if attempt_data['current_question'] >= len(questions):
            attempt = QuizAttempt.objects.create(
                quiz=quiz,
                student_name=attempt_data['student_name'],
                class_name=quiz.class_name,
                answers=attempt_data['answers'],
                is_completed=True
            )
            attempt.calculate_score()
            
            # Очищаем сессию
            if session_key in request.session:
                del request.session[session_key]
            
            return redirect('teacher:quiz_result_student', attempt_id=attempt.id)
        
        # Сохраняем прогресс в сессии
        request.session[session_key] = attempt_data
        request.session.modified = True
        
        # Перенаправляем на ту же страницу для отображения следующего вопроса
        return redirect('teacher:quiz_take_student', pk=quiz.id)
    
    # GET запрос - показываем текущий вопрос
    attempt_data = request.session.get(session_key, {
        'student_name': 'Студент',
        'answers': {},
        'current_question': 0
    })
    
    current_q_index = attempt_data.get('current_question', 0)
    
    # Если это первый вопрос и имя еще не задано
    if current_q_index == 0 and 'student_name' not in attempt_data:
        request.session[session_key] = attempt_data
    
    if current_q_index >= len(questions):
        # Если каким-то образом зашли сюда после завершения
        if session_key in request.session:
            del request.session[session_key]
        return redirect('teacher:quiz_list')
    
    current_question = questions[current_q_index]
    
    context = {
        'quiz': quiz,
        'question': current_question,
        'questions': questions,
        'question_number': current_q_index + 1,
        'total_questions': len(questions),
        'student_name': attempt_data.get('student_name', 'Студент'),
        'is_first_question': current_q_index == 0,
        'is_public': True,
    }
    return render(request, 'teacher/quiz_take.html', context)


def quiz_result_student(request, attempt_id):
    """Публичный просмотр результата викторины для студентов."""
    attempt = get_object_or_404(QuizAttempt, pk=attempt_id)
    context = {
        'attempt': attempt,
        'quiz': attempt.quiz,
        'percentage': attempt.percentage,
        'is_passed': attempt.percentage >= 60,
        'is_public': True,
    }
    return render(request, 'teacher/quiz_result.html', context)


@login_required
@require_POST
def create_quiz_from_ai(request):
    """Создание викторины из данных, сгенерированных ИИ"""
    try:
        import json
        quiz_data_str = request.POST.get('quiz_data', '{}')
        quiz_data = json.loads(quiz_data_str)

        # Создаём викторину
        quiz = Quiz.objects.create(
            teacher=request.user,
            title=quiz_data.get('title', 'Новая викторина'),
            description=quiz_data.get('description', ''),
            difficulty='medium',
            time_limit=15,
            is_active=True
        )

        # Создаём вопросы
        for index, q_data in enumerate(quiz_data.get('questions', [])):
            QuizQuestion.objects.create(
                quiz=quiz,
                question_text=q_data.get('question_text', ''),
                question_type=q_data.get('question_type', 'short_answer'),
                options=q_data.get('options'),
                correct_answer=q_data.get('correct_answer'),
                explanation=q_data.get('explanation', ''),
                points=q_data.get('points', 1),
                order=index
            )

        return JsonResponse({
            'success': True,
            'message': f'Викторина "{quiz.title}" создана успешно!',
            'quiz_id': quiz.id
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


# === Викторины ===

class QuizListView(LoginRequiredMixin, ListView):
    """Список викторин"""
    model = Quiz
    template_name = "teacher/quiz_list.html"
    context_object_name = "quizzes"
    paginate_by = 20

    def get_queryset(self):
        return Quiz.objects.filter(teacher=self.request.user).order_by("-created_at")


class QuizDetailView(LoginRequiredMixin, DetailView):
    """Детальная информация о викторине"""
    model = Quiz
    template_name = "teacher/quiz_detail.html"
    context_object_name = "quiz"

    def get_queryset(self):
        return Quiz.objects.filter(teacher=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['questions'] = self.object.questions.all().order_by('order')
        context['attempts'] = self.object.attempts.all().order_by('-completed_at')[:10]

        student_path = reverse('teacher:quiz_take_student', kwargs={'pk': self.object.pk})
        public_base_url = (getattr(settings, 'PUBLIC_BASE_URL', '') or '').strip().rstrip('/')
        if public_base_url:
            student_link = f"{public_base_url}{student_path}"
        else:
            student_link = self.request.build_absolute_uri(student_path)

        host = (self.request.get_host() or '').split(':')[0].lower()
        context['student_quiz_link'] = student_link
        context['student_link_may_be_local'] = host in {'localhost', '127.0.0.1'} and not public_base_url
        return context


class QuizCreateView(LoginRequiredMixin, CreateView):
    """Создание викторины"""
    model = Quiz
    template_name = "teacher/quiz_form.html"
    fields = ["title", "description", "curriculum", "topic", "subject", "class_name", "difficulty", "time_limit"]
    success_url = reverse_lazy("teacher:quiz_list")

    def form_valid(self, form):
        form.instance.teacher = self.request.user
        return super().form_valid(form)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Фильтруем по пользователю
        curriculum_qs = Curriculum.objects.filter(
            Q(lessons__teacher=self.request.user)
            | Q(student_group__created_by=self.request.user)
            | Q(subject__created_by=self.request.user)
        ).distinct()

        form.fields['curriculum'].queryset = curriculum_qs
        form.fields['topic'].queryset = Topic.objects.filter(curriculum__in=curriculum_qs).distinct()
        form.fields['subject'].queryset = Subject.objects.filter(created_by=self.request.user)
        form.fields['class_name'].queryset = StudentGroup.objects.filter(created_by=self.request.user)
        return form


class QuizUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование викторины"""
    model = Quiz
    template_name = "teacher/quiz_form.html"
    fields = ["title", "description", "curriculum", "topic", "subject", "class_name", "difficulty", "time_limit", "is_active"]
    success_url = reverse_lazy("teacher:quiz_list")

    def get_queryset(self):
        return Quiz.objects.filter(teacher=self.request.user)


class QuizDeleteView(LoginRequiredMixin, DeleteView):
    """Удаление викторины"""
    model = Quiz
    template_name = "teacher/quiz_confirm_delete.html"
    success_url = reverse_lazy("teacher:quiz_list")

    def get_queryset(self):
        return Quiz.objects.filter(teacher=self.request.user)


@login_required
@require_POST
def create_quiz_from_ai(request):
    """Создание викторины на основе данных от ИИ генератора"""
    try:
        data = request.POST.get('quiz_data')
        if not data:
            return JsonResponse({'success': False, 'error': 'Нет данных викторины'})

        import json
        quiz_data = json.loads(data)

        # Подбор обязательной рабочей программы (curriculum)
        curriculum_id = request.POST.get('curriculum_id') or quiz_data.get('curriculum_id')
        curricula_qs = Curriculum.objects.filter(
            Q(lessons__teacher=request.user)
            | Q(student_group__created_by=request.user)
            | Q(subject__created_by=request.user)
        ).distinct()

        curriculum = None
        if curriculum_id:
            curriculum = curricula_qs.filter(pk=curriculum_id).first()

        if curriculum is None:
            # Пробуем подобрать по предмету и уровню (если переданы)
            subject_name = (quiz_data.get('subject') or '').strip()
            class_level = (quiz_data.get('class_level') or '').strip()

            candidate_qs = curricula_qs
            if subject_name:
                candidate_qs = candidate_qs.filter(subject__name__icontains=subject_name)

            if class_level:
                import re
                level_match = re.search(r'\d{1,2}', class_level)
                if level_match:
                    candidate_qs = candidate_qs.filter(class_level=level_match.group(0))

            curriculum = candidate_qs.first() or curricula_qs.first()

        if curriculum is None:
            return JsonResponse({
                'success': False,
                'error': 'Невозможно сохранить викторину: сначала создайте рабочую программу (учебный план).'
            }, status=400)

        # Создаем викторину
        quiz = Quiz.objects.create(
            teacher=request.user,
            curriculum=curriculum,
            title=quiz_data.get('title', 'Сгенерированная викторина'),
            description=quiz_data.get('description', ''),
            subject=curriculum.subject,
            class_name=curriculum.student_group,
            difficulty='medium',
            is_active=True
        )

        # Создаем вопросы
        for question_data in quiz_data.get('questions', []):
            QuizQuestion.objects.create(
                quiz=quiz,
                question_text=question_data['question_text'],
                question_type=question_data['question_type'],
                options=question_data.get('options'),
                correct_answer=question_data['correct_answer'],
                explanation=question_data.get('explanation', ''),
                points=question_data.get('points', 1)
            )

        return JsonResponse({
            'success': True,
            'quiz_id': quiz.id,
            'message': f'Викторина "{quiz.title}" создана с {quiz.questions.count()} вопросами'
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})





@login_required
def quiz_participants(request, pk):
    """Список участников викторины и их результаты."""
    quiz = get_object_or_404(Quiz, pk=pk, teacher=request.user)
    participants, attempts = _build_quiz_participants_data(quiz)
    winners = _get_quiz_winners(quiz)

    context = {
        'quiz': quiz,
        'attempts': attempts,
        'participants': participants,
        'participants_count': len(participants),
        'attempts_count': attempts.count(),
        'winners': winners,  # Топ-3 победители
    }
    return render(request, 'teacher/quiz_participants.html', context)


def _build_quiz_participants_data(quiz):
    """Собирает агрегированные данные по участникам и все попытки."""
    attempts = quiz.attempts.all().order_by('-completed_at')

    participants_map = {}
    for attempt in attempts:
        name = attempt.student_name or 'Неизвестный'
        if name not in participants_map:
            participants_map[name] = {
                'student_name': name,
                'attempts_count': 0,
                'best_score': attempt.score,
                'best_percentage': float(attempt.percentage),
                'last_attempt': attempt.completed_at,
                'best_time': attempt.time_spent,  # Время для первой попытки
            }

        item = participants_map[name]
        item['attempts_count'] += 1
        if attempt.percentage > item['best_percentage']:
            item['best_percentage'] = float(attempt.percentage)
            item['best_score'] = attempt.score
            item['best_time'] = attempt.time_spent  # Обновляем время лучшего результата
        elif attempt.percentage == item['best_percentage'] and attempt.time_spent < item['best_time']:
            # При равном проценте берем результат с меньшим временем
            item['best_time'] = attempt.time_spent
        if attempt.completed_at > item['last_attempt']:
            item['last_attempt'] = attempt.completed_at

    participants = sorted(
        participants_map.values(),
        key=lambda x: x['last_attempt'],
        reverse=True,
    )
    return participants, attempts


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
        key=lambda x: (-x.percentage, x.time_spent)  # Минус для убывающей сортировки процента
    )[:3]
    
    return winners


@login_required
def quiz_participants_live_data(request, pk):
    """Live-данные по попыткам викторины для обновления страницы в реальном времени."""
    quiz = get_object_or_404(Quiz, pk=pk, teacher=request.user)
    participants, attempts = _build_quiz_participants_data(quiz)

    participants_payload = [
        {
            'student_name': p['student_name'],
            'attempts_count': p['attempts_count'],
            'best_score': p['best_score'],
            'best_percentage': round(float(p['best_percentage']), 1),
            'last_attempt': p['last_attempt'].strftime('%d.%m.%Y %H:%M') if p['last_attempt'] else '',
        }
        for p in participants
    ]

    attempts_payload = [
        {
            'id': attempt.id,
            'student_name': attempt.student_name,
            'score': attempt.score,
            'max_score': attempt.max_score,
            'percentage': round(float(attempt.percentage), 1),
            'completed_at': attempt.completed_at.strftime('%d.%m.%Y %H:%M') if attempt.completed_at else '',
        }
        for attempt in attempts
    ]

    return JsonResponse({
        'success': True,
        'participants_count': len(participants_payload),
        'attempts_count': len(attempts_payload),
        'participants': participants_payload,
        'attempts': attempts_payload,
    })


@login_required
def quiz_attempt_detail(request, attempt_id):
    """Детальный разбор ответов студента по попытке викторины."""
    attempt = get_object_or_404(QuizAttempt, pk=attempt_id, quiz__teacher=request.user)
    questions = attempt.quiz.questions.all().order_by('order')

    def format_answer(question, value):
        if value is None:
            return '—'

        if question.question_type in ['single_choice', 'multiple_choice']:
            options = question.options or []

            def option_to_text(item):
                if isinstance(item, int) and 0 <= item < len(options):
                    return options[item]
                return str(item)

            if isinstance(value, list):
                return ', '.join(option_to_text(v) for v in value)
            return option_to_text(value)

        if question.question_type == 'true_false':
            return 'Верно' if str(value).lower() in ['true', '1', 'yes', 'да', 'верно'] else 'Неверно'

        return str(value)

    question_results = []
    for question in questions:
        answer_key = str(question.id)
        has_answer = answer_key in (attempt.answers or {})
        user_answer_raw = (attempt.answers or {}).get(answer_key)
        is_correct = question.is_correct_answer(user_answer_raw) if has_answer else False

        question_results.append({
            'question': question,
            'has_answer': has_answer,
            'is_correct': is_correct,
            'user_answer': format_answer(question, user_answer_raw),
            'correct_answer': format_answer(question, question.correct_answer),
        })

    context = {
        'attempt': attempt,
        'quiz': attempt.quiz,
        'question_results': question_results,
    }
    return render(request, 'teacher/quiz_attempt_detail.html', context)


@login_required
@require_POST
def delete_quiz_attempt(request, attempt_id):
    """Удаление результата викторины"""
    attempt = get_object_or_404(QuizAttempt, pk=attempt_id)
    quiz = attempt.quiz
    
    # Проверяем, что это учитель этой викторины
    if quiz.teacher != request.user:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    attempt.delete()
    
    return JsonResponse({'success': True, 'message': 'Результат удален'})
