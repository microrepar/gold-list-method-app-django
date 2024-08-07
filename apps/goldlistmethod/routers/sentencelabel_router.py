import uuid
from typing import List, Optional

from django.shortcuts import get_object_or_404
from ninja import Router, Schema
from ninja.orm import create_schema

from goldlistmethod.models import SentenceLabel

router = Router()

SentenceLabelSchema = create_schema(SentenceLabel)


class SentenceLabelFilterSchema(Schema):
    pagesection_id : Optional[uuid.UUID] = None


class SentenceLabelIn(Schema):
    sentencetranslation_id: uuid.UUID
    pagesection_id: uuid.UUID
    translation: Optional[str] = None
    memorized: Optional[bool] = None

class SentenceLabelUpdate(Schema):
    translation: str
    memorized: bool


@router.get('/', response=List[SentenceLabelSchema])
def list_sentencelabel(request):
    qs = SentenceLabel.objects.all()
    return qs


@router.post('/', response=SentenceLabelSchema)
def registry(request, payload: SentenceLabelIn):
    sentencelabel = SentenceLabel.objects.create(**payload.dict())
    return sentencelabel


@router.post('/find_by_field/', response=List[SentenceLabelSchema])
def find_by_field(request, payload: SentenceLabelFilterSchema):
    filters = {k: v for k, v in payload.dict().items() if v is not None}
    if filters:
        return SentenceLabel.objects.filter(**filters)
    return SentenceLabel.objects.filter(id=None)


@router.put('/{sentencelabel_id}', response=SentenceLabelSchema)
def update(request, sentencelabel_id: uuid.UUID, payload: SentenceLabelUpdate):
    sentencelabel = get_object_or_404(SentenceLabel, id=sentencelabel_id)
    for attr, value in payload.dict().items():
        setattr(sentencelabel, attr, value)
    sentencelabel.save()
    return sentencelabel
