from django.db import models

from setup.base_models.base_model import BaseModel

from .pagesection import PageSection
from .sentencetranslation import SentenceTranslation


class SentenceLabel(BaseModel):    
    sentencetranslation = models.ForeignKey(SentenceTranslation, on_delete=models.PROTECT)
    pagesection = models.ForeignKey(PageSection, on_delete=models.CASCADE, related_name='sentencelabels')
    translation = models.CharField(max_length=255, default='', null=True, blank=True)
    memorized = models.BooleanField(default=False, null=True, blank=True)

    class Meta:
        verbose_name = 'Sentence Label'
        verbose_name_plural = 'Sentence Labels'

    def __str__(self) -> str:
        return self.sentencetranslation.foreign_language_sentence
