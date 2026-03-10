from django.urls import path
from . import views

try:
    from . import neural_network_views
    HAS_NEURAL_NETWORK = True
except (ImportError, Exception):
    HAS_NEURAL_NETWORK = False
    neural_network_views = None

app_name = "teacher"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("curriculum/", views.CurriculumListView.as_view(), name="curriculum_list"),
    path("curriculum/create/", views.CurriculumCreateView.as_view(), name="curriculum_create"),
    path("curriculum/<int:pk>/", views.CurriculumDetailView.as_view(), name="curriculum_detail"),
    path("curriculum/<int:pk>/edit/", views.CurriculumUpdateView.as_view(), name="curriculum_update"),
    path("curriculum/<int:pk>/delete/", views.CurriculumDeleteView.as_view(), name="curriculum_delete"),
    path("schedule/", views.ScheduleListView.as_view(), name="schedule_list"),
    path("schedule/create/", views.ScheduleCreateView.as_view(), name="schedule_create"),
    path("lessons/", views.LessonListView.as_view(), name="lesson_list"),
    path("lessons/create/", views.LessonCreateView.as_view(), name="lesson_create"),
    path("lessons/<int:pk>/", views.LessonDetailView.as_view(), name="lesson_detail"),
    path("lessons/<int:pk>/edit/", views.LessonUpdateView.as_view(), name="lesson_update"),
    path("lessons/<int:pk>/update-ajax/", views.update_lesson_ajax, name="lesson_update_ajax"),
    path("lessons/<int:pk>/delete/", views.LessonDeleteView.as_view(), name="lesson_delete"),
    path("grades/", views.GradeListView.as_view(), name="grade_list"),
    path("grades/add/", views.GradeCreateView.as_view(), name="grade_create"),
    path("grades/<int:pk>/update-ajax/", views.update_grade_ajax, name="grade_update_ajax"),
    path("tests/", views.TestListView.as_view(), name="test_list"),
    path("tests/create/", views.TestCreateView.as_view(), name="test_create"),
    path("tests/<int:pk>/", views.TestDetailView.as_view(), name="test_detail"),
    path("tests/<int:pk>/edit/", views.TestUpdateView.as_view(), name="test_update"),
    path("api/subject/create/", views.create_subject_ajax, name="subject_create_ajax"),
    path("api/group/create/", views.create_group_ajax, name="group_create_ajax"),
    path("api/topic/create/", views.create_topic_ajax, name="topic_create_ajax"),
    path("groups/", views.StudentGroupListView.as_view(), name="student_group_list"),
    path("groups/create/", views.StudentGroupCreateView.as_view(), name="student_group_create"),
    path("groups/<int:pk>/edit/", views.StudentGroupUpdateView.as_view(), name="student_group_update"),
    path("groups/<int:pk>/delete/", views.StudentGroupDeleteView.as_view(), name="student_group_delete"),
    path("subjects/", views.SubjectListView.as_view(), name="subject_list"),
    path("subjects/create/", views.SubjectCreateView.as_view(), name="subject_create"),
    path("subjects/<int:pk>/edit/", views.SubjectUpdateView.as_view(), name="subject_update"),
    path("subjects/<int:pk>/delete/", views.SubjectDeleteView.as_view(), name="subject_delete"),
    path("curriculum/<int:curriculum_id>/topics/", views.TopicListView.as_view(), name="topic_list"),
    path("curriculum/<int:curriculum_id>/topics/create/", views.TopicCreateView.as_view(), name="topic_create"),
    path("topics/<int:pk>/edit/", views.TopicUpdateView.as_view(), name="topic_update"),
    path("topics/<int:pk>/delete/", views.TopicDeleteView.as_view(), name="topic_delete"),
    path("quizzes/", views.QuizListView.as_view(), name="quiz_list"),
    path("quizzes/create/", views.QuizCreateView.as_view(), name="quiz_create"),
    path("quizzes/<int:pk>/", views.QuizDetailView.as_view(), name="quiz_detail"),
    path("quizzes/<int:pk>/edit/", views.QuizUpdateView.as_view(), name="quiz_update"),
    path("quizzes/<int:pk>/delete/", views.QuizDeleteView.as_view(), name="quiz_delete"),
    path("quizzes/<int:pk>/take/", views.take_quiz, name="quiz_take"),
    path("quizzes/<int:pk>/participants/", views.quiz_participants, name="quiz_participants"),
    path("quizzes/<int:pk>/student/", views.take_quiz_student, name="quiz_take_student"),
    path("quiz-attempts/<int:attempt_id>/result/", views.quiz_result, name="quiz_result"),
    path("quiz-attempts/<int:attempt_id>/detail/", views.quiz_attempt_detail, name="quiz_attempt_detail"),
    path("quiz-attempts/<int:attempt_id>/result/student/", views.quiz_result_student, name="quiz_result_student"),
    path("quiz-attempts/<int:attempt_id>/delete/", views.delete_quiz_attempt, name="quiz_attempt_delete"),
    path("api/quiz/create-from-ai/", views.create_quiz_from_ai, name="quiz_create_from_ai"),
]

if HAS_NEURAL_NETWORK:
    urlpatterns += [
        path("neural_network/dashboard/", neural_network_views.neural_network_dashboard, name="nn_dashboard"),
        path("neural_network/models/", neural_network_views.NeuralNetworkModelListView.as_view(), name="nn_models_list"),
        path("neural_network/models/<int:pk>/", neural_network_views.NeuralNetworkModelDetailView.as_view(), name="nn_model_detail"),
        path("neural_network/models/<int:pk>/statistics/", neural_network_views.model_statistics, name="nn_model_statistics"),
        path("neural_network/train/<int:curriculum_id>/", neural_network_views.train_neural_network, name="nn_train_model"),
        path("neural_network/predict/<str:student_name>/<int:curriculum_id>/", neural_network_views.predict_student_grade, name="nn_predict_grade"),
        path("neural_network/predictions/", neural_network_views.GradePredictionListView.as_view(), name="nn_predictions"),
        path("confirm-grade/", neural_network_views.confirm_student_grade, name="confirm_grade"),
        path("neural_network/student/<str:student_name>/<int:curriculum_id>/", neural_network_views.student_analysis, name="student_analysis"),
        path("homework-generator/", neural_network_views.generate_homework_helper, name="homework_generator"),
        path("quiz-generator/", neural_network_views.generate_quiz_helper, name="quiz_generator"),
    ]
