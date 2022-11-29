# Generated by Django 4.0.4 on 2022-11-28 17:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("citation_screening", "0011_remove_literaturereview_creation_date_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="literaturereview",
            name="data_format_version",
            field=models.IntegerField(
                default=3,
                help_text="Version of the data format. This is used to migrate data between versions.",
            ),
        ),
    ]
