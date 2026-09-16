from django.contrib import messages
from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from main.forms import ProjectForm
from main.models import Experience, Skill, Project



def show_main(request):
    context = {
        "name": "Ahsan",
        "npm": "2506624266",
        "study_program": "S1 Sistem Informasi",
        "bio": (
            "An Information Systems undergraduate at Universitas Indonesia bridging software engineering, data architecture, and business strategy. I specialize in transforming complex data infrastructure into scalable digital solutions and actionable intelligence that streamline operations and accelerate decision-making."
        ),
        "fullname": "Ahsan Rifqi Prasetyo"
    }
    return render(request, "index.html", context)


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
    form = ProjectForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Proyek baru berhasil ditambahkan!")
        return redirect("main:show_projects")

    context = {
        "name": "Ahsan",
        "form": form,
    }
    return render(request, "projects_form.html", context)


def delete_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if request.method == "POST":
        project.delete()
        messages.success(request, "Project berhasil dihapus!")
        return redirect("main:show_projects")
    return redirect("main:show_projects")



