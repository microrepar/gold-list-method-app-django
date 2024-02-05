from django.db import models

from setup.base_models.base_model import BaseModel


class Sentence(BaseModel):
    foreign_language = models.CharField(max_length=255)
    mother_tongue = models.CharField(max_length=255)
    foreign_idiom = models.CharField(max_length=255)
    mother_idiom = models.CharField(max_length=255)


    class Meta:
        verbose_name = 'Sentence'
        verbose_name_plural = 'Sentences'

    def __str__(self) -> str:
        return self.foreign_language