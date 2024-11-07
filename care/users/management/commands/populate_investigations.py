import json
from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import transaction

from care.facility.models import PatientInvestigation, PatientInvestigationGroup


def load_json(file_path):
    with Path(file_path).open() as json_file:
        return json.load(json_file)


def load_investigation_group_data(investigation_groups):
    investigation_group_dict = {}
    groups_to_create = []

    for investigation_group in investigation_groups:
        current_obj = PatientInvestigationGroup.objects.filter(
            name=investigation_group["name"]
        ).first()
        if not current_obj:
            current_obj = PatientInvestigationGroup(name=investigation_group["name"])
            groups_to_create.append(current_obj)

        investigation_group_dict[str(investigation_group["id"])] = current_obj

    if groups_to_create:
        PatientInvestigationGroup.objects.bulk_create(groups_to_create)

    return investigation_group_dict


def extract_investigation_data(investigation):
    return {
        "name": investigation["name"],
        "unit": investigation.get("unit", ""),
        "ideal_value": investigation.get("ideal_value", ""),
        "min_value": parse_float(investigation.get("min")),
        "max_value": parse_float(investigation.get("max")),
        "investigation_type": investigation.get("type", None),
        "choices": investigation.get("choices", ""),
    }


def parse_float(value):
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def update_existing_investigation(existing_obj, data):
    for field, value in data.items():
        setattr(existing_obj, field, value)


def handle_investigations(investigations, investigation_group_dict):
    bulk_create_data = []
    bulk_update_data = []
    investigations_to_update_groups = []

    for investigation in investigations:
        data = extract_investigation_data(investigation)
        existing_obj = PatientInvestigation.objects.filter(name=data["name"]).first()

        if existing_obj:
            update_existing_investigation(existing_obj, data)
            bulk_update_data.append(existing_obj)
            investigations_to_update_groups.append(
                (existing_obj, investigation["category_id"])
            )
        else:
            new_obj = PatientInvestigation(**data)
            bulk_create_data.append(new_obj)
            investigations_to_update_groups.append(
                (new_obj, investigation["category_id"])
            )

    return bulk_create_data, bulk_update_data, investigations_to_update_groups


class Command(BaseCommand):
    help = "Seed Data for Investigations"

    def handle(self, *args, **kwargs):
        investigation_groups = load_json("data/investigation_groups.json")
        investigations = load_json("data/investigations.json")

        investigation_group_dict = load_investigation_group_data(investigation_groups)

        bulk_create_data, bulk_update_data, investigations_to_update_groups = (
            handle_investigations(investigations, investigation_group_dict)
        )

        with transaction.atomic():
            if bulk_create_data:
                PatientInvestigation.objects.bulk_create(bulk_create_data)

            if bulk_update_data:
                PatientInvestigation.objects.bulk_update(
                    bulk_update_data,
                    fields=[
                        "unit",
                        "ideal_value",
                        "min_value",
                        "max_value",
                        "investigation_type",
                        "choices",
                    ],
                )

            for investigation_obj, category_ids in investigations_to_update_groups:
                groups_to_add = [
                    investigation_group_dict.get(str(category_id))
                    for category_id in category_ids
                ]
                investigation_obj.groups.set(groups_to_add)

        if kwargs.get("verbosity", 1) > 0:
            self.stdout.write(
                self.style.SUCCESS("Successfully populated investigation data")
            )
