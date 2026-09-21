from django.urls import path

from main.views import (
    show_main,
    show_about,
    show_experience,
    show_education,
    show_skills,
    show_contact,
    show_projects,
    create_project,
    create_education,
    edit_education,
    create_experience,
    get_projects_json,
    get_education_json,
    get_experience_json,
    delete_project,
    delete_education,
    delete_experience,
)

app_name = "main"

urlpatterns = [
    path("", show_main, name="show_main"),
    path("about/", show_about, name="show_about"),
    path("experience/", show_experience, name="show_experience"),
    path("experience/add/", create_experience, name="create_experience"),
    path("experience/<uuid:experience_id>/delete/", delete_experience, name="delete_experience"),
    path("education/", show_education, name="show_education"),
    path("education/add/", create_education, name="create_education"),
    path("education/<uuid:education_id>/edit/", edit_education, name="edit_education"),
    path("education/<uuid:education_id>/delete/", delete_education, name="delete_education"),
    path("skills/", show_skills, name="show_skills"),
    path("contact/", show_contact, name="show_contact"),
    path("projects/", show_projects, name="show_projects"),
    path("projects/add/", create_project, name="create_project"),
    path("api/projects/", get_projects_json, name="get_projects_json"),
    path("api/education/", get_education_json, name="get_education_json"),
    path("api/experience/", get_experience_json, name="get_experience_json"),
    path("projects/<uuid:project_id>/delete/", delete_project, name="delete_project"),
]

