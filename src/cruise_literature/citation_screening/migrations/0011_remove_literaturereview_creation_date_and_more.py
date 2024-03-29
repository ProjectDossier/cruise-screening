# Generated by Django 4.0.4 on 2022-11-26 17:12

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("citation_screening", "0010_literaturereview_organisation"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="literaturereview",
            name="creation_date",
        ),
        migrations.RemoveField(
            model_name="literaturereview",
            name="last_edit_date",
        ),
        migrations.AddField(
            model_name="literaturereview",
            name="criteria",
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="literaturereview",
            name="data_format_version",
            field=models.IntegerField(
                default=2,
                help_text="Version of the data format. This is used to migrate data between versions.",
            ),
        ),
        migrations.AddField(
            model_name="literaturereview",
            name="min_decisions",
            field=models.IntegerField(
                default=1,
                help_text="How many reviewers need to screen every paper. Default is 1.",
                validators=[
                    django.core.validators.MinValueValidator(1),
                    django.core.validators.MaxValueValidator(3),
                ],
                verbose_name="minimum decisions per paper",
            ),
        ),
        migrations.CreateModel(
            name="CitationScreening",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "screening_level",
                    models.IntegerField(
                        choices=[
                            (1, "Title and abstract screening"),
                            (2, "Full-text screening"),
                        ],
                        default=1,
                        help_text="Screening level: 1 or 2",
                        validators=[
                            django.core.validators.MinValueValidator(1),
                            django.core.validators.MaxValueValidator(2),
                        ],
                    ),
                ),
                ("tasks", models.JSONField(null=True)),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="created at"),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="updated at"),
                ),
                (
                    "literature_review",
                    models.ForeignKey(
                        help_text="Literature Review ID",
                        on_delete=django.db.models.deletion.CASCADE,
                        to="citation_screening.literaturereview",
                    ),
                ),
            ],
        ),
    ]
