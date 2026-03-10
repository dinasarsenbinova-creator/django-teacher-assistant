from django.shortcuts import render
from django.views.generic import ListView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from teacher.models import Subject


def home(request):
    return render(request, "core/home.html", {"title": "Home"})


class SubjectListView(ListView):
    """Список всех предметов (доступно всем)"""
    model = Subject
    template_name = "core/subject_list.html"
    context_object_name = "subjects"
    paginate_by = 10


class SubjectCreateView(LoginRequiredMixin, CreateView):
    """Создание предмета (только для авторизованных пользователей)"""
    model = Subject
    template_name = "core/subject_form.html"
    fields = ["name", "description"]
    success_url = reverse_lazy("core:subject_list")
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)
