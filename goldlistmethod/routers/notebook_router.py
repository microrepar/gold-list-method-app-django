import datetime
from typing import List, Optional
import uuid
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from ninja import Router, Schema
from ninja.orm import create_schema

from goldlistmethod.models.notebook import Notebook

router = Router()

NotebookSchema = create_schema(Notebook, depth=1)

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


@router.post('/', response={200: NotebookIn, 500: Error})
def registry(request, payload: NotebookIn):
    try:
        notebook = Notebook.objects.create(**payload.dict())
    except IntegrityError as error:
        return 400, {'message': f'{error}'}
    return notebook


@router.post('/find_by_field/', response=List[NotebookSchema])
def find_by_field(request, payload: NotebookIn):
    filters = {k: v for k, v in payload.dict().items() if v is not None}
    if filters:
        return Notebook.objects.filter(**filters)
    return Notebook.objects.filter(id=None)