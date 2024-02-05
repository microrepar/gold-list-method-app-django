import streamlit_authenticator as stauth
from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    
    class ProfileChoice(models.TextChoices):
        A = 'A', 'Student'
        P = 'P', 'Professor'
        G = 'G', 'Admin'
        R = 'R', 'Root'
    
    class StatusChoices(models.TextChoices):
        ACTIVE = 'Active', 'Active'
        INACTIVE = 'Inactive', 'Inactive'
        PENDING = 'Pending', 'Pending'
        SUSPENDED = 'Suspended', 'Suspended'
        ARCHIVED = 'Archived', 'Archived'
        APPROVED = 'Approved', 'Approved'

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    name = models.CharField(max_length=300, null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)
    profile = models.CharField(max_length=1, choices=ProfileChoice.choices)
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default='Pending')
    password2 = models.CharField(max_length=128, null=True)
    repeat_password = models.CharField(max_length=128, null=True)

    def set_password(self, raw_password: str | None) -> None:
        self.password2 = stauth.Hasher([raw_password]).generate()[-1]
        return super().set_password(raw_password)