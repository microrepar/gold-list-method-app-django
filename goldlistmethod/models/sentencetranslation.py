from django.db import models

from setup.base_models.base_model import BaseModel


class SentenceTranslation(BaseModel):
    foreign_language_sentence = models.CharField(max_length=200, blank=False, null=False)
    mother_language_sentence = models.CharField(max_length=200, blank=False, null=False)
    foreign_language_idiom = models.CharField(max_length=200)
    mother_language_idiom = models.CharField(max_length=200)

    class Meta:
        verbose_name = 'Sentence Translation'
        verbose_name_plural = 'Sentence Translations'
        constraints = [
            models.UniqueConstraint(
                fields=['foreign_language_sentence', 'foreign_language_idiom', 'mother_language_idiom'],
                name='unique_sentence_translation'
            )
        ]

    def __str__(self) -> str:
        return self.foreign_language_sentence

    