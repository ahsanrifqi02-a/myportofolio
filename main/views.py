from django.conf import settings
from django.contrib import messages
from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from main.forms import ProjectForm, EducationForm
from main.models import Experience, Skill, Project, Education


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



def show_main(request):
    context = {
        "name": "Ahsan",
        "npm": "2506624266",
        "study_program": "S1 Sistem Informasi",
        "bio": (
            "An Information Systems undergraduate at Universitas Indonesia bridging software engineering, data architecture, and business strategy. I specialize in transforming complex data infrastructure into scalable digital solutions and actionable intelligence that streamline operations and accelerate decision-making."
        ),
        "fullname": "Ahsan Rifqi Prasetyo",
        "skill_list": Skill.objects.all(),
    }
    return render(request, "index.html", context)


def show_education(request):
    context = {
        "name": "Ahsan",
        "fullname": "Ahsan Rifqi Prasetyo",
        "education_list": Education.objects.all(),
    }
    return render(request, "education.html", context)


def show_about(request):
    context = {
        "name": "Ahsan",
        "fullname": "Ahsan Rifqi Prasetyo",
        "bio": (
            "An Information Systems undergraduate at Universitas Indonesia bridging software engineering, "
            "data architecture, and business strategy. I specialize in transforming complex data infrastructure "
            "into scalable digital solutions and actionable intelligence that streamline operations and accelerate "
            "decision-making."
        ),
    }
    return render(request, "about.html", context)


def show_experience(request):
    context = {
        "name": "Ahsan",
        "experience_list": Experience.objects.all(),
    }
    return render(request, "experience.html", context)


def show_skills(request):
    context = {
        "name": "Ahsan",
        "fullname": "Ahsan Rifqi Prasetyo",
        "skill_list": Skill.objects.all(),
    }
    return render(request, "skills.html", context)


def show_contact(request):
    context = {
        "name": "Ahsan",
        "fullname": "Ahsan Rifqi Prasetyo",
    }
    return render(request, "contact.html", context)


def get_projects_json(request):
    title_query = request.GET.get("title", "").strip()
    projects = Project.objects.all()
    if title_query:
        projects = projects.filter(title__icontains=title_query)
    projects_json = serializers.serialize("json", projects)
    return HttpResponse(projects_json, content_type="application/json")


def show_projects(request):
    json_response = get_projects_json(request)
    projects = serializers.deserialize(
        "json",
        json_response.content.decode("utf-8"),
    )
    projects = [project.object for project in projects]
    title_query = request.GET.get("title", "").strip()

    context = {
        "name": "Ahsan",
        "project_list": projects,
        "title_query": title_query,
    }
    return render(request, "project.html", context)


def create_project(request):
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


def delete_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if request.method == "POST":
        if check_secret_code(request, post_key="password"):
            project.delete()
            messages.success(request, "Project deleted successfully!")
            return redirect("main:show_projects")
        else:
            messages.error(request, "Incorrect secret code! Project could not be deleted.")
            return redirect("main:show_projects")
    return redirect("main:show_projects")



