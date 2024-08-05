from django.db import models

from usermanager.models import ProfessorUser, User
from goldlistmethod.models.institution import Institution
from setup.base_models.base_model import BaseModel


class ClassRoom(BaseModel):
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='classroms')
    professor = models.ForeignKey(ProfessorUser, on_delete=models.PROTECT, related_name='classroms', null=True, blank=True)

    name = models.CharField(max_length=255)
    room_number = models.IntegerField()
    equipment = models.CharField(max_length=255)
    is_available = models.BooleanField(default=True)
    description = models.TextField(blank=True, null=True)


