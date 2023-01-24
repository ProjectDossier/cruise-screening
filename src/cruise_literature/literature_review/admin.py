from django.contrib import admin

from .models import LiteratureReview, LiteratureReviewMember

admin.site.register(LiteratureReview)
admin.site.register(LiteratureReviewMember)
