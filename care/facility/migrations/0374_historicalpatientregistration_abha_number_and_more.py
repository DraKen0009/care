# Generated by Django 4.2.2 on 2023-07-20 17:45

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        # ("abdm", "0001_initial_squashed_0007_alter_abhanumber_id"),
        ("facility", "0373_remove_patientconsultation_hba1c"),
    ]

    replaces = [
        ("facility", "0329_auto_20221219_1936"),
        ("facility", "0330_auto_20221220_2312"),
        ("facility", "0366_merge_20230628_1428"),
        ("facility", "0366_merge_20230628_1428"),
        ("facility", "0373_merge_20230719_1143"),
    ]

    operations = [
        migrations.AddField(
            model_name="historicalpatientregistration",
            name="abha_number",
            field=models.IntegerField(
                blank=True,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="patientregistration",
            name="abha_number",
            field=models.IntegerField(
                blank=True,
                null=True,
            ),
        ),
    ]
