from django.db import models

from goldlistmethod.models.pagesection import PageSection
from goldlistmethod.models.sentence import Sentence
from setup.base_models.base_model import BaseModel


class PageSectionSentenceAssoc(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    page = models.IntegerField(null=True, blank=True)
    group = models.CharField(max_length=2)
    memorialized = models.BooleanField(default=False)
    distillated = models.BooleanField(default=False)
    notebook_id = models.IntegerField()
    
    pagesection = models.ForeignKey(PageSection, on_delete=models.CASCADE)
    sentence = models.ForeignKey(Sentence, on_delete=models.CASCADE)