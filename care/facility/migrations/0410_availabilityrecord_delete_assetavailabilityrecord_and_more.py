# Generated by Django 4.2.8 on 2024-01-21 14:03

import uuid

import django.db.models.deletion
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.db import migrations, models

from care.facility.models.asset import Asset


def forwards_func(apps, schema_editor):
    AssetAvailabilityRecord = apps.get_model("facility", "AssetAvailabilityRecord")
    AvailabilityRecord = apps.get_model("facility", "AvailabilityRecord")
    ContentType = apps.get_model("contenttypes", "ContentType")

    asset_content_type = ContentType.objects.get_for_model(Asset)

    aar_records = AssetAvailabilityRecord.objects.all().order_by("pk")

    paginator = Paginator(aar_records, 1000)
    for page_number in paginator.page_range:
        availability_records = []
        for aar in paginator.page(page_number).object_list:
            availability_record = AvailabilityRecord(
                content_type=asset_content_type,
                object_external_id=aar.asset.external_id,
                status=aar.status,
                timestamp=aar.timestamp,
            )
            availability_records.append(availability_record)

        AvailabilityRecord.objects.bulk_create(availability_records)


def backwards_func(apps, schema_editor):
    AssetAvailabilityRecord = apps.get_model("facility", "AssetAvailabilityRecord")
    AvailabilityRecord = apps.get_model("facility", "AvailabilityRecord")
    ContentType = apps.get_model("contenttypes", "ContentType")

    asset_content_type = ContentType.objects.get_for_model(Asset)

    ar_records = AvailabilityRecord.objects.filter(
        content_type=asset_content_type
    ).order_by("pk")

    paginator = Paginator(ar_records, 1000)
    for page_number in paginator.page_range:
        asset_availability_records = []
        for ar in paginator.page(page_number).object_list:
            try:
                AssetObject = Asset.objects.get(external_id=ar.object_external_id)
                asset_availability_record = AssetAvailabilityRecord(
                    asset_id=AssetObject.id,
                    status=ar.status,
                    timestamp=ar.timestamp,
                )
                asset_availability_records.append(asset_availability_record)
            except ObjectDoesNotExist:
                continue  # Skip if the asset was deleted

        AssetAvailabilityRecord.objects.bulk_create(asset_availability_records)
        AvailabilityRecord.objects.filter(
            id__in=[ar.id for ar in paginator.page(page_number).object_list]
        ).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
        ("facility", "0409_merge_20240210_1510"),
    ]

    operations = [
        migrations.CreateModel(
            name="AvailabilityRecord",
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
                    "external_id",
                    models.UUIDField(db_index=True, default=uuid.uuid4, unique=True),
                ),
                (
                    "created_date",
                    models.DateTimeField(auto_now_add=True, db_index=True, null=True),
                ),
                (
                    "modified_date",
                    models.DateTimeField(auto_now=True, db_index=True, null=True),
                ),
                ("deleted", models.BooleanField(db_index=True, default=False)),
                ("object_external_id", models.UUIDField()),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("Not Monitored", "Not Monitored"),
                            ("Operational", "Operational"),
                            ("Down", "Down"),
                            ("Under Maintenance", "Under Maintenance"),
                        ],
                        default="Not Monitored",
                        max_length=20,
                    ),
                ),
                ("timestamp", models.DateTimeField()),
                (
                    "content_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="contenttypes.contenttype",
                    ),
                ),
            ],
            options={
                "ordering": ["-timestamp"],
            },
        ),
        migrations.AddIndex(
            model_name="availabilityrecord",
            index=models.Index(
                fields=["content_type", "object_external_id"],
                name="facility_av_content_ad9eff_idx",
            ),
        ),
        migrations.RunPython(forwards_func, backwards_func),
        migrations.DeleteModel(
            name="AssetAvailabilityRecord",
        ),
    ]
