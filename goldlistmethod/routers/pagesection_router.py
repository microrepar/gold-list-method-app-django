import contextlib
import datetime
import uuid
from typing import List, Optional

from django.db import IntegrityError
from django.db.models import Exists, Max, OuterRef, Q, Subquery
from django.shortcuts import get_object_or_404
from ninja import ModelSchema, Router, Schema
from ninja.orm import create_schema

from goldlistmethod.models import (GroupChoices, Notebook, PageSection,
                                   SentenceLabel, SentenceTranslation)

router = Router()

PageSectionSchema = create_schema(PageSection)
SentenceLabelSchema = create_schema(SentenceLabel, depth=1)
SentenceTranslationSchema = create_schema(SentenceTranslation)
NotebookSchema = create_schema(Notebook) 


class PageSectionSchemaOut(ModelSchema):
    sentencelabels: List[SentenceLabelSchema] = []  # type: ignore
    notebook: NotebookSchema                        # type: ignore
    created_by: Optional[PageSectionSchema] = None            # type: ignore

    class Meta:
        model = PageSection
        fields = ['id', 'created_at', 'updated_at', 'page_number', 'group', 
                  'distillation_at', 'distillated', 'distillation_actual', ]


class PageSectionIn(Schema):
    id : Optional[uuid.UUID] = None
    created_at : Optional[datetime.date] = None
    notebook_id : Optional[uuid.UUID] = None
    page_number : Optional[int] = None
    group : Optional[GroupChoices] = None
    distillated : Optional[bool] = False
    distillation_at : Optional[datetime.date] = None
    distillation_actual : Optional[datetime.date] = None
    created_by_id : Optional[uuid.UUID] = None


class SentenceTranslationSchemaIn(ModelSchema):
    class Meta:
        model = SentenceTranslation
        fields = ['foreign_language_sentence', 'mother_language_sentence', 
                  'foreign_language_idiom', 'mother_language_idiom', ]


class SentenceLabelSchemaIn(Schema):
    pagesection_id: Optional[uuid.UUID] = None
    sentencetranslation: Optional[SentenceTranslationSchemaIn] = None
    translation: Optional[str] = None
    memorialized: Optional[bool] = None


class PageSectionDepthIn(Schema):
    created_at : datetime.date
    page_number : Optional[int] = None
    group : Optional[GroupChoices] = None
    distillated : Optional[bool] = False
    distillation_at : Optional[datetime.date] = None
    distillation_actual : Optional[datetime.date] = None
    notebook_id : uuid.UUID
    created_by_id : Optional[uuid.UUID] = None
    sentencelabels: Optional[List[SentenceLabelSchemaIn]] = []


class SentenceLabelUpdateIn(Schema):
    id: uuid.UUID
    pagesection_id: Optional[uuid.UUID] = None
    sentencetranslation_id: Optional[uuid.UUID] = None
    translation: Optional[str] = None
    memorialized: Optional[bool] = None


class PageSectionUpdateDepthIn(Schema):
    page_number : Optional[int] = None
    group : Optional[GroupChoices] = None
    distillated : Optional[bool] = False
    distillation_at : Optional[datetime.date] = None
    distillation_actual : Optional[datetime.date] = None
    notebook_id : Optional[uuid.UUID] = None
    created_by_id : Optional[uuid.UUID] = None
    sentencelabels: Optional[List[SentenceLabelUpdateIn]] = []


class LastPageNumberSchema(Schema):
    last_pagenumber : int


class Error(Schema):
    message: str


@router.get('/', response=List[PageSectionSchema])
def list_pagesections(request):
    qs = PageSection.objects.all()
    return qs


@router.post('/', response=PageSectionSchema)
def registry(request, payload: PageSectionIn):
    pagesection = PageSection.objects.create(**payload.dict())
    return pagesection    


