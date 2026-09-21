from django import forms
from django.conf import settings
from django.forms import ModelForm, TextInput, Textarea, URLInput, PasswordInput, NumberInput
from main.models import Project, Education, Experience

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
        "description",
        "logo_url",
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
            "description",
            "logo_url",
        ]
        labels = {
            "institution": "Institution / School",
            "degree": "Degree / Level",
            "field_of_study": "Field of Study / Major",
            "start_year": "Start Year",
            "end_year": "End Year",
            "description": "Description / Activities",
            "logo_url": "Logo / Image URL",
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
                    "placeholder": "Undergraduate Student / S1",
                    "maxlength": 100,
                }
            ),
            "field_of_study": TextInput(
                attrs={
                    "placeholder": "Information System (or leave blank if not applicable)",
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
            "description": Textarea(
                attrs={
                    "placeholder": "Describe your academic focus, activities, or achievements...",
                    "rows": 3,
                }
            ),
            "logo_url": URLInput(
                attrs={
                    "placeholder": "https://example.com/logo.png (optional)",
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


class ExperienceForm(ModelForm):
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
        "category",
        "description",
        "started_at",
        "ended_at",
        "password",
    ]

    class Meta:
        model = Experience
        fields = [
            "title",
            "category",
            "description",
            "started_at",
            "ended_at",
        ]
        labels = {
            "title": "Role / Position Title",
            "category": "Category",
            "description": "Description / Responsibilities",
            "started_at": "Start Date",
            "ended_at": "End Date (Leave empty if ongoing)",
        }
        widgets = {
            "title": TextInput(
                attrs={
                    "placeholder": "e.g. Asisten Dosen PBP",
                    "maxlength": 255,
                }
            ),
            "category": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "description": Textarea(
                attrs={
                    "placeholder": "Describe your role, responsibilities, and achievements...",
                    "rows": 4,
                }
            ),
            "started_at": forms.DateInput(
                attrs={
                    "type": "date",
                }
            ),
            "ended_at": forms.DateInput(
                attrs={
                    "type": "date",
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
