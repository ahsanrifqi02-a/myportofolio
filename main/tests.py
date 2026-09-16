from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from main.models import Experience, Skill


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

    def test_main_url_is_accessible(self):
        response = self.client.get(reverse("main:show_main"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")
        self.assertNotContains(response, self.experience.title)
        self.assertContains(response, f'href="{reverse("main:show_experience")}"')
        self.assertContains(response, f'href="{reverse("main:show_about")}"')
        self.assertContains(response, f'href="{reverse("main:show_skills")}"')
        self.assertContains(response, f'href="{reverse("main:show_contact")}"')


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

    # Skill Tests (Assignment 2 Checklist)
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

    def test_create_project_post_success(self):
        data = {
            "title": "Fern AI Assistant",
            "description": "Build personal AI Assistant",
            "tech_stack": "AWS, Gemini API, Python",
            "project_url": "https://github.com/kakBurhan/burhanquestv4",
            "project_image_url": "https://drive.google.com/thumbnail?id=123",
        }
        response = self.client.post(reverse("main:create_project"), data=data)
        self.assertRedirects(response, reverse("main:show_projects"))

        from main.models import Project
        self.assertTrue(Project.objects.filter(title="Fern AI Assistant").exists())

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

    def test_delete_project(self):
        from main.models import Project
        project = Project.objects.create(
            title="Temporary Project",
            description="Will be deleted",
            tech_stack="Python",
        )
        response = self.client.post(reverse("main:delete_project", kwargs={"project_id": project.id}))
        self.assertRedirects(response, reverse("main:show_projects"))
        self.assertFalse(Project.objects.filter(id=project.id).exists())


