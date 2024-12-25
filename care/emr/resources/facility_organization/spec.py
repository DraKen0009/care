from enum import Enum

from pydantic import UUID4, field_validator, model_validator

from care.emr.models.organziation import FacilityOrganization
from care.emr.resources.base import EMRResource
from care.emr.resources.user.spec import UserSpec
from care.facility.models import Facility


class FacilityOrganizationTypeChoices(str, Enum):
    dept = "dept"
    team = "team"
    other = "other"


class FacilityOrganizationBaseSpec(EMRResource):
    __model__ = FacilityOrganization
    __exclude__ = ["facility", "parent"]
    id: str = None
    active: bool = True
    org_type: FacilityOrganizationTypeChoices
    name: str
    description: str = ""
    parent: UUID4 | None = None
    metadata: dict = {}


class FacilityOrganizationWriteSpec(FacilityOrganizationBaseSpec):
    facility: UUID4

    # TODO Validations to confirm facility and org exists

    @field_validator("facility")
    @classmethod
    def validate_encounter_exists(cls, facility):
        if not Facility.objects.filter(external_id=facility).exists():
            err = "Faciltiy not found"
            raise ValueError(err)
        return facility

    @model_validator(mode="after")
    def validate_parent_organization(self):
        if (
            self.parent
            and not FacilityOrganization.objects.filter(
                facility__external_id=self.facility, external_id=self.parent
            ).exists()
        ):
            err = "Parent not found"
            raise ValueError(err)
        return self

    def perform_extra_deserialization(self, is_update, obj):
        if not is_update:
            obj.facility = Facility.objects.get(
                external_id=self.facility
            )  # Needs more validation
            if self.parent:
                obj.parent = FacilityOrganization.objects.get(
                    facility=obj.facility, external_id=self.parent
                )
                obj.level_cache = obj.parent.level_cache + 1
                obj.parent_cache = [*obj.parent.parent_cache, obj.parent.id]
                if obj.parent.root_org is None:
                    obj.root_org = obj.parent
                else:
                    obj.root_org = obj.parent.root_org
                obj.parent.has_children = True
                obj.parent.save(update_fields=["has_children"])
            else:
                obj.parent = None


class FacilityOrganizationReadSpec(FacilityOrganizationBaseSpec):
    created_by: UserSpec = dict
    updated_by: UserSpec = dict
    system_generated: bool
    level_cache: int = 0
    has_children: bool

    @classmethod
    def perform_extra_serialization(cls, mapping, obj):
        mapping["id"] = obj.external_id
        mapping["parent"] = obj.get_parent_json()

        if obj.created_by:
            mapping["created_by"] = UserSpec.serialize(obj.created_by)
        if obj.updated_by:
            mapping["updated_by"] = UserSpec.serialize(obj.updated_by)
