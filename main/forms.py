from django import forms
from django.conf import settings
from django.forms import ModelForm, TextInput, Textarea, URLInput, PasswordInput, NumberInput
from main.models import Project, Education

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


class EducationForm(ModelForm):
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
        "institution",
        "degree",
        "field_of_study",
        "start_year",
        "end_year",
        "gpa",
        "description",
        "password",
    ]

    class Meta:
        model = Education
        fields = [
            "institution",
            "degree",
            "field_of_study",
            "start_year",
            "end_year",
            "gpa",
            "description",
        ]
        labels = {
            "institution": "Institution / School",
            "degree": "Degree / Certificate",
            "field_of_study": "Field of Study / Major",
            "start_year": "Start Year",
            "end_year": "End Year",
            "gpa": "GPA / Grade",
            "description": "Description / Activities",
        }
        widgets = {
            "institution": TextInput(
                attrs={
                    "placeholder": "Universitas Indonesia",
                    "maxlength": 255,
                }
            ),
            "degree": TextInput(
                attrs={
                    "placeholder": "Undergraduate (S1)",
                    "maxlength": 100,
                }
            ),
            "field_of_study": TextInput(
                attrs={
                    "placeholder": "Information Systems",
                    "maxlength": 255,
                }
            ),
            "start_year": NumberInput(
                attrs={
                    "placeholder": "2024",
                    "min": 1900,
                    "max": 2100,
                }
            ),
            "end_year": NumberInput(
                attrs={
                    "placeholder": "2028 (Leave empty if ongoing)",
                    "min": 1900,
                    "max": 2100,
                }
            ),
            "gpa": NumberInput(
                attrs={
                    "placeholder": "3.85",
                    "step": "0.01",
                    "min": 0,
                    "max": 4,
                }
            ),
            "description": Textarea(
                attrs={
                    "placeholder": "Describe your academic achievements, focus, or relevant coursework...",
                    "rows": 3,
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
