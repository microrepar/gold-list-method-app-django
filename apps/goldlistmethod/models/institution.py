import uuid

from django.db import models

from usermanager.models import User
from setup.base_models.base_model import BaseModel


class Institution(BaseModel):
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    max_qty_professor = models.IntegerField(default=1)
    max_qty_student = models.IntegerField(default=1)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    address = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField()
    website = models.URLField()
    established_date = models.DateField()
    description = models.TextField(blank=True, null=True)
    logo = models.ImageField(upload_to='institution_logos/', blank=True, null=True)

    def __str__(self):
        return self.name
