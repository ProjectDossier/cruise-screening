# Generated by Django 4.0.4 on 2022-11-28 16:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('document_search', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='searchengine',
            name='is_available',
        ),
        migrations.AddField(
            model_name='searchengine',
            name='is_available_for_review',
            field=models.BooleanField(default=True, verbose_name='Available for literature review'),
        ),
        migrations.AddField(
            model_name='searchengine',
            name='is_available_for_search',
            field=models.BooleanField(default=True, verbose_name='Is available for search'),
        ),
    ]
