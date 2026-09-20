from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from main.models import Experience, Skill, Education


class MainTest(TestCase):
    def setUp(self):
        self.experience = Experience.objects.create(
            title="Asisten Dosen PBP",
            description="Membantu mahasiswa memahami pengembangan web.",
            category="part-time",
        )
        self.skill = Skill.objects.create(
            title="Programming Languages",
            badge="</>",
            description="Core languages used for frontend, software development, and algorithms.",
            skills_list="Python, Java, HTML5 & CSS3",
            order=1,
        )
        self.education = Education.objects.create(
            institution="Universitas Indonesia",
            degree="Sarjana (S1)",
            field_of_study="Sistem Informasi",
            start_year=2024,
            end_year=2028,
            gpa=3.85,
            description="Fokus pada rekayasa perangkat lunak dan sistem informasi korporat.",
        )

    def test_main_url_is_accessible(self):
        response = self.client.get(reverse("main:show_main"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")
        self.assertNotContains(response, self.experience.title)
        self.assertContains(response, f'href="{reverse("main:show_experience")}"')
        self.assertContains(response, f'href="{reverse("main:show_about")}"')
        self.assertContains(response, f'href="{reverse("main:show_education")}"')
        self.assertContains(response, f'href="{reverse("main:show_contact")}"')
        self.assertContains(response, "Python")
        self.assertContains(response, "Django")


    def test_about_page(self):
        response = self.client.get(reverse("main:show_about"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "about.html")
        self.assertContains(response, "About Me")
        self.assertContains(response, f'href="{reverse("main:show_main")}"')

    def test_nonexistent_page_returns_404(self):
        response = self.client.get("/halaman-yang-tidak-ada/")

        self.assertEqual(response.status_code, 404)

    def test_experience_model(self):
        self.assertEqual(str(self.experience), "Asisten Dosen PBP")
        self.assertEqual(self.experience.category, "part-time")
        self.assertTrue(self.experience.is_ongoing)

    def test_experience_page(self):
        response = self.client.get(reverse("main:show_experience"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "experience.html")
        self.assertContains(response, self.experience.title)
        self.assertContains(response, self.experience.description)
        self.assertContains(response, "Part-Time")
        self.assertContains(response, "Sedang berlangsung")
        self.assertContains(response, f'href="{reverse("main:show_main")}"')

    def test_empty_experience_page(self):
        Experience.objects.all().delete()
        response = self.client.get(reverse("main:show_experience"))

        self.assertContains(response, "Belum ada pengalaman yang ditambahkan.")

    def test_completed_experience(self):
        self.experience.ended_at = timezone.now()
        self.experience.save()
        response = self.client.get(reverse("main:show_experience"))
    
        self.assertFalse(self.experience.is_ongoing)
        self.assertContains(response, "Selesai")
        self.assertNotContains(response, "Sedang berlangsung")

    def test_skill_model(self):
        self.assertEqual(str(self.skill), "Programming Languages")
        self.assertEqual(self.skill.get_chips(), ["Python", "Java", "HTML5 & CSS3"])

    def test_skills_url_is_accessible_and_uses_template(self):
        """Kasus 1: URL dapat diakses dan menggunakan template yang tepat."""
        response = self.client.get(reverse("main:show_skills"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "skills.html")

    def test_skill_data_appears_on_page(self):
        """Kasus 2: Data model muncul di halaman HTML ketika ada data."""
        response = self.client.get(reverse("main:show_skills"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.skill.title)
        self.assertContains(response, "&lt;/&gt;")
        self.assertContains(response, self.skill.description)
        self.assertContains(response, "Python")
        self.assertContains(response, "Java")
        self.assertNotContains(response, "Belum ada keahlian yang ditambahkan.")

    def test_empty_skills_page(self):
        """Kasus 3: Halaman HTML menampilkan pesan kondisi kosong ketika belum ada data."""
        Skill.objects.all().delete()
        response = self.client.get(reverse("main:show_skills"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Belum ada keahlian yang ditambahkan.")

    def test_education_model(self):
        self.assertEqual(str(self.education), "Sarjana (S1) in Sistem Informasi - Universitas Indonesia")
        self.assertFalse(self.education.is_ongoing)
        ongoing_edu = Education.objects.create(
            institution="Universitas Indonesia",
            degree="S1",
            field_of_study="SI",
            start_year=2024,
        )
        self.assertTrue(ongoing_edu.is_ongoing)

    def test_education_url_is_accessible_and_uses_template(self):
        response = self.client.get(reverse("main:show_education"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "education.html")

    def test_education_data_appears_on_page(self):
        response = self.client.get(reverse("main:show_education"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.education.institution)
        self.assertContains(response, self.education.degree)
        self.assertContains(response, self.education.field_of_study)
        self.assertContains(response, "3.85")

    def test_empty_education_page(self):
        Education.objects.all().delete()
        response = self.client.get(reverse("main:show_education"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No education history has been added yet.")

    def test_education_form_fields_and_validation(self):
        from main.forms import EducationForm
        form = EducationForm()
        expected_fields = [
            "institution",
            "degree",
            "field_of_study",
            "start_year",
            "end_year",
            "gpa",
            "description",
            "password",
        ]
        for field in expected_fields:
            self.assertIn(field, form.fields)

        self.assertNotIn("id", form.fields)
        self.assertNotIn("created_at", form.fields)
        self.assertNotIn("updated_at", form.fields)

        # Test valid submission with header authorization
        valid_data = {
            "institution": "SMA Negeri 1",
            "degree": "SMA",
            "field_of_study": "MIPA",
            "start_year": 2021,
            "end_year": 2024,
            "gpa": "3.90",
            "description": "Juara Olimpiade",
        }
        form = EducationForm(data=valid_data, is_header_authorized=True)
        self.assertTrue(form.is_valid())

    def test_contact_page(self):
        response = self.client.get(reverse("main:show_contact"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "contact.html")
        self.assertContains(response, "Contact")
        self.assertContains(response, "GitHub")
        self.assertContains(response, "LinkedIn")
        self.assertContains(response, "mailto:ahsanrifqi02@gmail.com")
        self.assertContains(response, f'href="{reverse("main:show_main")}"')

    # Project Tests (Tutorial 03 Langkah 1)
    def test_create_project_get(self):
        response = self.client.get(reverse("main:create_project"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "projects_form.html")
        self.assertContains(response, "Add New Projects")
        self.assertContains(response, 'name="title"')
        self.assertContains(response, 'name="description"')
        self.assertContains(response, 'name="tech_stack"')
        self.assertContains(response, 'name="project_url"')
        self.assertContains(response, 'name="project_image_url"')

    @override_settings(SECRET_CODE="test-secret-123")
    def test_create_project_post_success_with_password(self):
        data = {
            "title": "Fern AI Assistant",
            "description": "Build personal AI Assistant",
            "tech_stack": "AWS, Gemini API, Python",
            "project_url": "https://github.com/kakBurhan/burhanquestv4",
            "project_image_url": "https://drive.google.com/thumbnail?id=123",
            "password": "test-secret-123",
        }
        response = self.client.post(reverse("main:create_project"), data=data)
        self.assertRedirects(response, reverse("main:show_projects"))

        from main.models import Project
        self.assertTrue(Project.objects.filter(title="Fern AI Assistant").exists())

    def test_create_project_post_wrong_password(self):
        data = {
            "title": "Unauthorized Project",
            "description": "Should fail",
            "tech_stack": "Python",
            "password": "wrongpassword",
        }
        response = self.client.post(reverse("main:create_project"), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Incorrect secret code! Access denied.")

        from main.models import Project
        self.assertFalse(Project.objects.filter(title="Unauthorized Project").exists())

    @override_settings(SECRET_CODE="test-secret-123")
    def test_create_project_post_with_header(self):
        data = {
            "title": "Header Auth Project",
            "description": "Created with secret header",
            "tech_stack": "Django",
        }
        response = self.client.post(
            reverse("main:create_project"),
            data=data,
            HTTP_X_SECRET_KEY="test-secret-123",
        )
        self.assertRedirects(response, reverse("main:show_projects"))

        from main.models import Project
        self.assertTrue(Project.objects.filter(title="Header Auth Project").exists())

    def test_show_projects_page(self):
        from main.models import Project
        Project.objects.create(
            title="Portfolio Website",
            description="My personal portfolio",
            tech_stack="Django, HTML, CSS",
        )
        response = self.client.get(reverse("main:show_projects"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "project.html")
        self.assertContains(response, "Portfolio Website")
        self.assertContains(response, "Projects")

    def test_show_projects_search(self):
        from main.models import Project
        Project.objects.create(
            title="Fern AI Assistant",
            description="AI Assistant",
            tech_stack="Python",
        )
        Project.objects.create(
            title="Living Green Lantern's Bird",
            description="Green lantern creature",
            tech_stack="Creativity",
        )
        response = self.client.get(reverse("main:show_projects") + "?title=Fern")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Fern AI Assistant")
        self.assertNotContains(response, "Living Green Lantern's Bird")

    def test_get_projects_json(self):
        from main.models import Project
        import json
        Project.objects.create(
            title="Fern AI Assistant",
            description="AI Assistant",
            tech_stack="Python",
        )
        response = self.client.get(reverse("main:get_projects_json"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["content-type"], "application/json")
        data = json.loads(response.content)
        self.assertTrue(any(item["fields"]["title"] == "Fern AI Assistant" for item in data))

    def test_get_projects_json_filter(self):
        from main.models import Project
        import json
        Project.objects.create(
            title="Fern AI Assistant",
            description="AI Assistant",
            tech_stack="Python",
        )
        Project.objects.create(
            title="Living Green Lantern's Bird",
            description="Green lantern",
            tech_stack="Creativity",
        )
        response = self.client.get(reverse("main:get_projects_json") + "?title=Lantern")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["fields"]["title"], "Living Green Lantern's Bird")

    @override_settings(SECRET_CODE="test-secret-123")
    def test_delete_project_with_password(self):
        from main.models import Project
        project = Project.objects.create(
            title="Temporary Project",
            description="Will be deleted",
            tech_stack="Python",
        )
        response = self.client.post(
            reverse("main:delete_project", kwargs={"project_id": project.id}),
            data={"password": "test-secret-123"},
        )
        self.assertRedirects(response, reverse("main:show_projects"))
        self.assertFalse(Project.objects.filter(id=project.id).exists())

    def test_delete_project_wrong_password(self):
        from main.models import Project
        project = Project.objects.create(
            title="Protected Project",
            description="Should not be deleted",
            tech_stack="Python",
        )
        response = self.client.post(
            reverse("main:delete_project", kwargs={"project_id": project.id}),
            data={"password": "wrongpassword"},
        )
        self.assertRedirects(response, reverse("main:show_projects"))
        self.assertTrue(Project.objects.filter(id=project.id).exists())

    @override_settings(SECRET_CODE="test-secret-123")
    def test_delete_project_with_header(self):
        from main.models import Project
        project = Project.objects.create(
            title="API Deleted Project",
            description="Deleted via header",
            tech_stack="Python",
        )
        response = self.client.post(
            reverse("main:delete_project", kwargs={"project_id": project.id}),
            HTTP_X_SECRET_KEY="test-secret-123",
        )
        self.assertRedirects(response, reverse("main:show_projects"))
        self.assertFalse(Project.objects.filter(id=project.id).exists())

