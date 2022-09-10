from .models import LiteratureReview, LiteratureReviewMember, CitationScreening


class LiteratureReviewDBRouter:
    def db_for_read(self, model, **hints):
        if model in [LiteratureReview, LiteratureReviewMember, CitationScreening]:
            # your model name as in settings.py/DATABASES
            return "literature_review"
        return None

    def db_for_write(self, model, **hints):
        if model in [LiteratureReview, LiteratureReviewMember, CitationScreening]:
            # your model name as in settings.py/DATABASES
            return "literature_review"
        return None
