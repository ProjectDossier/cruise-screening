from django.contrib import admin

from .models import User, Language, KnowledgeArea, KnowledgeGroup

admin.site.register(User)
admin.site.register(Language)
admin.site.register(KnowledgeArea)
admin.site.register(KnowledgeGroup)
