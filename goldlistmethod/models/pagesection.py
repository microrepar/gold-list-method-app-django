import json

from django.db import models

from setup.base_models.base_model import BaseModel


class PageSection(BaseModel):
    class GroupChoices(models.TextChoices):
        HEADLIST = 'A', 'HEADLIST'
        B = 'B', 'B'
        C = 'C', 'C'
        D = 'D', 'D'
        NEW_PAGE = 'NP', 'NP'
        REMOVED = 'RM', 'RM'

    section_number = models.IntegerField()
    page_number = models.IntegerField()
    _group = models.CharField(max_length=2, choices=GroupChoices.choices, db_column='group')
    distillation_at = models.DateField(null=True)
    distillated = models.BooleanField(default=False, null=True)
    distillation_actual = models.DateField(null=True)
    _translated_sentences = models.TextField(db_column='translated_sentences', null=True)
    _memorializeds = models.TextField(db_column='memorializeds', null=True)

    notebook = models.ForeignKey('Notebook', on_delete=models.CASCADE, related_name='page_section_list')
    created_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    
    
    class Meta:
        verbose_name = 'Page Section'
        verbose_name_plural = 'Page Sections'
    
    def __str__(self) -> str:
        return f'page={self.page_number}, group{self._group}, section{self.section_number}'

    @property
    def translated_sentences(self):
        return json.loads(self._translated_sentences)

    @translated_sentences.setter
    def translated_sentences(self, bool_list):
        self._translated_sentences = json.dumps(bool_list)

    @property
    def memorializeds(self):
        return json.loads(self._memorializeds)

    @memorializeds.setter
    def memorializeds(self, bool_list):
        self._memorializeds = json.dumps(bool_list)
