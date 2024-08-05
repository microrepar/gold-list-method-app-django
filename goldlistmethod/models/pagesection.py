from django.db import models
from django.utils import timezone

from setup.base_models.base_model import BaseModel


class PageSection(BaseModel):

    class GroupChoices(models.TextChoices):
        HEADLIST = 'A', 'HEADLIST'
        B        = 'B', 'B'
        C        = 'C', 'C'
        D        = 'D', 'D'
        NEW_PAGE = 'NP', 'NP'
        REMOVED  = 'RM', 'RM'


    created_at = models.DateField(default=timezone.now)
    notebook = models.ForeignKey('Notebook', on_delete=models.CASCADE, related_name='pagesection_list')
    page_number = models.IntegerField()
    group = models.CharField(max_length=2, choices=GroupChoices.choices, default='A')
    distillation_at = models.DateField(null=True, blank=True)
    distillated = models.BooleanField(default=False)
    distillation_actual = models.DateField(null=True, blank=True)

    created_by = models.ForeignKey('PageSection', on_delete=models.SET_NULL, null=True, blank=True)
        
    class Meta:
        verbose_name = 'Page Section'
        verbose_name_plural = 'Page Sections'
        unique_together = ('group', 'created_at', 'distillation_at',)
    
    def __str__(self) -> str:
        return f'page={self.page_number}, group{self.group}, distillation_at={self.distillation_at}'
    