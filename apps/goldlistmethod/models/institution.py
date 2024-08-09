from django.core.validators import MinValueValidator
from django.db import models
from usermanager.models import User

from setup.base_models.base_model import BaseModel


class Institution(BaseModel):
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    abbr = models.CharField(verbose_name='Abbreviation', max_length=10)
    max_qty_professor = models.IntegerField(default=5, validators=[MinValueValidator(1)])
    max_qty_student = models.IntegerField(default=5, validators=[MinValueValidator(1)])
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField()
    website = models.URLField(null=True, blank=True)
    established_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    logo = models.ImageField(upload_to='institution_logos/', blank=True, null=True)
    
    class Meta:
        verbose_name = 'Institution'
        verbose_name_plural = 'Institutions'
    

    def __str__(self):
        return self.name
    

