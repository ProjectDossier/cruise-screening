from django.contrib import admin

from .models import Organisation, OrganisationMember

admin.site.register(Organisation)
admin.site.register(OrganisationMember)
