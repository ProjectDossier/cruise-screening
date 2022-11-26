import json
from datetime import datetime

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

_fake_paper = {
    "id": "1",
    "title": "Fake paper",
    "authors": "Fake author",
    "year": "2020",
    "abstract": "Fake abstract",
    "doi": "10.1234/5678",
    "url": "https://www.fake.com",
    "pdf": "https://www.fake.com/fake.pdf",
    "screened": False,
    "decision": [
        {
            "decision": "Include",
            "reason": "Fake reason",
        }
    ]
}

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
            title="Test Literature Review 1",
            description="Test Description",
            project_deadline="2020-01-01",
            inclusion_criteria=["test inclusion criterion"],
            exclusion_criteria=["test exclusion criterion"],
            papers=[_fake_paper],
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
        self.create_new_review_url = reverse("literature_review:create_new_review")
        self.edit_review_url = reverse("literature_review:edit_review", args=[1])
        self.export_review_url = reverse("literature_review:export_review", args=[1])
        self.screen_papers_url = reverse("literature_review:screen_papers", args=[1])
        self.automatic_screening_url = reverse(
            "literature_review:automatic_screening", args=[1]
        )
        self.add_seed_studies_url = reverse(
            "literature_review:add_seed_studies", args=[1]
        )

        self.new_review_params = {
            "title": "Test Literature Review 2",
            "description": "Test Description",
            "project_deadline": "2020-01-01",
            "search_queries": "test",
            "inclusion_criteria": "test",
            "exclusion_criteria": "test",
            "top_k": 10,
            "search_engines": ["CRUISE"],
            "annotations_per_paper": 1,
        }

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
        response = self.client.get(
            reverse("literature_review:review_details", args=[2])
        )
        self.assertEqual(response.status_code, 404)

    def test_create_new_review_GET(self):
        response = self.client.get(self.create_new_review_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, "literature_review/create_literature_review.html"
        )
        for template in base_templates:
            self.assertTemplateUsed(response, template)

    def test_create_new_review_GET_unauthenticated(self):
        self.client.logout()
        response = self.client.get(self.create_new_review_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/accounts/login/?next=/create_review/")

    def test_create_new_review_POST(self):
        response = self.client.post(self.create_new_review_url, self.new_review_params)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/")

        self.assertEqual(LiteratureReview.objects.count(), 2)
        self.assertEqual(LiteratureReviewMember.objects.count(), 2)
        test_lit_review = LiteratureReview.objects.get(title="Test Literature Review 2")
        test_lit_review_member = LiteratureReviewMember.objects.get(
            literature_review=test_lit_review
        )
        self.assertEqual(test_lit_review_member.member, self.user)

        self.assertEqual(test_lit_review.title, "Test Literature Review 2")
        self.assertEqual(test_lit_review.description, "Test Description")
        self.assertEqual(test_lit_review.project_deadline, datetime(2020, 1, 1).date())
        self.assertEqual(test_lit_review.search_queries, ["test"])
        self.assertEqual(test_lit_review.inclusion_criteria, ["test"])
        self.assertEqual(test_lit_review.exclusion_criteria, ["test"])
        self.assertEqual(test_lit_review.annotations_per_paper, 1)

        _papers = test_lit_review.papers
        self.assertEqual(len(_papers), 10)
        self.assertEqual(
            _papers[0]["title"],
            "Collateral ASIC Test",
        )
        self.assertEqual(_papers[0]["authors"], "Al Bailey, Tim Lada, Jim Preston")
        self.assertEqual(_papers[0]["url"], "http://dx.doi.org/10.1109/54.573368")
        self.assertEqual(_papers[0]["decision"], None)
        self.assertEqual(_papers[0]["search_origin"][0]["query"], "test")
        self.assertEqual(_papers[0]["search_origin"][0]["search_engine"], "CRUISE")

        self.assertEqual(_papers[1]["title"], "Agile Test Composition")

    def test_create_new_review_POST_unauthenticated(self):
        self.client.logout()
        response = self.client.post(self.create_new_review_url, self.new_review_params)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/accounts/login/?next=/create_review/")

        self.assertEqual(LiteratureReview.objects.count(), 1)
        self.assertEqual(LiteratureReviewMember.objects.count(), 1)

    def test_create_new_review_POST_invalid(self):
        self.new_review_params["title"] = ""
        response = self.client.post(self.create_new_review_url, self.new_review_params)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, "literature_review/create_literature_review.html"
        )

        self.assertEqual(LiteratureReview.objects.count(), 1)
        self.assertEqual(LiteratureReviewMember.objects.count(), 1)

    def test_edit_review_GET(self):
        response = self.client.get(self.edit_review_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, "literature_review/edit_literature_review.html"
        )
        for template in base_templates:
            self.assertTemplateUsed(response, template)

    def test_edit_review_GET_unauthenticated(self):
        self.client.logout()
        response = self.client.get(self.edit_review_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response, "/accounts/login/?next=/literature_review/1/edit"
        )

    def test_edit_review_GET_not_member(self):
        self.client.logout()
        usr2 = User.objects.create_user(
            username="testuser2",
            email="",
        )
        usr2.set_password("testpassword")
        usr2.save()
        self.client.login(username="testuser2", password="testpassword")
        response = self.client.get(self.edit_review_url)
        self.assertEqual(response.status_code, 404)

    def test_edit_review_GET_not_exist(self):
        response = self.client.get(reverse("literature_review:edit_review", args=[2]))
        self.assertEqual(response.status_code, 404)

    def test_edit_review_POST(self):
        new_review_params = {
            "title": "Updated Literature Review",
            "description": "Updated Description",
            "inclusion_criteria": ["new inclusion"],
            "exclusion_criteria": ["new exclusion"],
        }
        response = self.client.post(self.edit_review_url, new_review_params)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "literature_review/view_review.html")
        self.assertTemplateUsed(response, "literature_review/_review_header.html")
        for template in base_templates:
            self.assertTemplateUsed(response, template)

        self.assertEqual(LiteratureReview.objects.count(), 1)
        test_lit_review = LiteratureReview.objects.get(
            title="Updated Literature Review"
        )
        self.assertEqual(test_lit_review.title, "Updated Literature Review")
        self.assertEqual(test_lit_review.description, "Updated Description")
        self.assertEqual(test_lit_review.inclusion_criteria, ["new inclusion"])
        self.assertEqual(test_lit_review.exclusion_criteria, ["new exclusion"])

    def assertions_failed_edit_review(self):
        """Bulk assertions for
        - test_edit_review_POST_unauthenticated
        - test_edit_review_POST_not_member
        - test_edit_review_POST_not_exist
        - test_edit_review_POST_invalid
        checking if the literature review was not updated.
        """
        self.assertEqual(LiteratureReview.objects.count(), 1)
        test_lit_review = LiteratureReview.objects.get(title="Test Literature Review 1")
        self.assertEqual(test_lit_review.title, "Test Literature Review 1")
        self.assertEqual(test_lit_review.description, "Test Description")
        self.assertEqual(test_lit_review.project_deadline, datetime(2020, 1, 1).date())

    def test_edit_review_POST_unauthenticated(self):
        self.client.logout()
        new_review_params = {"title": "Updated Literature Review"}
        response = self.client.post(self.edit_review_url, new_review_params)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response, "/accounts/login/?next=/literature_review/1/edit"
        )
        self.assertions_failed_edit_review()

    def test_edit_review_POST_not_member(self):
        self.client.logout()
        usr2 = User.objects.create_user(
            username="testuser2",
            email="",
        )
        usr2.set_password("testpassword")
        usr2.save()
        self.client.login(username="testuser2", password="testpassword")
        new_review_params = {"title": "Updated Literature Review"}
        response = self.client.post(self.edit_review_url, new_review_params)
        self.assertEqual(response.status_code, 404)
        self.assertions_failed_edit_review()

    def test_edit_review_POST_not_exist(self):
        new_review_params = {"title": "Updated Literature Review"}
        response = self.client.post(
            reverse("literature_review:edit_review", args=[2]), new_review_params
        )
        self.assertEqual(response.status_code, 404)
        self.assertions_failed_edit_review()

    def test_edit_review_POST_invalid(self):
        new_review_params = {"title": ""}
        response = self.client.post(self.edit_review_url, new_review_params)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/")
        self.assertions_failed_edit_review()

    def test_export_review_GET(self):
        response = self.client.get(self.export_review_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")

        lit_rev = json.loads(response.content)
        self.assertEqual(lit_rev['title'], "Test Literature Review 1")
        self.assertEqual(lit_rev['description'], "Test Description")
        self.assertEqual(lit_rev['search_queries'], None)
        self.assertEqual(lit_rev['inclusion_criteria'], ["test inclusion criterion"])
        self.assertEqual(lit_rev['exclusion_criteria'], ["test exclusion criterion"])
        self.assertEqual(len(lit_rev['papers']), 1)
        self.assertEqual(lit_rev['papers'][0], _fake_paper)

    def test_export_review_GET_unauthenticated(self):
        self.client.logout()
        response = self.client.get(self.export_review_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response, "/accounts/login/?next=/export_review/1/"
        )

    def test_export_review_GET_not_member(self):
        self.client.logout()
        usr2 = User.objects.create_user(
            username="testuser2",
            email="",
        )
        usr2.set_password("testpassword")
        usr2.save()
        self.client.login(username="testuser2", password="testpassword")
        response = self.client.get(self.export_review_url)
        self.assertEqual(response.status_code, 404)

    def test_export_review_GET_not_exist(self):
        response = self.client.get(reverse("literature_review:export_review", args=[2]))
        self.assertEqual(response.status_code, 404)

