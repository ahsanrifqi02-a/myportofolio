from django import forms
from django.conf import settings
from django.forms import ModelForm, TextInput, Textarea, URLInput, PasswordInput
from main.models import Project

class ProjectForm(ModelForm):
    password = forms.CharField(
        widget=PasswordInput(
            attrs={
                "placeholder": "Enter secret code",
                "autocomplete": "current-password",
            }
        ),
        label="Secret Code",
        required=False,
    )

    field_order = [
        "title",
        "description",
        "tech_stack",
        "project_url",
        "project_image_url",
        "password",
    ]

    class Meta:
        model = Project
        fields = [
            "title",
            "description",
            "tech_stack",
            "project_url",
            "project_image_url",
        ]
        labels = {
            "title": "Project Title",
            "description": "Project Description",
            "tech_stack": "Technologies Used",
            "project_url": "Project URL",
            "project_image_url": "Project Image URL",
        }
        widgets = {
            "title": TextInput(
                attrs={
                    "placeholder": "Portfolio Website",
                    "maxlength": 255,
                }
            ),
            "description": Textarea(
                attrs={
                    "placeholder": "Tell us about your project",
                    "rows": 3,
                }
            ),
            "tech_stack": TextInput(
                attrs={
                    "placeholder": "Django, Python, HTML, CSS",
                }
            ),
            "project_url": URLInput(
                attrs={
                    "placeholder": "https://github.com/ahsanrifqi02-a/placeholder",
                }
            ),
            "project_image_url": URLInput(
                attrs={
                    "placeholder": "https://drive.google.com/thumbnail?id=...&sz=w1000",
                }
            ),
        }

    def __init__(self, *args, is_header_authorized=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_header_authorized = is_header_authorized

    def clean(self):
        cleaned_data = super().clean()
        if not self.is_header_authorized:
            password = cleaned_data.get("password")
            secret_code = getattr(settings, "SECRET_CODE", "")
            if not password:
                self.add_error("password", "Secret code is required.")
            elif not secret_code or password != secret_code:
                self.add_error("password", "Incorrect secret code! Access denied.")
        return cleaned_data
