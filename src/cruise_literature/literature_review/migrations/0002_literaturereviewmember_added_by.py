# Generated by Django 4.1.5 on 2023-01-25 00:25

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('literature_review', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='literaturereviewmember',
            name='added_by',
            field=models.ForeignKey(default=1, help_text='User ID', on_delete=django.db.models.deletion.CASCADE, related_name='lrm_added_by', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]
