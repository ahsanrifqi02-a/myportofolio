from django.conf import settings
from django.contrib import messages
from django.core import serializers
from django.core.exceptions import PermissionDenied
from django.db import models
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from main.forms import ProjectForm, EducationForm, ExperienceForm
from main.models import Experience, Skill, Project, Education

import datetime

def check_secret_code(request, post_key="password"):
    secret_code = getattr(settings, "SECRET_CODE", "")
    if not secret_code:
        return False
    header_code = (
        request.headers.get("X-Secret-Code")
        or request.headers.get("X-Secret-Key")
        or request.headers.get("X-Kode-Rahasia")
    )
    if header_code and header_code == secret_code:
        return True
    if post_key and request.POST.get(post_key) == secret_code:
        return True
    return False

# Fungsi agar tidak perlu mengulang syntax yang panjang
def is_editor_or_superuser(user):
    return user.is_authenticated and (user.is_superuser or user.groups.filter(name="Editor").exists())

def show_main(request):
    last_login = request.COOKIES.get(
        'last_login', 
        'No login session yet / Cookie not found'
    )

    context = {
        "name": "Ahsan",
        "npm": "2506624266",
        "study_program": "S1 Sistem Informasi",
        "bio": (
            "An Information Systems undergraduate at Universitas Indonesia bridging software engineering, data architecture, and business strategy. I specialize in transforming complex data infrastructure into scalable digital solutions and actionable intelligence that streamline operations and accelerate decision-making."
        ),
        "fullname": "Ahsan Rifqi Prasetyo",
        "skill_list": Skill.objects.all(),
        "last_login": last_login,
    }
    return render(request, "index.html", context)


def get_education_json(request):
    query = (
        request.GET.get("institution", "")
        or request.GET.get("search", "")
        or request.GET.get("q", "")
    ).strip()
    education_list = Education.objects.all()
    if query:
        education_list = education_list.filter(
            models.Q(institution__icontains=query) |
            models.Q(degree__icontains=query) |
            models.Q(field_of_study__icontains=query)
        )
    data = []
    for edu in education_list:
        data.append({
            "pk": str(edu.id),
            "fields": {
                "institution": edu.institution,
                "degree": edu.degree,
                "field_of_study": edu.field_of_study,
                "start_year": edu.start_year,
                "end_year": edu.end_year,
                "is_ongoing": edu.is_ongoing,
                "description": edu.description,
                "logo_url": edu.logo_url,
            }
        })
    return JsonResponse(data, safe=False)


def get_experience_json(request):
    query = (
        request.GET.get("title", "")
        or request.GET.get("search", "")
        or request.GET.get("q", "")
    ).strip()
    experience_list = Experience.objects.all()
    if query:
        experience_list = experience_list.filter(
            models.Q(title__icontains=query) |
            models.Q(description__icontains=query) |
            models.Q(category__icontains=query)
        )
    data = []
    for exp in experience_list:
        data.append({
            "pk": str(exp.id),
            "fields": {
                "title": exp.title,
                "category": exp.category,
                "category_display": exp.get_category_display(),
                "description": exp.description,
                "started_at": exp.started_at.strftime("%Y-%m-%d") if exp.started_at else None,
                "ended_at": exp.ended_at.strftime("%Y-%m-%d") if exp.ended_at else None,
                "is_ongoing": exp.is_ongoing,
            }
        })
    return JsonResponse(data, safe=False)


def show_education(request):
    institution_query = request.GET.get("institution", "").strip()
    is_editor = request.user.is_authenticated and request.user.groups.filter(name="Editor").exists()

    context = {
        "name": "Ahsan",
        "fullname": "Ahsan Rifqi Prasetyo",
        "institution_query": institution_query,
        "form": EducationForm(),
        "is_editor": is_editor,
    }
    return render(request, "education.html", context)


def show_experience(request):
    title_query = request.GET.get("title", "").strip()
    context = {
        "name": "Ahsan",
        "title_query": title_query,
        "form": ExperienceForm(),
    }
    return render(request, "experience.html", context)


def show_skills(request):
    context = {
        "name": "Ahsan",
        "fullname": "Ahsan Rifqi Prasetyo",
        "skill_list": Skill.objects.all(),
    }
    return render(request, "skills.html", context)


