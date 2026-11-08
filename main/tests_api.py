import uuid

from django.contrib.auth.models import Group, User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from main.models import Education, Experience, Project


class ProjectAPITest(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_superuser(
            username="owner", password="test-password", email="owner@example.com",
        )
        self.visitor = User.objects.create_user(username="visitor", password="test-password")
        self.project = Project.objects.create(
            title="Portfolio", description="My website", tech_stack="Django",
        )
        self.list_url = reverse("api:project-list")
        self.detail_url = reverse("api:project-detail", args=[self.project.id])
        self.star_url = reverse("api:project-star", args=[self.project.id])
        self.payload = {
            "title": "New project", "description": "A useful app", "tech_stack": "Python",
            "project_url": "https://example.com/", "project_image_url": "",
        }

    def test_public_list_and_detail(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["id"], str(self.project.id))
        self.assertFalse(response.data[0]["is_starred"])
        self.assertNotIn("fields", response.data[0])
        self.assertEqual(self.client.get(self.detail_url).status_code, status.HTTP_200_OK)

    def test_search_and_empty_results(self):
        response = self.client.get(self.list_url, {"title": "PORT"})
        self.assertEqual(len(response.data), 1)
        response = self.client.get(self.list_url, {"title": "not-found"})
        self.assertEqual(response.data, [])

    def test_missing_project(self):
        url = reverse("api:project-detail", args=[uuid.uuid4()])
        self.assertEqual(self.client.get(url).status_code, status.HTTP_404_NOT_FOUND)

    def test_guest_and_visitor_cannot_write(self):
        for user in (None, self.visitor):
            self.client.force_authenticate(user=user)
            self.assertEqual(self.client.post(self.list_url, self.payload, format="json").status_code, 403)
            self.assertEqual(self.client.patch(self.detail_url, {"title": "Changed"}, format="json").status_code, 403)
            self.assertEqual(self.client.delete(self.detail_url).status_code, 403)
        self.assertEqual(Project.objects.count(), 1)
        self.project.refresh_from_db()
        self.assertEqual(self.project.title, "Portfolio")

    def test_owner_can_create(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.list_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Project.objects.filter(pk=response.data["id"]).exists())

    def test_validation(self):
        self.client.force_authenticate(user=self.owner)
        for changes, field in [
            ({"title": "   "}, "title"),
            ({"title": '<img src="x" onerror="alert(1)">'}, "title"),
            ({"project_url": "javascript:alert(1)"}, "project_url"),
        ]:
            response = self.client.post(self.list_url, {**self.payload, **changes}, format="json")
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn(field, response.data)
        self.assertEqual(Project.objects.count(), 1)

    def test_patch_put_and_delete(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.patch(self.detail_url, {"title": "Changed"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.project.refresh_from_db()
        self.assertEqual(self.project.description, "My website")
        response = self.client.put(self.detail_url, {"title": "Incomplete"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response = self.client.put(self.detail_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.content, b"")
        self.assertFalse(Project.objects.filter(pk=self.project.id).exists())

    def test_star_requires_login_and_toggles(self):
        self.assertEqual(self.client.post(self.star_url).status_code, status.HTTP_403_FORBIDDEN)
        self.client.force_authenticate(user=self.visitor)
        response = self.client.post(self.star_url)
        self.assertTrue(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 1)
        response = self.client.post(self.star_url)
        self.assertFalse(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 0)

    def test_computed_fields_are_read_only(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.list_url, {
            **self.payload, "star_count": 99, "is_starred": True,
            "starred_by_names": "forged", "starred_by": [self.visitor.id],
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["star_count"], 0)
        self.assertFalse(response.data["is_starred"])

    def test_staff_and_editor_cannot_manage_tutorial_projects(self):
        self.visitor.is_staff = True
        self.visitor.save()
        self.visitor.groups.add(Group.objects.create(name="Editor"))
        self.client.force_authenticate(user=self.visitor)
        response = self.client.patch(self.detail_url, {"title": "Changed"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_wrong_method(self):
        self.client.force_authenticate(user=self.owner)
        self.assertEqual(self.client.delete(self.list_url).status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_session_write_without_csrf_is_rejected(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(username="owner", password="test-password"))
        response = client.post(self.list_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Project.objects.count(), 1)

    def test_session_write_with_csrf_succeeds(self):
        client = APIClient(enforce_csrf_checks=True)
        client.login(username="owner", password="test-password")
        page = client.get(self.list_url, HTTP_ACCEPT="text/html")
        self.assertEqual(page.status_code, status.HTTP_200_OK)
        token = client.cookies["csrftoken"].value
        response = client.post(
            self.list_url, self.payload, format="json", HTTP_X_CSRFTOKEN=token,
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class EducationAPITest(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_superuser(
            username="edu_owner", password="test-password", email="edu_owner@example.com",
        )
        self.visitor = User.objects.create_user(
            username="edu_visitor", password="test-password", email="visitor_secret@example.com",
        )
        self.editor_group = Group.objects.create(name="Editor")
        self.editor = User.objects.create_user(
            username="edu_editor", password="test-password", email="editor_secret@example.com",
        )
        self.editor.groups.add(self.editor_group)

        self.education = Education.objects.create(
            institution="Universitas Indonesia",
            degree="Sarjana (S1)",
            field_of_study="Sistem Informasi",
            start_year=2024,
            end_year=2028,
            description="Fokus pada rekayasa perangkat lunak.",
            logo_url="https://example.com/ui.png",
        )
        self.list_url = reverse("api:education-list")
        self.detail_url = reverse("api:education-detail", args=[self.education.id])
        self.star_url = reverse("api:education-star", args=[self.education.id])
        self.payload = {
            "institution": "Stanford University",
            "degree": "Master of Science",
            "field_of_study": "Computer Science",
            "start_year": 2028,
            "end_year": 2030,
            "description": "Distributed systems and AI.",
            "logo_url": "https://example.com/stanford.png",
        }

    def test_public_list_and_detail(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], str(self.education.id))
        self.assertEqual(response.data[0]["institution"], "Universitas Indonesia")
        self.assertFalse(response.data[0]["is_starred"])
        self.assertEqual(response.data[0]["star_count"], 0)
        self.assertNotIn("fields", response.data[0])

        detail_response = self.client.get(self.detail_url)
        self.assertEqual(detail_response.status_code, status.HTTP_200_OK)
        self.assertEqual(detail_response.data["degree"], "Sarjana (S1)")

    def test_search_query_parameter_and_empty_results(self):
        response = self.client.get(self.list_url, {"institution": "indonesia"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        response_degree = self.client.get(self.list_url, {"institution": "Sarjana"})
        self.assertEqual(len(response_degree.data), 1)

        response_empty = self.client.get(self.list_url, {"institution": "nonexistent-school"})
        self.assertEqual(response_empty.status_code, status.HTTP_200_OK)
        self.assertEqual(response_empty.data, [])

    def test_missing_education_returns_404(self):
        missing_id = uuid.uuid4()
        detail_url = reverse("api:education-detail", args=[missing_id])
        star_url = reverse("api:education-star", args=[missing_id])
        self.assertEqual(self.client.get(detail_url).status_code, status.HTTP_404_NOT_FOUND)
        self.client.force_authenticate(user=self.visitor)
        self.assertEqual(self.client.post(star_url).status_code, status.HTTP_404_NOT_FOUND)

    def test_guest_and_regular_user_cannot_write_and_db_unchanged(self):
        for user in (None, self.visitor):
            self.client.force_authenticate(user=user)
            self.assertEqual(
                self.client.post(self.list_url, self.payload, format="json").status_code,
                status.HTTP_403_FORBIDDEN,
            )
            self.assertEqual(
                self.client.put(self.detail_url, self.payload, format="json").status_code,
                status.HTTP_403_FORBIDDEN,
            )
            self.assertEqual(
                self.client.patch(
                    self.detail_url, {"institution": "Tampered"}, format="json"
                ).status_code,
                status.HTTP_403_FORBIDDEN,
            )
            self.assertEqual(
                self.client.delete(self.detail_url).status_code,
                status.HTTP_403_FORBIDDEN,
            )

        self.assertEqual(Education.objects.count(), 1)
        self.education.refresh_from_db()
        self.assertEqual(self.education.institution, "Universitas Indonesia")

    def test_editor_can_patch_and_put_but_cannot_create_or_delete(self):
        self.client.force_authenticate(user=self.editor)

        # Editor CANNOT create (POST -> 403) and DB count remains 1
        post_response = self.client.post(self.list_url, self.payload, format="json")
        self.assertEqual(post_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Education.objects.count(), 1)

        # Editor CAN partial update (PATCH -> 200) and DB is updated
        patch_response = self.client.patch(
            self.detail_url,
            {"institution": "Universitas Indonesia (Updated by Editor)"},
            format="json",
        )
        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)
        self.education.refresh_from_db()
        self.assertEqual(self.education.institution, "Universitas Indonesia (Updated by Editor)")
        self.assertEqual(self.education.degree, "Sarjana (S1)")

        # Editor CAN full update (PUT -> 200)
        put_response = self.client.put(self.detail_url, self.payload, format="json")
        self.assertEqual(put_response.status_code, status.HTTP_200_OK)
        self.education.refresh_from_db()
        self.assertEqual(self.education.institution, "Stanford University")

        # Editor CANNOT delete (DELETE -> 403) and DB record still exists
        delete_response = self.client.delete(self.detail_url)
        self.assertEqual(delete_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Education.objects.filter(pk=self.education.id).exists())

    def test_owner_can_create_update_and_delete(self):
        self.client.force_authenticate(user=self.owner)

        # Create (POST -> 201)
        create_response = self.client.post(self.list_url, self.payload, format="json")
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Education.objects.count(), 2)
        created_id = create_response.data["id"]
        self.assertTrue(Education.objects.filter(pk=created_id).exists())

        # Partial Update (PATCH -> 200)
        patch_response = self.client.patch(
            self.detail_url, {"degree": "Sarjana Komputer"}, format="json"
        )
        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)
        self.education.refresh_from_db()
        self.assertEqual(self.education.degree, "Sarjana Komputer")

        # Delete (DELETE -> 204)
        delete_response = self.client.delete(self.detail_url)
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(delete_response.content, b"")
        self.assertFalse(Education.objects.filter(pk=self.education.id).exists())

    def test_validation_and_strip_tags(self):
        self.client.force_authenticate(user=self.owner)
        for changes, field in [
            ({"institution": "   "}, "institution"),
            ({"institution": '<script>alert("xss")</script>'}, "institution"),
            ({"degree": '<img src="x" onerror="alert(1)">'}, "degree"),
            ({"logo_url": "javascript:alert(1)"}, "logo_url"),
            ({"start_year": 2028, "end_year": 2024}, "end_year"),
        ]:
            response = self.client.post(
                self.list_url, {**self.payload, **changes}, format="json"
            )
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn(field, response.data)
        self.assertEqual(Education.objects.count(), 1)

        # Verify HTML tags are stripped on valid text inputs
        clean_response = self.client.post(
            self.list_url,
            {
                **self.payload,
                "institution": "<b>MIT</b>",
                "degree": "<i>PhD</i>",
                "field_of_study": "<span>AI</span>",
                "description": "<p>Research</p>",
            },
            format="json",
        )
        self.assertEqual(clean_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(clean_response.data["institution"], "MIT")
        self.assertEqual(clean_response.data["degree"], "PhD")
        self.assertEqual(clean_response.data["field_of_study"], "AI")
        self.assertEqual(clean_response.data["description"], "Research")

    def test_star_endpoint_and_no_sensitive_user_data_exposed(self):
        # Guest is rejected from starring
        guest_response = self.client.post(self.star_url)
        self.assertEqual(guest_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.education.starred_by.count(), 0)

        # Authenticated regular user can star and unstar
        self.client.force_authenticate(user=self.visitor)
        star_response = self.client.post(self.star_url)
        self.assertEqual(star_response.status_code, status.HTTP_200_OK)
        self.assertTrue(star_response.data["is_starred"])
        self.assertEqual(star_response.data["star_count"], 1)
        self.assertIn("edu_visitor", star_response.data["starred_by_names"])

        # Ensure sensitive account data (email, password hash) is never exposed
        serialized_text = str(star_response.data)
        self.assertNotIn("visitor_secret@example.com", serialized_text)
        self.assertNotIn("pbkdf2_", serialized_text)
        self.assertNotIn("password", star_response.data)

        # Toggle off
        unstar_response = self.client.post(self.star_url)
        self.assertEqual(unstar_response.status_code, status.HTTP_200_OK)
        self.assertFalse(unstar_response.data["is_starred"])
        self.assertEqual(unstar_response.data["star_count"], 0)

    def test_computed_star_fields_are_read_only(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(
            self.list_url,
            {
                **self.payload,
                "star_count": 500,
                "is_starred": True,
                "starred_by_names": "spoofed_user",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["star_count"], 0)
        self.assertFalse(response.data["is_starred"])
        self.assertEqual(response.data["starred_by_names"], "")

    def test_session_write_without_csrf_is_rejected(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(username="edu_owner", password="test-password"))
        response = client.post(self.list_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Education.objects.count(), 1)

    def test_session_write_with_csrf_succeeds(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(username="edu_editor", password="test-password"))
        page = client.get(self.list_url, HTTP_ACCEPT="text/html")
        self.assertEqual(page.status_code, status.HTTP_200_OK)
        token = client.cookies["csrftoken"].value
        response = client.patch(
            self.detail_url,
            {"institution": "CSRF Verified University"},
            format="json",
            HTTP_X_CSRFTOKEN=token,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.education.refresh_from_db()
        self.assertEqual(self.education.institution, "CSRF Verified University")


class ExperienceAPITest(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_superuser(
            username="exp_owner", password="test-password", email="exp_owner@example.com",
        )
        self.visitor = User.objects.create_user(
            username="exp_visitor", password="test-password",
        )
        self.editor_group = Group.objects.create(name="Editor")
        self.editor = User.objects.create_user(
            username="exp_editor", password="test-password",
        )
        self.editor.groups.add(self.editor_group)

        self.experience = Experience.objects.create(
            title="Teaching Assistant PBP",
            category="part-time",
            description="Guiding students in web development labs.",
            started_at="2026-07-01",
        )
        self.list_url = reverse("api:experience-list")
        self.detail_url = reverse("api:experience-detail", args=[self.experience.id])
        self.star_url = reverse("api:experience-star", args=[self.experience.id])
        self.payload = {
            "title": "Software Engineering Intern",
            "category": "internship",
            "description": "Developing REST APIs with Django REST Framework.",
            "started_at": "2026-06-01",
            "ended_at": "2026-08-31",
        }

    def test_roles_and_crud_on_experience_api(self):
        # Guest & visitor rejected on write
        for user in (None, self.visitor):
            self.client.force_authenticate(user=user)
            self.assertEqual(
                self.client.post(self.list_url, self.payload, format="json").status_code,
                status.HTTP_403_FORBIDDEN,
            )
            self.assertEqual(
                self.client.patch(self.detail_url, {"title": "No"}, format="json").status_code,
                status.HTTP_403_FORBIDDEN,
            )
            self.assertEqual(
                self.client.delete(self.detail_url).status_code,
                status.HTTP_403_FORBIDDEN,
            )
        self.assertEqual(Experience.objects.count(), 1)

        # Editor can PATCH, cannot POST or DELETE
        self.client.force_authenticate(user=self.editor)
        self.assertEqual(
            self.client.post(self.list_url, self.payload, format="json").status_code,
            status.HTTP_403_FORBIDDEN,
        )
        patch_res = self.client.patch(
            self.detail_url, {"title": "Lead TA PBP"}, format="json"
        )
        self.assertEqual(patch_res.status_code, status.HTTP_200_OK)
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, "Lead TA PBP")
        self.assertEqual(
            self.client.delete(self.detail_url).status_code,
            status.HTTP_403_FORBIDDEN,
        )

        # Owner can POST and DELETE
        self.client.force_authenticate(user=self.owner)
        create_res = self.client.post(self.list_url, self.payload, format="json")
        self.assertEqual(create_res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Experience.objects.count(), 2)
        del_res = self.client.delete(self.detail_url)
        self.assertEqual(del_res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Experience.objects.filter(pk=self.experience.id).exists())

    def test_experience_star_and_csrf(self):
        self.assertEqual(
            self.client.post(self.star_url).status_code, status.HTTP_403_FORBIDDEN
        )
        self.client.force_authenticate(user=self.visitor)
        res = self.client.post(self.star_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.data["is_starred"])
        self.assertEqual(res.data["star_count"], 1)

        csrf_client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(csrf_client.login(username="exp_owner", password="test-password"))
        self.assertEqual(
            csrf_client.post(self.list_url, self.payload, format="json").status_code,
            status.HTTP_403_FORBIDDEN,
        )
