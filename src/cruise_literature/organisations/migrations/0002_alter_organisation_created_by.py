# Generated by Django 4.0.4 on 2022-10-24 16:08

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("organisations", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="organisation",
            name="created_by",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="organisation",
                to=settings.AUTH_USER_MODEL,
                verbose_name="created_by",
            ),
        ),
    ]
