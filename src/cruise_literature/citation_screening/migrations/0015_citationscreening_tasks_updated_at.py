# Generated by Django 4.1.5 on 2023-01-25 05:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('citation_screening', '0014_alter_citationscreening_literature_review_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='citationscreening',
            name='tasks_updated_at',
            field=models.DateTimeField(blank=True, help_text='When tasks were last redistributed.', null=True),
        ),
    ]
