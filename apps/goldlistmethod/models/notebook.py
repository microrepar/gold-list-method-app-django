from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from usermanager.models import StudentUser, User

from setup.base_models.base_model import BaseModel


class Notebook(BaseModel):
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    name = models.CharField(max_length=200)
    sentence_list_size = models.IntegerField(
        default=20,
        # validators=[
        #     MinValueValidator(10),
        #     MaxValueValidator(25),
        # ]
    )
    days_period = models.IntegerField(
        default=15,
        # validators=[
        #     MinValueValidator(5),
        #     MaxValueValidator(15),
        # ]
    )
    foreign_idiom = models.CharField(max_length=100, default='English')
    mother_idiom = models.CharField(max_length=100, default='Portuguese Brazil')
    user = models.ForeignKey(StudentUser, verbose_name='Student', on_delete=models.CASCADE, related_name='notebook_list', null=True)

    class Meta:
        verbose_name = 'Notebook'
        verbose_name_plural = 'Notebooks'
        unique_together = ('name', 'user')

    
    def __str__(self) -> str:
        return self.name
