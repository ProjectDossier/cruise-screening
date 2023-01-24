import time

from django.test import TestCase, Client
from django.urls import reverse
from django.utils.datastructures import MultiValueDictKeyError

from literature_review.models import LiteratureReview, LiteratureReviewMember
from users.models import User
from .views import (
    screen_papers,
    automatic_screening,
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
    "decision": [],
    "automatic_decisions": [],
    "decisions": [],
}

paper_screening_POST_params = {
    "paper_id": "1",
    "start_time": time.time(),
    "topic_relevance": "1",
    "domain_relevance": "1",
    "decision": "1",
    "reason": "Fake reason",
    "paper_prior_knowledge": "1",
    "authors_prior_knowledge": "2",
}

base_templates = [
    "_base_templates/_base.html",
    "_base_templates/_header.html",
    "_base_templates/_footer.html",
]


class ViewTests(TestCase):
    user = None
    lit_rev = None
    fixtures = [
        "search_engines.json",
    ]

    @classmethod
    def setUpClass(cls):
        super(ViewTests, cls).setUpClass()
        cls.view_functions = [
            screen_papers,
            automatic_screening,
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
            criteria={
                "inclusion": [
                    {
                        "id": "in_0",
                        "text": "test inclusion criterion",
                        "is_active": True,
                    }
                ],
                "exclusion": [
                    {
                        "id": "ex_0",
                        "text": "test exclusion criterion",
                        "is_active": True,
                    }
                ],
            },
            papers={_fake_paper["id"]: _fake_paper},
        )
        cls.member = LiteratureReviewMember.objects.create(
            member=cls.user, literature_review=cls.lit_rev
        )

    def setUp(self):
        self.client = Client()
        self.client.login(username="testuser", password="testpassword")

        self.screen_papers_url = reverse("citation_screening:screen_papers", args=[1])
        self.automatic_screening_url = reverse(
            "citation_screening:automatic_screening", args=[1]
        )

    def test_automatic_screening_GET(self):
        self.assertRaises(ValueError, self.client.get, self.automatic_screening_url)

    def test_automatic_screening_GET_unauthenticated(self):
        self.client.logout()
        response = self.client.get(self.automatic_screening_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response, "/accounts/login/?next=/literature_review/1/automatic_screening"
        )

    def test_automatic_screening_GET_not_exist(self):
        response = self.client.get(
            reverse("citation_screening:automatic_screening", args=[2])
        )
        self.assertEqual(response.status_code, 404)

    def test_screen_papers_GET(self):
        response = self.client.get(self.screen_papers_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "literature_review/screen_paper.html")
        for template in base_templates:
            self.assertTemplateUsed(response, template)

    def test_screen_papers_GET_unauthenticated(self):
        self.client.logout()
        response = self.client.get(self.screen_papers_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/accounts/login/?next=/screen_papers/1/")

    def test_screen_papers_GET_not_exist(self):
        response = self.client.get(
            reverse("citation_screening:screen_papers", args=[2])
        )
        self.assertEqual(response.status_code, 404)

    def test_screen_papers_POST(self):
        response = self.client.post(self.screen_papers_url, paper_screening_POST_params)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "literature_review/view_review.html")

        self.assertEqual(LiteratureReview.objects.count(), 1)
        test_lit_review = LiteratureReview.objects.get(title="Test Literature Review 1")
        _papers = test_lit_review.papers
        self.assertEqual(len(_papers), 1)
        self.assertEqual(_papers[_fake_paper["id"]]["id"], _fake_paper["id"])
        self.assertEqual(_papers[_fake_paper["id"]]["title"], _fake_paper["title"])
        self.assertEqual(
            _papers[_fake_paper["id"]]["abstract"], _fake_paper["abstract"]
        )

        _decisions = _papers[_fake_paper["id"]]["decisions"]
        self.assertEqual(_decisions[0]["domain_relevance"], 1)
        self.assertEqual(_decisions[0]["topic_relevance"], 1)
        self.assertEqual(_decisions[0]["decision"], 1)
        self.assertEqual(_decisions[0]["reason"], "Fake reason")
        self.assertEqual(_decisions[0]["paper_prior_knowledge"], 1)
        self.assertEqual(_decisions[0]["authors_prior_knowledge"], 2)

    def test_screen_papers_POST_unauthenticated(self):
        self.client.logout()
        response = self.client.post(self.screen_papers_url, paper_screening_POST_params)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/accounts/login/?next=/screen_papers/1/")
        self.assertEqual(LiteratureReview.objects.count(), 1)
        test_lit_review = LiteratureReview.objects.get(title="Test Literature Review 1")
        self.assertEqual(len(test_lit_review.papers), 1)
        papers = test_lit_review.papers
        self.assertEqual(papers[_fake_paper["id"]], _fake_paper)

    def test_screen_papers_POST_not_member(self):
        self.client.logout()
        usr2 = User.objects.create_user(
            username="testuser2",
            email="",
        )
        usr2.set_password("testpassword")
        usr2.save()
        self.client.login(username="testuser2", password="testpassword")
        response = self.client.post(self.screen_papers_url, paper_screening_POST_params)
        self.assertEqual(response.status_code, 404)

        self.assertEqual(LiteratureReview.objects.count(), 1)
        test_lit_review = LiteratureReview.objects.get(title="Test Literature Review 1")
        self.assertEqual(len(test_lit_review.papers), 1)
        papers = test_lit_review.papers
        self.assertEqual(papers[_fake_paper["id"]], _fake_paper)

    def test_screen_papers_POST_not_exist(self):
        # screening_params = {"screening": "1"}
        response = self.client.post(
            reverse("citation_screening:screen_papers", args=[2]),
            paper_screening_POST_params,
        )
        self.assertEqual(response.status_code, 404)

        self.assertEqual(LiteratureReview.objects.count(), 1)
        test_lit_review = LiteratureReview.objects.get(title="Test Literature Review 1")
        self.assertEqual(len(test_lit_review.papers), 1)
        papers = test_lit_review.papers
        self.assertEqual(papers[_fake_paper["id"]], _fake_paper)

    def test_screen_papers_POST_invalid(self):
        screening_params = {"bad_key": "1"}  # and missing keys
        self.assertRaises(
            MultiValueDictKeyError,
            self.client.post,
            self.screen_papers_url,
            screening_params,
        )

        self.assertEqual(LiteratureReview.objects.count(), 1)
        test_lit_review = LiteratureReview.objects.get(title="Test Literature Review 1")
        self.assertEqual(len(test_lit_review.papers), 1)
        papers = test_lit_review.papers
        self.assertEqual(papers[_fake_paper["id"]], _fake_paper)
