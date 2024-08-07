from django.db import models

from usermanager.models import ProfessorUser, User
from goldlistmethod.models.institution import Institution
from setup.base_models.base_model import BaseModel


class ClassRoom(BaseModel):
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='classrooms')
    professor = models.ForeignKey(ProfessorUser, on_delete=models.PROTECT, related_name='classrooms')

    name = models.CharField(max_length=255)
    room_number = models.IntegerField()
    equipment = models.CharField(max_length=255)
    is_available = models.BooleanField(default=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Class Room'
        verbose_name_plural = 'Class Rooms'

    def __str__(self):
        return f'{self.name} - {self.room_number}'


