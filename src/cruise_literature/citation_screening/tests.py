import json
from datetime import datetime
import time

from django.utils.datastructures import MultiValueDictKeyError
from django.test import TestCase, Client
from django.urls import reverse

from document_search.models import SearchEngine
from users.models import User
from .models import LiteratureReview, LiteratureReviewMember
from .process_pdf import parse_doc_grobid

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
    "decision": [],
    "automatic_decisions": [],
    "decisions": []
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

base_templates = ["_base.html", "_header.html", "_footer.html"]


class ViewTests(TestCase):
    user = None
    lit_rev = None
    fixtures = ['search_engines.json', ]

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
            # inclusion_criteria=["test inclusion criterion"],
            # exclusion_criteria=["test exclusion criterion"],
            criteria={
                "inclusion": [
                    {
                        "id": "in_1",
                        "text": "test inclusion criterion",
                        "is_active": True,
                    }
                ],
                "exclusion": [
                    {
                        "id": "ex_1",
                        "text": "test exclusion criterion",
                        "is_active": True,
                    }
                ]
            },
            papers={_fake_paper['id']: _fake_paper},
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
            "search_engines": [SearchEngine.objects.filter(
                name="CRUISE").first().id],
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

    def test_create_new_review_POST_success_test_redirect(self):
        response = self.client.post(self.create_new_review_url, self.new_review_params)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/")

    def test_create_new_review_POST_success_test_db(self):
        self.client.post(self.create_new_review_url, self.new_review_params)

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
        _test_paper_id = 'v_XFroEBnCl8skwT4wON'
        self.assertEqual(
            _papers[_test_paper_id]["title"],
            "Collateral ASIC Test",
        )
        self.assertEqual(_papers[_test_paper_id]["authors"], "Al Bailey, Tim Lada, Jim Preston")
        self.assertEqual(_papers[_test_paper_id]["url"], "http://dx.doi.org/10.1109/54.573368")
        self.assertEqual(_papers[_test_paper_id]["decision"], None)
        self.assertEqual(_papers[_test_paper_id]["search_origin"][0]["query"], "test")
        self.assertEqual(_papers[_test_paper_id]["search_origin"][0]["search_engine"], "CRUISE")

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
        criteria = test_lit_review.criteria

        self.assertEqual(criteria["inclusion"][0]['id'], "in_1")
        self.assertEqual(criteria["inclusion"][0]['text'], "test inclusion criterion")
        self.assertEqual(criteria["inclusion"][0]['is_active'], False)

        self.assertEqual(criteria["inclusion"][1]['id'], "in_2")
        self.assertEqual(criteria["inclusion"][1]['text'], "new inclusion")
        self.assertEqual(criteria["inclusion"][0]['is_active'], True)

        self.assertEqual(test_lit_review.criteria, ["new exclusion"])

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
        self.assertEqual(lit_rev["title"], "Test Literature Review 1")
        self.assertEqual(lit_rev["description"], "Test Description")
        self.assertEqual(lit_rev["search_queries"], None)
        self.assertEqual(lit_rev["criteria"], {
                "inclusion": [
                    {
                        "id": "in_1",
                        "text": "test inclusion criterion",
                        "is_active": True,
                    }
                ],
                "exclusion": [
                    {
                        "id": "ex_1",
                        "text": "test exclusion criterion",
                        "is_active": True,
                    }
                ]
            })
        # self.assertEqual(lit_rev["inclusion_criteria"], ["test inclusion criterion"])
        # self.assertEqual(lit_rev["exclusion_criteria"], ["test exclusion criterion"])
        self.assertEqual(len(lit_rev["papers"]), 1)
        self.assertEqual(lit_rev["papers"][_fake_paper['id']], _fake_paper)

    def test_export_review_GET_unauthenticated(self):
        self.client.logout()
        response = self.client.get(self.export_review_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/accounts/login/?next=/export_review/1/")

    def test_views_GET_not_member(self):
        self.client.logout()
        usr2 = User.objects.create_user(
            username="testuser2",
            email="",
        )
        usr2.set_password("testpassword")
        usr2.save()
        self.client.login(username="testuser2", password="testpassword")

        for testing_url in [
            self.screen_papers_url,
            self.export_review_url,
            self.automatic_screening_url,
            self.edit_review_url,
            self.review_details_url,
            self.add_seed_studies_url,
        ]:
            response = self.client.get(testing_url)
            self.assertEqual(response.status_code, 404)

    def test_export_review_GET_not_exist(self):
        response = self.client.get(reverse("literature_review:export_review", args=[2]))
        self.assertEqual(response.status_code, 404)

    def test_add_seed_studies_GET(self):
        response = self.client.get(self.add_seed_studies_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "literature_review/add_seed_studies.html")
        for template in base_templates:
            self.assertTemplateUsed(response, template)

    def test_add_seed_studies_GET_unauthenticated(self):
        self.client.logout()
        response = self.client.get(self.add_seed_studies_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response, "/accounts/login/?next=/literature_review/1/add_seed_studies"
        )

    def test_add_seed_studies_GET_not_exist(self):
        response = self.client.get(
            reverse("literature_review:add_seed_studies", args=[2])
        )
        self.assertEqual(response.status_code, 404)

    def test_add_seed_studies_POST(self):
        TEST_SEED_STUDY = "https://arxiv.org/pdf/2211.04623.pdf"
        new_seed_studies = {
            "seed_studies_urls": [TEST_SEED_STUDY]
        }
        response = self.client.post(self.add_seed_studies_url, new_seed_studies)
        self.assertTemplateUsed(response, "literature_review/add_seed_studies.html")
        self.assertEqual(response.status_code, 200)
        for template in base_templates:
            self.assertTemplateUsed(response, template)

        self.assertEqual(LiteratureReview.objects.count(), 1)
        test_lit_review = LiteratureReview.objects.get(title="Test Literature Review 1")
        self.assertEqual(len(test_lit_review.papers), 2)
        _grobid_doc = parse_doc_grobid(url=TEST_SEED_STUDY)
        papers = test_lit_review.papers
        self.assertEqual(papers[_fake_paper['id']], _fake_paper)
        self.assertEqual(
            papers[_grobid_doc.pdf_md5]["title"], "Neural network concatenation for Polar Codes"
        )
        self.assertEqual(papers[_grobid_doc.pdf_md5]["authors"], "Evgeny Stupachenko")
        self.assertEqual(papers[_grobid_doc.pdf_md5]["seed_study"], True)
        self.assertEqual(papers[_grobid_doc.pdf_md5]["search_engine"], "Seed Study")  # fixme
        self.assertEqual(papers[_grobid_doc.pdf_md5]["pdf"], TEST_SEED_STUDY)
        self.assertEqual(papers[_grobid_doc.pdf_md5]["decision"], None)

    def test_add_seed_studies_POST_unauthenticated(self):
        self.client.logout()
        new_seed_studies = {
            "seed_studies_urls": ["https://arxiv.org/pdf/2211.12583.pdf"]
        }
        response = self.client.post(self.add_seed_studies_url, new_seed_studies)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response, "/accounts/login/?next=/literature_review/1/add_seed_studies"
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
            reverse("literature_review:automatic_screening", args=[2])
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
        response = self.client.get(reverse("literature_review:screen_papers", args=[2]))
        self.assertEqual(response.status_code, 404)

    def test_screen_papers_POST(self):
        response = self.client.post(self.screen_papers_url, paper_screening_POST_params)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "literature_review/view_review.html")

        self.assertEqual(LiteratureReview.objects.count(), 1)
        test_lit_review = LiteratureReview.objects.get(title="Test Literature Review 1")
        _papers = test_lit_review.papers
        self.assertEqual(len(_papers), 1)
        self.assertEqual(_papers[_fake_paper['id']]["id"], _fake_paper["id"])
        self.assertEqual(_papers[_fake_paper['id']]["title"], _fake_paper["title"])
        self.assertEqual(_papers[_fake_paper['id']]["abstract"], _fake_paper["abstract"])

        _decisions = _papers[_fake_paper['id']]["decisions"]
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
        self.assertEqual(papers[_fake_paper['id']], _fake_paper)

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
        self.assertEqual(papers[_fake_paper['id']], _fake_paper)

    def test_screen_papers_POST_not_exist(self):
        # screening_params = {"screening": "1"}
        response = self.client.post(
            reverse("literature_review:screen_papers", args=[2]),
            paper_screening_POST_params,
        )
        self.assertEqual(response.status_code, 404)

        self.assertEqual(LiteratureReview.objects.count(), 1)
        test_lit_review = LiteratureReview.objects.get(title="Test Literature Review 1")
        self.assertEqual(len(test_lit_review.papers), 1)
        papers = test_lit_review.papers
        self.assertEqual(papers[_fake_paper['id']], _fake_paper)

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
        self.assertEqual(papers[_fake_paper['id']], _fake_paper)
