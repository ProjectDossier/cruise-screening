# Generated by Django 4.1.5 on 2023-01-24 22:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("citation_screening", "0012_alter_literaturereview_data_format_version"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="literaturereview",
            name="discipline",
        ),
        migrations.RemoveField(
            model_name="literaturereview",
            name="members",
        ),
        migrations.RemoveField(
            model_name="literaturereview",
            name="organisation",
        ),
        migrations.RemoveField(
            model_name="literaturereviewmember",
            name="literature_review",
        ),
        migrations.RemoveField(
            model_name="literaturereviewmember",
            name="member",
        ),
    ]
