from django.contrib import admin

from .models import CitationScreening, LiteratureReview, LiteratureReviewMember

admin.site.register(CitationScreening)
admin.site.register(LiteratureReview)
admin.site.register(LiteratureReviewMember)
