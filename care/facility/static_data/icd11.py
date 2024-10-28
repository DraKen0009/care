import logging
import re
from typing import TypedDict

from django.core.paginator import Paginator
from redis.exceptions import RedisError
from redis_om import Field, Migrator
from redis_om.model.model import NotFoundError as RedisModelNotFoundError

from care.facility.models.icd11_diagnosis import ICD11Diagnosis
from care.utils.static_data.models.base import BaseRedisModel

logger = logging.getLogger(__name__)

DISEASE_CODE_PATTERN = r"^(?:[A-Z]+\d|\d+[A-Z])[A-Z\d.]*\s"


class ICD11Object(TypedDict):
    id: int
    label: str
    chapter: str


class ICD11(BaseRedisModel):
    id: int = Field(primary_key=True)
    label: str
    chapter: str = Field(index=True)
    has_code: int = Field(index=True)

    vec: str = Field(index=True, full_text_search=True)

    def get_representation(self) -> ICD11Object:
        return {
            "id": self.id,
            "label": self.label,
            "chapter": self.chapter if self.chapter != "null" else "",
        }


def load_icd11_diagnosis():
    logger.info("Loading ICD11 Diagnosis into the redis cache...")

    icd_objs = ICD11Diagnosis.objects.order_by("id").values_list(
        "id", "label", "meta_chapter_short"
    )
    paginator = Paginator(icd_objs, 5000)
    for page_number in paginator.page_range:
        for diagnosis in paginator.page(page_number).object_list:
            ICD11(
                id=diagnosis[0],
                label=diagnosis[1],
                chapter=diagnosis[2] or "null",
                has_code=1 if re.match(DISEASE_CODE_PATTERN, diagnosis[1]) else 0,
                vec=diagnosis[1].replace(".", "\\.", 1),
            ).save()
    Migrator().run()
    logger.info("ICD11 Diagnosis Loaded")


def get_icd11_diagnosis_object_by_id(
    diagnosis_id: int, as_dict=False
) -> tuple[ICD11 | ICD11Object | None, str | None]:
    """
    Retrieves ICD11 diagnosis by ID with Redis lookup and DB fallback.
    Returns a tuple: (diagnosis_data, error_message)
    """
    try:
        diagnosis = ICD11.get(diagnosis_id)
        return diagnosis.get_representation() if as_dict else diagnosis, None

    except RedisModelNotFoundError:
        try:
            diagnosis = ICD11Diagnosis.objects.get(id=diagnosis_id)

            icd11_obj = ICD11(
                id=diagnosis.id,
                label=diagnosis.label,
                chapter=diagnosis.meta_chapter_short or "null",
                has_code=1 if re.match(DISEASE_CODE_PATTERN, diagnosis.label) else 0,
                vec=diagnosis.label.replace(".", "\\.", 1),
            )
            icd11_obj.save()
            return icd11_obj.get_representation() if as_dict else icd11_obj, None

        except ICD11Diagnosis.DoesNotExist:
            return None, "Diagnosis with the specified ID not found."

    except RedisError:
        return None, "Redis connection issue encountered."

    except Exception as e:
        logger.error(
            "An unexpected error occurred while retrieving the diagnosis. Details - %s",
            e,
        )
        return None, "An unexpected error occurred while retrieving the diagnosis."


def get_icd11_diagnoses_objects_by_ids(diagnoses_ids: list[int]) -> list[ICD11Object]:
    if not diagnoses_ids:
        return []

    query = None
    for diagnosis_id in diagnoses_ids:
        if query is None:
            query = ICD11.id == diagnosis_id
        else:
            query |= ICD11.id == diagnosis_id

    diagnosis_objects: list[ICD11] = list(ICD11.find(query))
    return [diagnosis.get_representation() for diagnosis in diagnosis_objects]
