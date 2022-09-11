from .models import LiteratureReview, LiteratureReviewMember, CitationScreening
#
#
# class LiteratureReviewDBRouter:
#     def db_for_read(self, model, **hints):
#         if model in [LiteratureReview, LiteratureReviewMember, CitationScreening]:
#             # your model name as in settings.py/DATABASES
#             return "literature_review"
#         return None
#
#     def db_for_write(self, model, **hints):
#         if model in [LiteratureReview, LiteratureReviewMember, CitationScreening]:
#             # your model name as in settings.py/DATABASES
#             return "literature_review"
#         return None
#
#     def allow_relation(self, obj1, obj2, **hints):
#         """
#         Relations between objects are allowed if both objects are
#         in the primary/replica pool.
#         """
#         db_set = {'literature_review', 'default'}
#         if obj1._state.db in db_set and obj2._state.db in db_set:
#             return True
#         return None
