# Generated by Django 4.0.4 on 2022-05-31 19:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="allow_logging",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="user",
            name="preferred_taxonomies",
            field=models.CharField(blank=True, max_length=200),
        ),
    ]
