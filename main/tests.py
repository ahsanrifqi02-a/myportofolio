from django.contrib.auth.models import User, Group
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from main.models import Experience, Skill, Education, Project


class MainTest(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(
            username="admin_test",
            password="adminpassword123",
            email="admin@test.com",
        )
        self.regular_user = User.objects.create_user(
            username="user_test",
            password="userpassword123",
        )
        self.editor_group, _ = Group.objects.get_or_create(name="Editor")
        self.editor_user = User.objects.create_user(
            username="editor_test",
            password="editorpassword123",
        )
        self.editor_user.groups.add(self.editor_group)
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
            description="Fokus pada rekayasa perangkat lunak dan sistem informasi korporat.",
        )

    def test_main_url_is_accessible(self):
        response = self.client.get(reverse("main:show_main"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")
        self.assertNotContains(response, self.experience.title)
        self.assertContains(response, f'href="{reverse("main:show_experience")}"')
        self.assertContains(response, f'href="{reverse("main:show_education")}"')
        self.assertContains(response, 'href="/#about"')
        self.assertContains(response, 'href="/#contact"')
        self.assertContains(response, "About Me")
        self.assertContains(response, "Contact")
        self.assertContains(response, "Python")
        self.assertContains(response, "Django")

    def test_about_section_on_main_page(self):
        response = self.client.get(reverse("main:show_main"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="about"')
        self.assertContains(response, "About Me")
        self.assertContains(response, "Information Systems")

    def test_nonexistent_page_returns_404(self):
        response = self.client.get("/halaman-yang-tidak-ada/")

        self.assertEqual(response.status_code, 404)

    def test_experience_model(self):
        self.assertEqual(str(self.experience), "Asisten Dosen PBP")
        self.assertEqual(self.experience.category, "part-time")
        self.assertTrue(self.experience.is_ongoing)

    def test_experience_page(self):
        self.client.force_login(self.superuser)
        response = self.client.get(reverse("main:show_experience"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "experience.html")
        self.assertContains(response, 'popovertarget="add-experience-modal"')
        self.assertContains(response, "Add Experience")
        self.assertContains(response, 'id="experience-list"')
        self.assertContains(response, 'id="experience-search-form"')
        self.assertContains(response, 'id="loading"')
        self.assertContains(response, 'id="empty"')
        self.assertContains(response, 'id="error"')

    def test_empty_experience_page(self):
        Experience.objects.all().delete()
        response = self.client.get(reverse("main:show_experience"))

        self.assertContains(response, "Belum ada pengalaman yang ditambahkan.")

    def test_completed_experience(self):
        self.experience.ended_at = timezone.now()
        self.experience.save()
        self.assertFalse(self.experience.is_ongoing)

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
        self.client.force_login(self.superuser)
        response = self.client.get(reverse("main:show_education"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "education.html")
        self.assertContains(response, 'popovertarget="add-education-modal"')
        self.assertContains(response, "Add Education")

    def test_education_data_appears_on_page(self):
        self.client.force_login(self.superuser)
        response = self.client.get(reverse("main:show_education"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="education-timeline"')
        self.assertContains(response, 'id="education-search-form"')
        self.assertContains(response, 'id="loading"')
        self.assertContains(response, 'id="empty"')
        self.assertContains(response, 'id="error"')

    def test_empty_education_page(self):
        response = self.client.get(reverse("main:show_education"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No education history added or found yet.")

    @override_settings(SECRET_CODE="test-secret-123")
    def test_education_form_fields_and_validation(self):
        from main.forms import EducationForm
        form = EducationForm()
        expected_fields = [
            "institution",
            "degree",
            "field_of_study",
            "start_year",
            "end_year",
            "description",
            "logo_url",
            "password",
        ]
        for field in expected_fields:
            self.assertIn(field, form.fields)

        # Verify id and timestamp fields are excluded
        self.assertNotIn("id", form.fields)
        self.assertNotIn("created_at", form.fields)
        self.assertNotIn("updated_at", form.fields)
        self.assertNotIn("gpa", form.fields)

        # Test valid submission with password
        valid_data = {
            "institution": "SMA Negeri 1",
            "degree": "High School Diploma",
            "field_of_study": "Natural Sciences (MIPA)",
            "start_year": 2021,
            "end_year": 2024,
            "description": "Science competition participant.",
            "logo_url": "https://example.com/logo.png",
            "password": "test-secret-123",
        }
        form = EducationForm(data=valid_data)
        self.assertTrue(form.is_valid())
        saved_edu = form.save()
        self.assertEqual(saved_edu.institution, "SMA Negeri 1")

        # Test submission with wrong password
        invalid_data = valid_data.copy()
        invalid_data["password"] = "wrong-code"
        invalid_form = EducationForm(data=invalid_data)
        self.assertFalse(invalid_form.is_valid())
        self.assertIn("password", invalid_form.errors)

        # Test valid submission with header authorization
        header_form = EducationForm(data=valid_data, is_header_authorized=True)
        self.assertTrue(header_form.is_valid())

    def test_create_education_get(self):
        self.client.force_login(self.superuser)
        response = self.client.get(reverse("main:create_education"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "education_form.html")
        self.assertContains(response, "Add New Education")

    @override_settings(SECRET_CODE="test-secret-123")
    def test_create_education_post_success(self):
        self.client.force_login(self.superuser)
        data = {
            "institution": "Stanford University",
            "degree": "Master of Science",
            "field_of_study": "Computer Science",
            "start_year": 2028,
            "end_year": 2030,
            "description": "AI & Systems specialization",
            "password": "test-secret-123",
        }
        response = self.client.post(reverse("main:create_education"), data=data)
        self.assertRedirects(response, reverse("main:show_education"))
        self.assertTrue(Education.objects.filter(institution="Stanford University").exists())

    def test_edit_education_get(self):
        self.client.force_login(self.superuser)
        response = self.client.get(reverse("main:edit_education", kwargs={"education_id": self.education.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "education_form.html")
        self.assertContains(response, "Edit Education")
        self.assertContains(response, self.education.institution)

    @override_settings(SECRET_CODE="test-secret-123")
    def test_edit_education_post_success(self):
        self.client.force_login(self.superuser)
        data = {
            "institution": "Universitas Indonesia Updated",
            "degree": "Sarjana (S1)",
            "field_of_study": "Sistem Informasi",
            "start_year": 2024,
            "end_year": 2028,
            "description": "Updated academic description",
            "password": "test-secret-123",
        }
        response = self.client.post(
            reverse("main:edit_education", kwargs={"education_id": self.education.id}),
            data=data,
        )
        self.assertRedirects(response, reverse("main:show_education"))
        self.education.refresh_from_db()
        self.assertEqual(self.education.institution, "Universitas Indonesia Updated")

    def test_edit_education_post_wrong_password(self):
        self.client.force_login(self.superuser)
        data = {
            "institution": "Hacked University",
            "degree": "Sarjana (S1)",
            "field_of_study": "Sistem Informasi",
            "start_year": 2024,
            "password": "wrong-password",
        }
        response = self.client.post(
            reverse("main:edit_education", kwargs={"education_id": self.education.id}),
            data=data,
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Incorrect secret code! Access denied.")
        self.education.refresh_from_db()
        self.assertNotEqual(self.education.institution, "Hacked University")

    def test_create_experience_get(self):
        self.client.force_login(self.superuser)
        response = self.client.get(reverse("main:create_experience"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "experience_form.html")
        self.assertContains(response, "Add New Experience")

    @override_settings(SECRET_CODE="test-secret-123")
    def test_create_experience_post_success(self):
        self.client.force_login(self.superuser)
        data = {
            "title": "Backend Intern",
            "category": "internship",
            "description": "Building microservices with Django",
            "started_at": "2026-06-01",
            "ended_at": "2026-08-31",
            "password": "test-secret-123",
        }
        response = self.client.post(reverse("main:create_experience"), data=data)
        self.assertRedirects(response, reverse("main:show_experience"))
        created = Experience.objects.filter(title="Backend Intern").first()
        self.assertIsNotNone(created)
        self.assertEqual(str(created.started_at), "2026-06-01")
        self.assertEqual(str(created.ended_at), "2026-08-31")

    def test_contact_section_on_main_page(self):
        response = self.client.get(reverse("main:show_main"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="contact"')
        self.assertContains(response, "Contact")
        self.assertContains(response, "GitHub")
        self.assertContains(response, "LinkedIn")
        self.assertContains(response, "mailto:ahsanrifqi02@gmail.com")

    # Project Tests (Tutorial 03 Langkah 1)
    def test_create_project_get(self):
        self.client.force_login(self.superuser)
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
        self.client.force_login(self.superuser)
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
        self.client.force_login(self.superuser)
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
        self.client.force_login(self.superuser)
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
        self.assertContains(response, "Projects")
        self.assertContains(response, 'id="grid"')
        self.assertContains(response, 'id="loading"')

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
        self.assertContains(response, 'value="Fern"')

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

    def test_get_education_json(self):
        import json
        response = self.client.get(reverse("main:get_education_json"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["content-type"], "application/json")
        data = json.loads(response.content)
        self.assertTrue(any(item["fields"]["institution"] == self.education.institution for item in data))

    def test_get_education_json_filter(self):
        import json
        Education.objects.create(
            institution="Oxford University",
            degree="Master",
            field_of_study="CS",
            start_year=2025,
        )
        response = self.client.get(reverse("main:get_education_json") + "?institution=Oxford")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["fields"]["institution"], "Oxford University")

    def test_get_experience_json(self):
        import json
        response = self.client.get(reverse("main:get_experience_json"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["content-type"], "application/json")
        data = json.loads(response.content)
        self.assertTrue(any(item["fields"]["title"] == self.experience.title for item in data))

    @override_settings(SECRET_CODE="test-secret-123")
    def test_delete_project_with_password(self):
        self.client.force_login(self.superuser)
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
        self.client.force_login(self.superuser)
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
        self.client.force_login(self.superuser)
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

    @override_settings(SECRET_CODE="test-secret-123")
    def test_delete_education_with_password(self):
        self.client.force_login(self.superuser)
        edu = Education.objects.create(
            institution="Oxford University",
            degree="Master",
            field_of_study="Computer Science",
            start_year=2025,
            end_year=2026,
        )
        response = self.client.post(
            reverse("main:delete_education", kwargs={"education_id": edu.id}),
            data={"password": "test-secret-123"},
            follow=True,
        )
        self.assertRedirects(response, reverse("main:show_education"))
        self.assertFalse(Education.objects.filter(id=edu.id).exists())
        self.assertContains(response, "Education entry deleted successfully!")

    def test_delete_education_wrong_password(self):
        self.client.force_login(self.superuser)
        edu = Education.objects.create(
            institution="Cambridge University",
            degree="Master",
            field_of_study="Computer Science",
            start_year=2025,
            end_year=2026,
        )
        response = self.client.post(
            reverse("main:delete_education", kwargs={"education_id": edu.id}),
            data={"password": "wrongpassword"},
            follow=True,
        )
        self.assertRedirects(response, reverse("main:show_education"))
        self.assertTrue(Education.objects.filter(id=edu.id).exists())
        self.assertContains(response, "Incorrect secret code! Education entry could not be deleted.")

    @override_settings(SECRET_CODE="test-secret-123")
    def test_delete_education_with_header(self):
        self.client.force_login(self.superuser)
        edu = Education.objects.create(
            institution="MIT",
            degree="PhD",
            field_of_study="Artificial Intelligence",
            start_year=2026,
        )
        response = self.client.post(
            reverse("main:delete_education", kwargs={"education_id": edu.id}),
            HTTP_X_SECRET_KEY="test-secret-123",
        )
        self.assertRedirects(response, reverse("main:show_education"))
        self.assertFalse(Education.objects.filter(id=edu.id).exists())

    def test_delete_education_404(self):
        self.client.force_login(self.superuser)
        import uuid
        response = self.client.post(
            reverse("main:delete_education", kwargs={"education_id": uuid.uuid4()}),
            data={"password": "test-secret-123"},
        )
        self.assertEqual(response.status_code, 404)

    @override_settings(SECRET_CODE="test-secret-123")
    def test_delete_experience_with_password(self):
        self.client.force_login(self.superuser)
        exp = Experience.objects.create(
            title="Software Engineering Intern",
            description="Working on backend systems.",
            category="internship",
        )
        response = self.client.post(
            reverse("main:delete_experience", kwargs={"experience_id": exp.id}),
            data={"password": "test-secret-123"},
            follow=True,
        )
        self.assertRedirects(response, reverse("main:show_experience"))
        self.assertFalse(Experience.objects.filter(id=exp.id).exists())
        self.assertContains(response, "Experience entry deleted successfully!")

    def test_delete_experience_wrong_password(self):
        self.client.force_login(self.superuser)
        exp = Experience.objects.create(
            title="Teaching Assistant",
            description="Teaching Python programming.",
            category="part-time",
        )
        response = self.client.post(
            reverse("main:delete_experience", kwargs={"experience_id": exp.id}),
            data={"password": "wrongpassword"},
            follow=True,
        )
        self.assertRedirects(response, reverse("main:show_experience"))
        self.assertTrue(Experience.objects.filter(id=exp.id).exists())
        self.assertContains(response, "Incorrect secret code! Experience entry could not be deleted.")

    @override_settings(SECRET_CODE="test-secret-123")
    def test_delete_experience_with_header(self):
        self.client.force_login(self.superuser)
        exp = Experience.objects.create(
            title="Research Assistant",
            description="AI lab research.",
            category="internship",
        )
        response = self.client.post(
            reverse("main:delete_experience", kwargs={"experience_id": exp.id}),
            HTTP_X_SECRET_KEY="test-secret-123",
        )
        self.assertRedirects(response, reverse("main:show_experience"))
        self.assertFalse(Experience.objects.filter(id=exp.id).exists())

    def test_delete_experience_404(self):
        self.client.force_login(self.superuser)
        import uuid
        response = self.client.post(
            reverse("main:delete_experience", kwargs={"experience_id": uuid.uuid4()}),
            data={"password": "test-secret-123"},
        )
        self.assertEqual(response.status_code, 404)

    # Tutorial 04 Tests: Authentication, Sessions, Cookies & Authorization
    def test_register_view_get(self):
        response = self.client.get(reverse("main:register"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "register.html")
        self.assertContains(response, "Create Account")
        self.assertContains(response, 'name="username"')

    def test_register_view_post_success(self):
        data = {
            "username": "newuser",
            "password1": "StrongP@ssw0rd!",
            "password2": "StrongP@ssw0rd!",
        }
        response = self.client.post(reverse("main:register"), data=data)
        self.assertRedirects(response, reverse("main:login"))
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_login_view_get(self):
        response = self.client.get(reverse("main:login"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "login.html")
        self.assertContains(response, "Login")

    def test_login_user_post_sets_cookie_and_session(self):
        data = {
            "username": "user_test",
            "password": "userpassword123",
        }
        response = self.client.post(reverse("main:login"), data=data)
        self.assertRedirects(response, reverse("main:show_main"))
        self.assertIn("last_login", response.cookies)
        self.assertTrue(response.cookies["last_login"].value)

    def test_logout_user_deletes_cookie(self):
        self.client.force_login(self.regular_user)
        self.client.cookies["last_login"] = "2026-09-27 12:00:00"
        response = self.client.get(reverse("main:logout"))
        self.assertRedirects(response, reverse("main:show_main"))
        self.assertEqual(response.cookies["last_login"].value, "")

    def test_show_main_displays_last_login_cookie(self):
        self.client.cookies["last_login"] = "2026-09-27 23:59:59"
        response = self.client.get(reverse("main:show_main"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "2026-09-27 23:59:59")
        self.assertContains(response, "Last Login Session")

    def test_unauthenticated_cannot_create_project(self):
        response = self.client.get(reverse("main:create_project"))
        self.assertRedirects(response, f"{reverse('main:login')}?next={reverse('main:create_project')}")

    def test_unauthenticated_cannot_delete_project(self):
        project = Project.objects.create(
            title="Unauth Delete",
            description="Testing delete",
            tech_stack="Django",
        )
        url = reverse("main:delete_project", kwargs={"project_id": project.id})
        response = self.client.post(url, data={"password": "any"})
        self.assertRedirects(response, f"{reverse('main:login')}?next={url}")

    def test_regular_user_create_project_forbidden(self):
        self.client.force_login(self.regular_user)
        response = self.client.get(reverse("main:create_project"))
        self.assertEqual(response.status_code, 403)

    def test_regular_user_delete_project_forbidden(self):
        self.client.force_login(self.regular_user)
        project = Project.objects.create(
            title="Forbidden Delete",
            description="Testing 403",
            tech_stack="Django",
        )
        url = reverse("main:delete_project", kwargs={"project_id": project.id})
        response = self.client.post(url, data={"password": "any"})
        self.assertEqual(response.status_code, 403)

    def test_toggle_star_authenticated(self):
        project = Project.objects.create(
            title="Starrable Project",
            description="Testing star",
            tech_stack="Django",
        )
        self.client.force_login(self.regular_user)
        url = reverse("main:toggle_star", kwargs={"project_id": project.id})

        # Add star
        response = self.client.post(url)
        self.assertRedirects(response, reverse("main:show_projects"))
        self.assertTrue(project.starred_by.filter(id=self.regular_user.id).exists())

        # Remove star
        response = self.client.post(url)
        self.assertRedirects(response, reverse("main:show_projects"))
        self.assertFalse(project.starred_by.filter(id=self.regular_user.id).exists())

    def test_toggle_star_unauthenticated(self):
        project = Project.objects.create(
            title="Unauth Star",
            description="Testing unauth star",
            tech_stack="Django",
        )
        url = reverse("main:toggle_star", kwargs={"project_id": project.id})
        response = self.client.post(url)
        self.assertRedirects(response, f"{reverse('main:login')}?next={url}")

    def test_get_projects_json_natural_foreign_keys(self):
        import json
        project = Project.objects.create(
            title="Natural Key Project",
            description="Testing JSON",
            tech_stack="Django",
        )
        project.starred_by.add(self.regular_user)

        response = self.client.get(reverse("main:get_projects_json") + f"?title=Natural")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data), 1)
        # Should be list of natural keys [["username"]] rather than IDs [1]
        self.assertEqual(data[0]["fields"]["starred_by"], [[self.regular_user.username]])

    def test_project_page_ui_superuser_vs_regular_user(self):
        project = Project.objects.create(
            title="UI Project",
            description="Testing UI",
            tech_stack="Django",
        )

        res_anon = self.client.get(reverse("main:show_projects"))
        self.assertNotContains(res_anon, "popovertarget=\"add-project-modal\"")
        self.assertNotContains(res_anon, "id=\"add-project-modal\"")
        self.assertContains(res_anon, "id=\"grid\"")
        self.assertContains(res_anon, "id=\"loading\"")

        self.client.force_login(self.regular_user)
        res_user = self.client.get(reverse("main:show_projects"))
        self.assertNotContains(res_user, "popovertarget=\"add-project-modal\"")
        self.assertNotContains(res_user, "id=\"add-project-modal\"")

        self.client.force_login(self.superuser)
        res_admin = self.client.get(reverse("main:show_projects"))
        self.assertContains(res_admin, "popovertarget=\"add-project-modal\"")
        self.assertContains(res_admin, "id=\"add-project-modal\"")

    # Tutorial 05 Tests: Web Interactivity with JavaScript & AJAX
    def test_get_projects_json_ajax_format_and_star_status(self):
        import json
        project = Project.objects.create(
            title="Interactive App",
            description="Testing AJAX JSON format",
            tech_stack="JavaScript, Django",
            project_url="https://example.com",
            project_image_url="https://example.com/img.png",
        )
        project.starred_by.add(self.regular_user)

        res = self.client.get(reverse("main:get_projects_json"))
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.content)
        self.assertEqual(len(data), 1)
        item = data[0]
        self.assertEqual(item["pk"], str(project.id))
        self.assertEqual(item["fields"]["title"], "Interactive App")
        self.assertEqual(item["fields"]["star_count"], 1)
        self.assertFalse(item["fields"]["is_starred"])
        self.assertEqual(item["fields"]["starred_by_names"], self.regular_user.username)

        self.client.force_login(self.regular_user)
        res_auth = self.client.get(reverse("main:get_projects_json"))
        data_auth = json.loads(res_auth.content)
        self.assertTrue(data_auth[0]["fields"]["is_starred"])

    def test_create_project_ajax_superuser_success(self):
        self.client.force_login(self.superuser)
        data = {
            "title": "AJAX Portfolio Project",
            "description": "Built using Fetch API",
            "tech_stack": "Django, JS, CSS",
            "project_url": "https://github.com/example/ajax-project",
            "project_image_url": "https://example.com/ajax.jpg",
        }
        response = self.client.post(reverse("main:create_project_ajax"), data=data)
        self.assertEqual(response.status_code, 201)
        response_json = response.json()
        self.assertEqual(response_json["message"], "Proyek berhasil ditambahkan.")
        self.assertTrue(Project.objects.filter(id=response_json["pk"]).exists())

    def test_create_project_ajax_forbidden_non_superuser(self):
        data = {
            "title": "Anon Project",
            "description": "Should fail",
            "tech_stack": "Python",
        }
        res_anon = self.client.post(reverse("main:create_project_ajax"), data=data)
        self.assertEqual(res_anon.status_code, 403)

        self.client.force_login(self.regular_user)
        res_user = self.client.post(reverse("main:create_project_ajax"), data=data)
        self.assertEqual(res_user.status_code, 403)

    def test_create_project_ajax_validation_error(self):
        self.client.force_login(self.superuser)
        data = {
            "title": "",
            "description": "No title",
            "tech_stack": "Django",
            "project_url": "invalid-url-format",
        }
        response = self.client.post(reverse("main:create_project_ajax"), data=data)
        self.assertEqual(response.status_code, 400)
        self.assertIn("errors", response.json())

    def test_create_project_ajax_xss_protection(self):
        self.client.force_login(self.superuser)
        data = {
            "title": "<img src=\"x\" onerror=\"alert('XSS!')\">",
            "description": "Testing XSS",
            "tech_stack": "Python",
        }
        response = self.client.post(reverse("main:create_project_ajax"), data=data)
        self.assertEqual(response.status_code, 400)
        self.assertIn("title", response.json()["errors"])

        data_clean = {
            "title": "Clean Project",
            "description": "Hello <b>world</b>",
            "tech_stack": "Django <em>&</em> Python",
        }
        response_clean = self.client.post(reverse("main:create_project_ajax"), data=data_clean)
        self.assertEqual(response_clean.status_code, 201)
        created_project = Project.objects.get(id=response_clean.json()["pk"])
        self.assertEqual(created_project.description, "Hello world")
        self.assertEqual(created_project.tech_stack, "Django & Python")

    def test_delete_project_superuser_direct_ajax_style(self):
        self.client.force_login(self.superuser)
        project = Project.objects.create(
            title="Direct Delete Project",
            description="Testing direct delete",
            tech_stack="Python",
        )
        response = self.client.post(
            reverse("main:delete_project", kwargs={"project_id": project.id})
        )
        self.assertRedirects(response, reverse("main:show_projects"))
        self.assertFalse(Project.objects.filter(id=project.id).exists())

    def test_education_page_ui_superuser_vs_regular_user(self):
        res_anon = self.client.get(reverse("main:show_education"))
        self.assertNotContains(res_anon, 'popovertarget="add-education-modal"')
        self.assertNotContains(res_anon, 'id="add-education-modal"')
        self.assertContains(res_anon, 'id="education-timeline"')

        self.client.force_login(self.regular_user)
        res_user = self.client.get(reverse("main:show_education"))
        self.assertNotContains(res_user, 'popovertarget="add-education-modal"')
        self.assertNotContains(res_user, 'id="add-education-modal"')
        self.assertContains(res_user, 'id="education-timeline"')

        self.client.force_login(self.superuser)
        res_admin = self.client.get(reverse("main:show_education"))
        self.assertContains(res_admin, 'popovertarget="add-education-modal"')
        self.assertContains(res_admin, 'id="add-education-modal"')
        self.assertContains(res_admin, 'id="education-timeline"')

    def test_experience_page_ui_superuser_vs_regular_user(self):
        res_anon = self.client.get(reverse("main:show_experience"))
        self.assertNotContains(res_anon, 'popovertarget="add-experience-modal"')
        self.assertNotContains(res_anon, 'id="add-experience-modal"')
        self.assertContains(res_anon, 'id="experience-list"')

        self.client.force_login(self.regular_user)
        res_user = self.client.get(reverse("main:show_experience"))
        self.assertNotContains(res_user, 'popovertarget="add-experience-modal"')
        self.assertNotContains(res_user, 'id="add-experience-modal"')
        self.assertContains(res_user, 'id="experience-list"')

        self.client.force_login(self.superuser)
        res_admin = self.client.get(reverse("main:show_experience"))
        self.assertContains(res_admin, 'popovertarget="add-experience-modal"')
        self.assertContains(res_admin, 'id="add-experience-modal"')
        self.assertContains(res_admin, 'id="experience-list"')

    # Assignment 4 Tests: 4-Role Authorization on Tugas 3 (Education & Experience)
    def test_unauthenticated_cannot_create_or_edit_or_delete_education(self):
        # Create
        create_url = reverse("main:create_education")
        res_create = self.client.get(create_url)
        self.assertRedirects(res_create, f"{reverse('main:login')}?next={create_url}")

        # Edit
        edit_url = reverse("main:edit_education", kwargs={"education_id": self.education.id})
        res_edit = self.client.get(edit_url)
        self.assertRedirects(res_edit, f"{reverse('main:login')}?next={edit_url}")

        # Delete
        delete_url = reverse("main:delete_education", kwargs={"education_id": self.education.id})
        res_delete = self.client.post(delete_url, data={"password": "any"})
        self.assertRedirects(res_delete, f"{reverse('main:login')}?next={delete_url}")

    def test_regular_user_cannot_create_or_edit_or_delete_education(self):
        self.client.force_login(self.regular_user)

        # Create -> 403
        res_create = self.client.get(reverse("main:create_education"))
        self.assertEqual(res_create.status_code, 403)

        # Edit -> 403
        edit_url = reverse("main:edit_education", kwargs={"education_id": self.education.id})
        res_edit = self.client.get(edit_url)
        self.assertEqual(res_edit.status_code, 403)

        # Delete -> 403
        delete_url = reverse("main:delete_education", kwargs={"education_id": self.education.id})
        res_delete = self.client.post(delete_url, data={"password": "any"})
        self.assertEqual(res_delete.status_code, 403)

    @override_settings(SECRET_CODE="test-secret-123")
    def test_editor_user_can_edit_education(self):
        self.client.force_login(self.editor_user)
        edit_url = reverse("main:edit_education", kwargs={"education_id": self.education.id})

        # GET edit form is accessible
        res_get = self.client.get(edit_url)
        self.assertEqual(res_get.status_code, 200)

        # POST edit saves successfully
        data = {
            "institution": "Editor Updated UI",
            "degree": "Sarjana (S1)",
            "field_of_study": "Sistem Informasi",
            "start_year": 2024,
            "end_year": 2028,
            "description": "Updated by editor",
            "password": "test-secret-123",
        }
        res_post = self.client.post(edit_url, data=data)
        self.assertRedirects(res_post, reverse("main:show_education"))
        self.education.refresh_from_db()
        self.assertEqual(self.education.institution, "Editor Updated UI")

    def test_editor_user_cannot_create_or_delete_education(self):
        self.client.force_login(self.editor_user)

        # Create -> 403
        res_create = self.client.get(reverse("main:create_education"))
        self.assertEqual(res_create.status_code, 403)

        # Delete -> 403
        delete_url = reverse("main:delete_education", kwargs={"education_id": self.education.id})
        res_delete = self.client.post(delete_url, data={"password": "any"})
        self.assertEqual(res_delete.status_code, 403)

    def test_editor_user_cannot_create_or_delete_experience(self):
        self.client.force_login(self.editor_user)

        # Create -> 403
        res_create = self.client.get(reverse("main:create_experience"))
        self.assertEqual(res_create.status_code, 403)

        # Delete -> 403
        delete_url = reverse("main:delete_experience", kwargs={"experience_id": self.experience.id})
        res_delete = self.client.post(delete_url, data={"password": "any"})
        self.assertEqual(res_delete.status_code, 403)

    def test_education_ui_editor_role(self):
        self.client.force_login(self.editor_user)
        res = self.client.get(reverse("main:show_education"))
        self.assertEqual(res.status_code, 200)

        # Editor CANNOT see Add Education modal or button
        self.assertNotContains(res, 'popovertarget="add-education-modal"')
        self.assertNotContains(res, 'id="add-education-modal"')
        self.assertContains(res, 'id="education-timeline"')

    # Assignment 5 Tests: AJAX, Modals, and Security for Education & Experience
    def test_create_education_ajax_superuser_success(self):
        self.client.force_login(self.superuser)
        data = {
            "institution": "Harvard University",
            "degree": "Master of Science",
            "field_of_study": "Computer Science",
            "start_year": 2024,
            "end_year": 2026,
            "description": "Graduate studies in software and systems.",
            "logo_url": "https://example.com/harvard.png",
        }
        response = self.client.post(reverse("main:create_education_ajax"), data=data)
        self.assertEqual(response.status_code, 201)
        response_json = response.json()
        self.assertEqual(response_json["message"], "Riwayat pendidikan berhasil ditambahkan.")
        self.assertTrue(Education.objects.filter(id=response_json["pk"]).exists())

    def test_create_education_ajax_forbidden_non_superuser(self):
        data = {
            "institution": "MIT",
            "degree": "Bachelor",
            "start_year": 2024,
        }
        res_anon = self.client.post(reverse("main:create_education_ajax"), data=data)
        self.assertEqual(res_anon.status_code, 403)

        self.client.force_login(self.regular_user)
        res_user = self.client.post(reverse("main:create_education_ajax"), data=data)
        self.assertEqual(res_user.status_code, 403)

        self.client.force_login(self.editor_user)
        res_editor = self.client.post(reverse("main:create_education_ajax"), data=data)
        self.assertEqual(res_editor.status_code, 403)

    def test_create_education_ajax_validation_error(self):
        self.client.force_login(self.superuser)
        data = {
            "institution": "",
            "degree": "",
            "start_year": "invalid-year",
        }
        response = self.client.post(reverse("main:create_education_ajax"), data=data)
        self.assertEqual(response.status_code, 400)
        self.assertIn("errors", response.json())

    def test_create_education_ajax_xss_protection(self):
        self.client.force_login(self.superuser)
        data = {
            "institution": "<img src=\"x\" onerror=\"alert('XSS!')\">",
            "degree": "S1",
            "start_year": 2024,
        }
        response = self.client.post(reverse("main:create_education_ajax"), data=data)
        self.assertEqual(response.status_code, 400)
        self.assertIn("institution", response.json()["errors"])

        data_clean = {
            "institution": "Universitas Indonesia",
            "degree": "Sarjana <b>S1</b>",
            "field_of_study": "Sistem Informasi <i>UI</i>",
            "description": "Fokus pada <strong>Software Engineering</strong>",
            "start_year": 2024,
        }
        response_clean = self.client.post(reverse("main:create_education_ajax"), data=data_clean)
        self.assertEqual(response_clean.status_code, 201)
        created_edu = Education.objects.get(id=response_clean.json()["pk"])
        self.assertEqual(created_edu.degree, "Sarjana S1")
        self.assertEqual(created_edu.field_of_study, "Sistem Informasi UI")
        self.assertEqual(created_edu.description, "Fokus pada Software Engineering")

    def test_create_experience_ajax_superuser_success(self):
        self.client.force_login(self.superuser)
        data = {
            "title": "Software Engineer Intern",
            "category": "internship",
            "description": "Building backend web services.",
            "started_at": "2026-06-01",
            "ended_at": "2026-08-31",
        }
        response = self.client.post(reverse("main:create_experience_ajax"), data=data)
        self.assertEqual(response.status_code, 201)
        response_json = response.json()
        self.assertEqual(response_json["message"], "Pengalaman berhasil ditambahkan.")
        self.assertTrue(Experience.objects.filter(id=response_json["pk"]).exists())

    def test_create_experience_ajax_forbidden_non_superuser(self):
        data = {
            "title": "Unauthorized Role",
            "category": "full-time",
            "description": "Should fail",
        }
        res_anon = self.client.post(reverse("main:create_experience_ajax"), data=data)
        self.assertEqual(res_anon.status_code, 403)

        self.client.force_login(self.regular_user)
        res_user = self.client.post(reverse("main:create_experience_ajax"), data=data)
        self.assertEqual(res_user.status_code, 403)

        self.client.force_login(self.editor_user)
        res_editor = self.client.post(reverse("main:create_experience_ajax"), data=data)
        self.assertEqual(res_editor.status_code, 403)

    def test_create_experience_ajax_validation_error(self):
        self.client.force_login(self.superuser)
        data = {
            "title": "",
            "category": "invalid-category",
        }
        response = self.client.post(reverse("main:create_experience_ajax"), data=data)
        self.assertEqual(response.status_code, 400)
        self.assertIn("errors", response.json())

    def test_create_experience_ajax_xss_protection(self):
        self.client.force_login(self.superuser)
        data = {
            "title": "<img src=\"x\" onerror=\"alert('XSS!')\">",
            "category": "full-time",
            "description": "Testing XSS",
        }
        response = self.client.post(reverse("main:create_experience_ajax"), data=data)
        self.assertEqual(response.status_code, 400)
        self.assertIn("title", response.json()["errors"])

        data_clean = {
            "title": "Backend <b>Developer</b>",
            "category": "part-time",
            "description": "API design with <strong>Django REST</strong>",
        }
        response_clean = self.client.post(reverse("main:create_experience_ajax"), data=data_clean)
        self.assertEqual(response_clean.status_code, 201)
        created_exp = Experience.objects.get(id=response_clean.json()["pk"])
        self.assertEqual(created_exp.title, "Backend Developer")
        self.assertEqual(created_exp.description, "API design with Django REST")




