from django.test import TestCase, Client
from django.urls import reverse

from users.models import User
from .models import LiteratureReview, LiteratureReviewMember

from .views import (
    create_new_review,
    edit_review,
    export_review,
    literature_review_home,
    review_details,
    screen_papers,
    automatic_screening,
    add_seed_studies,
)

base_templates = ["_base.html", "_header.html", "_footer.html"]


class ViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super(ViewTests, cls).setUpClass()
        cls.view_functions = [
            create_new_review,
            edit_review,
            export_review,
            literature_review_home,
            review_details,
            screen_papers,
            automatic_screening,
            add_seed_studies,
        ]
        cls.user = User.objects.create_user(
            username="testuser",
            email="",
        )
        cls.user.set_password("testpassword")
        cls.user.save()

        cls.lit_rev = LiteratureReview.objects.create(
            title="Test Literature Review",
            description="Test Description",
            project_deadline="2020-01-01",
        )
        cls.member = LiteratureReviewMember.objects.create(
            member=cls.user, literature_review=cls.lit_rev
        )

    def setUp(self):
        self.client = Client()
        self.client.login(username="testuser", password="testpassword")

        self.literature_review_list_url = reverse(
            "literature_review:literature_review_home"
        )
        self.review_details_url = reverse("literature_review:review_details", args=[1])

    def test_literature_review_list_GET(self):
        response = self.client.get(self.literature_review_list_url)
        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, "literature_review/home.html")
        for template in base_templates:
            self.assertTemplateUsed(response, template)

    def test_literature_review_list_GET_unauthenticated(self):
        self.client.logout()
        response = self.client.get(self.literature_review_list_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/accounts/login/?next=/literature_review/")

    def test_review_details_GET(self):
        response = self.client.get(self.review_details_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "literature_review/view_review.html")
        self.assertTemplateUsed(response, "literature_review/_review_header.html")
        for template in base_templates:
            self.assertTemplateUsed(response, template)

    def test_review_details_GET_unauthenticated(self):
        self.client.logout()
        response = self.client.get(self.review_details_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/accounts/login/?next=/literature_review/1/")

    def test_review_details_GET_not_member(self):
        self.client.logout()
        usr2 = User.objects.create_user(
            username="testuser2",
            email="",
        )
        usr2.set_password("testpassword")
        usr2.save()
        self.client.login(username="testuser2", password="testpassword")
        response = self.client.get(self.review_details_url)
        self.assertEqual(response.status_code, 404)

    def test_review_details_GET_not_exist(self):
        response = self.client.get(reverse("literature_review:review_details", args=[2]))
        self.assertEqual(response.status_code, 404)

    def test_create_new_review_GET(self):
        response = self.client.get(reverse("literature_review:create_new_review"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "literature_review/create_literature_review.html")
        for template in base_templates:
            self.assertTemplateUsed(response, template)

    def test_create_new_review_GET_unauthenticated(self):
        self.client.logout()
        response = self.client.get(reverse("literature_review:create_new_review"))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/accounts/login/?next=/create_review/")

    def test_create_new_review_POST(self):
        response = self.client.post(reverse("literature_review:create_new_review"), {
            "title": "Test Literature Review",
            "description": "Test Description",
            "project_deadline": "2020-01-01",
            "search_queries": "test",
            "inclusion_criteria": "test",
            "exclusion_criteria": "test",
            "top_k": 10,
            "search_engines": ["SemanticScholar"],
            "annotations_per_paper": 1,
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/")

