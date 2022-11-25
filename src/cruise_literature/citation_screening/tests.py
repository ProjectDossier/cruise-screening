from django.test import TestCase, Client
from django.urls import reverse

from users.models import User

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

    def setUp(self):
        self.client.login(username="testuser", password="testpassword")

        self.literature_review_list_url = reverse(
            "literature_review:literature_review_home"
        )

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

    def test_review_details(self):
        review_details_url = "/literature_review/1/"
        response = self.client.get(review_details_url)
        self.assertEqual(response.status_code, 200)
