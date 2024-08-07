import uuid
from typing import List, Optional

from django.shortcuts import get_object_or_404
from ninja import Router, Schema
from ninja.errors import ValidationError
from ninja.orm import create_schema
from pydantic import field_validator

from goldlistmethod.models import SentenceTranslation

router = Router()


SentenceTranslationSchema = create_schema(SentenceTranslation)


class Error(Schema):
    message: str


class SentenceTranslationFields(Schema):
    id : Optional[uuid.UUID] = None
    foreign_language_sentence : Optional[str] = None
    mother_language_sentence : Optional[str] = None


@router.get('/', response=List[SentenceTranslationSchema])
def list_sentencetranslation(request):
    qs = SentenceTranslation.objects.all()
    return qs


class SentenceTranslationIn(Schema):
    foreign_language_sentence: str
    mother_language_sentence: str
    foreign_language_idiom: str
    mother_language_idiom: str        
    
    @field_validator('foreign_language_sentence', 'mother_language_sentence',
                     'foreign_language_idiom', 'mother_language_idiom')
    @classmethod
    def no_blank_or_whitespace(cls, v):
        if not v.strip():
            raise ValidationError('There is one or more empty fields to sentence registry.')
        return v
    
    
@router.post('/',  response={200: SentenceTranslationSchema, 409: Error})
def registry(request, payload: SentenceTranslationIn):
    try:
        sentencetranslation = SentenceTranslation.objects.create(**payload.dict())
    except Exception as error:
        return 409, {'message': f'This sentence already exits. - {str(error)}'}
    return sentencetranslation


@router.post('/find_by_field/', response=List[SentenceTranslationSchema])
def find_by_field(request, payload: SentenceTranslationFields):
    filters = {k: v for k, v in payload.dict().items() if v is not None}
    if filters:
        sentencetranslations = SentenceTranslation.objects.filter(**filters)
        return sentencetranslations
    return SentenceTranslation.objects.filter(id=None)
