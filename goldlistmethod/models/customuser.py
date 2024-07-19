import streamlit_authenticator as stauth
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator

from .model_choices import ProfileChoices, StatusChoices


class CustomUser(AbstractUser):
    name = models.CharField(max_length=250, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    profile = models.CharField(max_length=1, choices=ProfileChoices.choices, default='A')
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default='Pending')
    password2 = models.CharField(max_length=128, null=True)
    repeat_password = models.CharField(max_length=128, null=True)
    age = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(6),])

    def set_password(self, raw_password: str | None) -> None:
        self.password2 = stauth.Hasher([raw_password]).generate()[-1]
        return super().set_password(raw_password)
