from django.shortcuts import render

from main.models import Experience, Skill



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