def get_projects_json(request):
    title_query = request.GET.get("title", "").strip()
    projects = Project.objects.prefetch_related('starred_by').all()
    if title_query:
        projects = projects.filter(title__icontains=title_query)
    data = []
    for project in projects:
        starred_users = project.starred_by.all()
        is_starred = request.user in starred_users if request.user.is_authenticated else False
        starred_by_names = ", ".join([u.username for u in starred_users])
        data.append({
            "pk": str(project.id),
            "fields": {
                "title": project.title,
                "description": project.description,
                "tech_stack": project.tech_stack,
                "project_url": project.project_url,
                "project_image_url": project.project_image_url,
                "star_count": starred_users.count(),
                "is_starred": is_starred,
                "starred_by_names": starred_by_names,
                "starred_by": [[u.username] for u in starred_users],
            }
        })
    return JsonResponse(data, safe=False)

def show_projects(request):
    title_query = request.GET.get("title", "").strip()
    is_editor = request.user.is_authenticated and request.user.groups.filter(name="Editor").exists()
    context = {
        "name": "Ahsan",
        "title_query": title_query,
        "form": ProjectForm(),
        "is_editor": is_editor,
    }
    return render(request, "project.html", context)

@login_required(login_url="/login/")
def create_project(request):
    if not request.user.is_superuser:
        raise PermissionDenied
    is_auth = check_secret_code(request, post_key=None)
    form = ProjectForm(request.POST or None, is_header_authorized=is_auth)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "New project added successfully!")
        return redirect("main:show_projects")

    context = {
        "name": "Ahsan",
        "form": form,
    }
    return render(request, "projects_form.html", context)

@login_required(login_url="/login/")
def edit_project(request, project_id):
    if not is_editor_or_superuser(request.user):
        raise PermissionDenied

    project = get_object_or_404(Project, pk=project_id)
    is_auth = check_secret_code(request, post_key=None)
    form = ProjectForm(request.POST or None, instance=project, is_header_authorized=is_auth)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Project updated successfully!")
        return redirect("main:show_projects")

    context = {
        "name": "Ahsan",
        "form": form,
        "project": project,
        "is_edit": True,
    }
    return render(request, "projects_form.html", context)

@login_required(login_url="/login/")
def delete_project(request, project_id):
    if not request.user.is_superuser:
        raise PermissionDenied
    project = get_object_or_404(Project, pk=project_id)
    if request.method == "POST":
        if "password" in request.POST:
            if not check_secret_code(request, post_key="password"):
                messages.error(request, "Incorrect secret code! Project could not be deleted.")
                return redirect("main:show_projects")
        elif request.headers.get("X-Secret-Code") or request.headers.get("X-Secret-Key") or request.headers.get("X-Kode-Rahasia"):
            if not check_secret_code(request, post_key=None):
                messages.error(request, "Incorrect secret code! Project could not be deleted.")
                return redirect("main:show_projects")
        project.delete()
        messages.success(request, "Project deleted successfully!")
        return redirect("main:show_projects")
    return redirect("main:show_projects")


@login_required(login_url="/login/")
def toggle_star(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if request.method == "POST":
        if request.user in project.starred_by.all():
            project.starred_by.remove(request.user)
        else:
            project.starred_by.add(request.user)
    return redirect("main:show_projects")

@login_required(login_url="/login/")
def create_education(request): 
    if not request.user.is_superuser:
        raise PermissionDenied
    is_auth = check_secret_code(request, post_key=None)
    form = EducationForm(request.POST or None, is_header_authorized=is_auth)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "New education added successfully!")
        return redirect("main:show_education")

    context = {
        "name": "Ahsan",
        "form": form,
    }
    return render(request, "education_form.html", context)

@login_required(login_url="/login/")
def edit_education(request, education_id):
    if not is_editor_or_superuser(request.user):
        raise PermissionDenied

    education = get_object_or_404(Education, pk=education_id)
    is_auth = check_secret_code(request, post_key=None)
    form = EducationForm(request.POST or None, instance=education, is_header_authorized=is_auth)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Education entry updated successfully!")
        return redirect("main:show_education")

    context = {
        "name": "Ahsan",
        "form": form,
        "education": education,
        "is_edit": True,
    }
    return render(request, "education_form.html", context)

