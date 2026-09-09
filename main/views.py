from django.shortcuts import render

from main.models import Experience


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


def show_experience(request):
    context = {
        "name": "Ahsan",
        "experience_list": Experience.objects.all(),
    }
    return render(request, "experience.html", context)