@router.post('/depth/', response={200: PageSectionSchemaOut, 422: Error})
def registry_depth(request, payload: PageSectionDepthIn):
    payload_dict = payload.dict()
    sentencelabels_dict = payload_dict.pop('sentencelabels')
    pagesection = None
    try:
        pagesection = PageSection.objects.create(**payload_dict)
    except IntegrityError as error:
        return  422, {'message': f'registry_depth error: PageSection create - {str(error)}'}
    
    existing_sentence_memo_list = []
    existing_sentence_list = []
    for sl_dict in sentencelabels_dict:
        st_dict = sl_dict.pop('sentencetranslation')
        
        sentencetranslation = None
        with contextlib.suppress(IntegrityError):
            sentencetranslation = SentenceTranslation.objects.create(**st_dict)
        
        if not sentencetranslation:
            sentencetranslation = SentenceTranslation.objects.filter(
                Q(foreign_language_sentence__iexact=st_dict['foreign_language_sentence']) &
                Q(foreign_language_idiom__iexact=st_dict['foreign_language_idiom']) &
                Q(mother_language_idiom__iexact=st_dict['mother_language_idiom'])
            ).first()

            if pagesection.group == GroupChoices.HEADLIST:            
                if SentenceLabel.objects.filter(sentencetranslation=sentencetranslation, 
                                                pagesection__notebook=pagesection.notebook, 
                                                memorialized=True).exists():
                    existing_sentence_memo_list.append(sentencetranslation.foreign_language_sentence)
                
                if SentenceLabel.objects.filter(Q(sentencetranslation=sentencetranslation) &
                                                Q(pagesection__notebook=pagesection.notebook) &
                                                ~Q(pagesection__group=GroupChoices.NEW_PAGE)
                                                ).exists():
                    existing_sentence_list.append(sentencetranslation.foreign_language_sentence)
                
                if existing_sentence_list or existing_sentence_memo_list:
                    continue
        
        try:
            sl_dict['pagesection_id'] = pagesection.id
            sl_dict['sentencetranslation_id'] = sentencetranslation.id

            sentencelabel = SentenceLabel.objects.create(**sl_dict)
        except Exception as error:
            pagesection.delete() 
            return 422, {'message': f'registry_depth error: SentenceLabel create - {str(error)}'}
    
    if existing_sentence_list or existing_sentence_memo_list:
        pagesection.delete()
        messages = ''
        if existing_sentence_list:
            if len(existing_sentence_list) == 1:
                messages = '\nThis phrase is about to be distilled on other page: \n' + '; '.join(existing_sentence_list)
            else:
                messages = '\nThese phrases are about to be distilled on other pages: \n' + '; '.join(existing_sentence_list)
        
        if existing_sentence_memo_list:
            if len(existing_sentence_memo_list) == 1:
                messages = '\nThis phrase have already been memorized: \n' + '; '.join(existing_sentence_memo_list)
            else:
                messages = '\nThese phrases have already been memorized: \n' + '; '.join(existing_sentence_memo_list)
        
        return 422, {'message': messages}
        
    return pagesection


@router.get('/get_sentencelabel_by/{notebook_id}/{group}', response=List[SentenceTranslationSchema])
def get_sentencelabel_by_group(request, notebook_id: uuid.UUID, group: str):
    if group == GroupChoices.NEW_PAGE:
        np_group_filter = SentenceLabel.objects.filter(
            pagesection__group=GroupChoices.NEW_PAGE,
            pagesection__notebook_id=notebook_id).values('sentencetranslation_id')
                 
        distillated_false_subquery = SentenceLabel.objects.filter(
            Q(pagesection__notebook_id=notebook_id) &
            Q(pagesection__distillated=False) &
            ~Q(pagesection__group=GroupChoices.NEW_PAGE) &
            ~Q(memorialized=True)).values('sentencetranslation_id')

        subquery = (SentenceLabel.objects.filter(sentencetranslation_id__in=np_group_filter)
                  .exclude(sentencetranslation_id__in=distillated_false_subquery)).values('sentencetranslation_id')

    else:
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


@router.post('/find_by_field/depth/', response=List[PageSectionSchemaOut])
def find_by_field_depth(request, payload: PageSectionIn):
    filters = payload.dict(exclude_unset=True)
    if filters:
        return (PageSection.objects.filter(**filters)
                .select_related('notebook', 'created_by')
                .prefetch_related('sentencelabels')
               )
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


@router.put('/{pagesection_id}', response=PageSectionSchema)
def update(request, pagesection_id: uuid.UUID, payload: PageSectionIn):
    pagesection = get_object_or_404(PageSection, id=pagesection_id)
    update_fields = payload.dict(exclude_unset=True)
    for attr, value in update_fields.items():
        setattr(pagesection, attr, value)
    pagesection.save()
    return pagesection


@router.put('/depth/{pagesection_id}',  response={200: PageSectionSchemaOut, 422: Error, 404: Error})
def update_depth(request, pagesection_id: uuid.UUID, payload: PageSectionUpdateDepthIn):
    pagesection = None    
    try:
        pagesection = get_object_or_404(PageSection, id=pagesection_id)
        
        update_fields_dict = payload.dict(exclude_unset=True)
        sentencelabels_dict = update_fields_dict.pop('sentencelabels')
        for attr, value in update_fields_dict.items():
            setattr(pagesection, attr, value)
    
        sl_obj_list = []
        for sl_dict in sentencelabels_dict:
            sentencelabel = get_object_or_404(SentenceLabel, id=sl_dict['id'])
            sl_dict = {k: v for k, v in sl_dict.items() if v}
            for attr, value in sl_dict.items():
                setattr(sentencelabel, attr, value)
            sl_obj_list.append(sentencelabel)
    except Exception as error:        
        return 404, {'message': f'{str(error)}'}

    try:
        for sl in sl_obj_list:
            sl.save()
        pagesection.save()
    except Exception as error:
        return 422, {'message': f'{str(error)}'}

    return pagesection
