# Generated by Django 5.1.1 on 2024-12-11 17:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('emr', '0018_remove_observation_value_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='observation',
            name='value',
            field=models.JSONField(default={}),
            preserve_default=False,
        ),
    ]
