from django.contrib.auth.models import AbstractUser
from django.db import models


class KnowledgeGroup(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class KnowledgeArea(models.Model):
    name = models.CharField(max_length=100)
    group = models.ForeignKey(KnowledgeGroup, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Language(models.Model):
    name = models.CharField(max_length=100)
    name_native = models.CharField(max_length=100)
    iso_639_1 = models.CharField(max_length=2)

    def __str__(self):
        return self.name


class User(AbstractUser):
    first_name = models.CharField(max_length=256, blank=True)
    last_name = models.CharField(max_length=256, blank=True)

    date_of_birth = models.DateField(null=True, blank=True)
    location = models.CharField(max_length=30, blank=True)

    languages = models.ManyToManyField(Language, blank=True)
    knowledge_areas = models.ManyToManyField(KnowledgeArea, blank=True)

    allow_logging = models.BooleanField(default=False)
    preferred_taxonomies = models.CharField(max_length=200, blank=True)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def user_languages(self):
        return ", ".join(str(lang) for lang in self.languages.all())

    @property
    def user_knowledge_areas(self):
        return ", ".join(str(lang) for lang in self.knowledge_areas.all())
