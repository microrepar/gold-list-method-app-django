import datetime
import uuid
from typing import List, Optional

from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from ninja import ModelSchema, Router, Schema
from ninja.orm import create_schema

from usermanager.models import User
from goldlistmethod.models.notebook import Notebook
from goldlistmethod.models.pagesection import PageSection

router = Router()

NotebookSchema = create_schema(Notebook, depth=1)
UserSchema = create_schema(User)
PageSectionSchema = create_schema(PageSection)


class NotebookSchemaOut(ModelSchema):
    pagesection_list: List[PageSectionSchema] = [] # type: ignore
    user: UserSchema # type: ignore

    class Meta:
        model = Notebook
        fields = ['id', 'created_at', 'updated_at', 'name', 'sentence_list_size', 'days_period', 
                  'foreign_idiom', 'mother_idiom',]


class NotebookIn(Schema):
    id: Optional[uuid.UUID] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None
    name: Optional[str] = None
    sentence_list_size: Optional[int] = None
    days_period: Optional[int] = None
    foreign_idiom: Optional[str] = None
    mother_idiom: Optional[str] = None
    user_id: Optional[int] = None

class Error(Schema):
    message: str

@router.get('/', response=List[NotebookSchema])
def list_notebooks(request):
    qs = Notebook.objects.all()
    return qs


@router.post('/', response={200: NotebookIn, 422: Error})
def registry(request, payload: NotebookIn):
    try:
        notebook = Notebook.objects.create(**payload.dict())
    except IntegrityError as error:
        return 422, {'message': f'{error}'}
    return notebook


@router.post('/find_by_field/', response=List[NotebookSchema])
def find_by_field(request, payload: NotebookIn):
    filters = {k: v for k, v in payload.dict().items() if v is not None}
    if filters:
        return Notebook.objects.filter(**filters)
    return Notebook.objects.filter(id=None)

@router.post('/find_by_field/clean/', response=List[NotebookSchema])
def find_by_field_clean(request, payload: NotebookIn):
    filters = {k: v for k, v in payload.dict().items() if v is not None}
    if filters:
        return Notebook.objects.filter(**filters)
    return Notebook.objects.filter(id=None)


@router.post('/find_by_field/depth/', response=List[NotebookSchemaOut])
def find_by_field_depth(request, payload: NotebookIn):
    filters = {k: v for k, v in payload.dict().items() if v is not None}
    if filters:
        return Notebook.objects.filter(**filters).select_related('user').prefetch_related('pagesection_list')
    return Notebook.objects.filter(id=None)
