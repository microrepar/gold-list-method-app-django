import datetime
import uuid
from typing import List, Optional

from django.db.models import Max, OuterRef, Q, Subquery
from django.shortcuts import get_object_or_404
from ninja import Router, Schema
from ninja.orm import create_schema

from goldlistmethod.models import (GroupChoices, PageSection, SentenceLabel,
                                   SentenceTranslation)

router = Router()

PageSectionSchema = create_schema(PageSection)
SentenceTranslationSchema = create_schema(SentenceTranslation)


class PageSectionIn(Schema):
    id : Optional[uuid.UUID] = None
    created_at : Optional[datetime.date] = None
    notebook_id : Optional[uuid.UUID] = None
    page_number : Optional[int] = None
    group : Optional[GroupChoices] = None
    distillated : Optional[bool] = None
    distillation_at : Optional[datetime.date] = None
    distillation_actual : Optional[datetime.date] = None
    created_by_id : Optional[uuid.UUID] = None

class LastPageNumberSchema(Schema):
    last_pagenumber : int


@router.get('/', response=List[PageSectionSchema])
def list_pagesections(request):
    qs = PageSection.objects.all()
    return qs


@router.post('/', response=PageSectionSchema)
def registry(request, payload: PageSectionIn):
    pagesection = PageSection.objects.create(**payload.dict())
    return pagesection    


@router.get('/get_sentencelabel_by/{notebook_id}/{group}', response=List[SentenceTranslationSchema])
def get_sentencelabel_by_group(request, notebook_id: uuid.UUID, group: str):
    subquery = SentenceLabel.objects.filter(
        pagesection__group=group,
        pagesection__notebook_id=notebook_id
    ).values('sentencetranslation_id')
    return SentenceTranslation.objects.filter(pk__in=Subquery(subquery))


@router.post('/find_by_field/', response=List[PageSectionSchema])
def find_by_field(request, payload: PageSectionIn):
    filters = {k: v for k, v in payload.dict().items() if v is not None}
    if filters:
        return PageSection.objects.filter(**filters)
    return PageSection.objects.filter(id=None)


@router.get('/get_last_pagenumber/', response=LastPageNumberSchema)
def get_last_pagenumber(request, notebook_id: uuid.UUID):
    qs = PageSection.objects.filter(notebook__id=notebook_id)
    last_pagenumber = qs.aggregate(page_number=Max('page_number'))['page_number']
    if last_pagenumber:
        return LastPageNumberSchema(last_pagenumber=last_pagenumber)
    return LastPageNumberSchema(last_pagenumber=0)


@router.delete('/{pagesection_id}')
def delete_pagesection(request, pagesection_id: uuid.UUID):
    pagesection: PageSection = get_object_or_404(PageSection, id=pagesection_id)
    pagesection.delete()
    return {'success': True}
