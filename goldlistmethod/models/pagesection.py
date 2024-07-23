from django.db import models
from django.utils import timezone

from setup.base_models.base_model import BaseModel

from .model_choices import GroupChoices


class PageSection(BaseModel):    
    created_at = models.DateField('Data cadastro', default=timezone.now)
    notebook = models.ForeignKey('Notebook', on_delete=models.CASCADE, related_name='pagesection_list')
    page_number = models.IntegerField()
    group = models.CharField(max_length=2, choices=GroupChoices.choices, default='A')
    distillation_at = models.DateField(null=True, blank=True)
    distillated = models.BooleanField(null=True, blank=True)
    distillation_actual = models.DateField(null=True, blank=True)

    created_by = models.ForeignKey('PageSection', on_delete=models.SET_NULL, null=True, blank=True)
        
    class Meta:
        verbose_name = 'Page Section'
        verbose_name_plural = 'Page Sections'
    
    def __str__(self) -> str:
        return f'page={self.page_number}, group{self.group}, distillation_at={self.distillation_at}'
    