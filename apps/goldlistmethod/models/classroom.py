from django import forms
from django.core.validators import MinValueValidator
from django.db import models
from goldlistmethod.models.institution import Institution
from usermanager.models import ProfessorUser, User

from setup.base_models.base_model import BaseModel


class ClassRoom(BaseModel):
    name = models.CharField(max_length=255)
    room_number = models.IntegerField(validators=[MinValueValidator(1)])
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    professor = models.ForeignKey(ProfessorUser, on_delete=models.PROTECT, related_name='classrooms')
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='classrooms')

    equipment = models.CharField(max_length=255, null=True, blank=True)
    is_available = models.BooleanField(default=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Class Room'
        verbose_name_plural = 'Class Rooms'
        unique_together = ('name', 'room_number', 'institution')

    def __str__(self):
        professor = ''
        institution = ''
        if self.professor:
            professor = ' - ' + self.professor.username
            institution = ' - ' + self.institution.abbr
        return f'{self.name} {self.room_number}{professor}{institution}'


