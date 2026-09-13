from django.urls import path

from main.views import show_main, show_about, show_experience

app_name = "main"

urlpatterns = [
    path("", show_main, name="show_main"),
    path("about/", show_about, name="show_about"),
    path("experience/", show_experience, name="show_experience"),
]