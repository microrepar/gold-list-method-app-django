from .customuser import CustomUser
from django.db import models

from setup.base_models.base_model import BaseModel


class Notebook(BaseModel):
    name = models.CharField(max_length=200)
    list_size = models.IntegerField()
    days_period = models.IntegerField()
    foreign_idiom = models.CharField(max_length=100)
    mother_idiom = models.CharField(max_length=100)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notebook_list', null=True)


    class Meta:
        verbose_name = 'Notebook'
        verbose_name_plural = 'Notebooks'
        unique_together = ('name', 'user')

    
    def __str__(self) -> str:
        return self.name