@login_required(login_url="/login/")
def create_experience(request):
    if not request.user.is_superuser:
        raise PermissionDenied
    
    is_auth = check_secret_code(request, post_key=None)
    form = ExperienceForm(request.POST or None, is_header_authorized=is_auth)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "New experience added successfully!")
        return redirect("main:show_experience")

    context = {
        "name": "Ahsan",
        "form": form,
    }
    return render(request, "experience_form.html", context)

@login_required(login_url="/login/")
def delete_education(request, education_id):
    if not request.user.is_superuser:
        raise PermissionDenied
    
    education = get_object_or_404(Education, pk=education_id)
    if request.method == "POST":
        if "password" in request.POST:
            if not check_secret_code(request, post_key="password"):
                messages.error(request, "Incorrect secret code! Education entry could not be deleted.")
                return redirect("main:show_education")
        elif request.headers.get("X-Secret-Code") or request.headers.get("X-Secret-Key") or request.headers.get("X-Kode-Rahasia"):
            if not check_secret_code(request, post_key=None):
                messages.error(request, "Incorrect secret code! Education entry could not be deleted.")
                return redirect("main:show_education")
        education.delete()
        messages.success(request, "Education entry deleted successfully!")
        return redirect("main:show_education")
    return redirect("main:show_education")

@login_required(login_url="/login/")
def delete_experience(request, experience_id):
    if not request.user.is_superuser:
        raise PermissionDenied
    experience = get_object_or_404(Experience, pk=experience_id)
    if request.method == "POST":
        if "password" in request.POST:
            if not check_secret_code(request, post_key="password"):
                messages.error(request, "Incorrect secret code! Experience entry could not be deleted.")
                return redirect("main:show_experience")
        elif request.headers.get("X-Secret-Code") or request.headers.get("X-Secret-Key") or request.headers.get("X-Kode-Rahasia"):
            if not check_secret_code(request, post_key=None):
                messages.error(request, "Incorrect secret code! Experience entry could not be deleted.")
                return redirect("main:show_experience")
        experience.delete()
        messages.success(request, "Experience entry deleted successfully!")
        return redirect("main:show_experience")
    return redirect("main:show_experience")

def register(request):
    form = UserCreationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Account has been created. Please login")
        return redirect("main:login")
    context = {
        "name" : "Ahsan",
        "form" : form,
    }
    return render(request, "register.html", context)

def login_user(request):
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        login(request, user)
        response = redirect("main:show_main")
        response.set_cookie('last_login', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        return response
    
    context = {
        "name": "Ahsan",
        "form": form,
    }
    return render(request, "login.html", context)

def logout_user(request):
    logout(request)
    response = redirect("main:show_main")
    response.delete_cookie('last_login')
    return response

@require_POST
def create_project_ajax(request):
    if not request.user.is_superuser:
        return JsonResponse(
            {"message": "Hanya pemilik portofolio yang dapat menambahkan proyek."},
            status=403,
        )
    form = ProjectForm(request.POST, is_header_authorized=True)
    if form.is_valid():
        project = form.save()
        return JsonResponse(
            {"message": "Proyek berhasil ditambahkan.", "pk": str(project.id)},
            status=201,
        )
    return JsonResponse({"errors": form.errors.get_json_data()}, status=400)


@require_POST
def create_education_ajax(request):
    if not request.user.is_superuser:
        return JsonResponse(
            {"message": "Hanya pemilik portofolio yang dapat menambahkan riwayat pendidikan."},
            status=403,
        )
    form = EducationForm(request.POST, is_header_authorized=True)
    if form.is_valid():
        education = form.save()
        return JsonResponse(
            {"message": "Riwayat pendidikan berhasil ditambahkan.", "pk": str(education.id)},
            status=201,
        )
    return JsonResponse({"errors": form.errors.get_json_data()}, status=400)


@require_POST
def create_experience_ajax(request):
    if not request.user.is_superuser:
        return JsonResponse(
            {"message": "Hanya pemilik portofolio yang dapat menambahkan pengalaman."},
            status=403,
        )
    form = ExperienceForm(request.POST, is_header_authorized=True)
    if form.is_valid():
        experience = form.save()
        return JsonResponse(
            {"message": "Pengalaman berhasil ditambahkan.", "pk": str(experience.id)},
            status=201,
        )
    return JsonResponse({"errors": form.errors.get_json_data()}, status=400)
