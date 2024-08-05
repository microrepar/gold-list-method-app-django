import streamlit_authenticator as stauth
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db import models


class User(AbstractUser):
        
    class ProfileChoices(models.TextChoices):
        STUDENT = 'Student', 'Student'
        PROFESSOR = 'Professor', 'Professor'
        ADMIN = 'Admin', 'Admin'
        ROOT = 'Root', 'Root'
        UNDEFINED = 'Undefined', 'Undefined'

    class StatusChoices(models.TextChoices):
        ACTIVE    = 'Active', 'Active'
        INACTIVE  = 'Inactive', 'Inactive'
        PENDING   = 'Pending', 'Pending'
        SUSPENDED = 'Suspended', 'Suspended'
        ARCHIVED  = 'Archived', 'Archived'
        APPROVED  = 'Approved', 'Approved'
    
    name = models.CharField(max_length=250, null=True, blank=True)
    created_by = models.ForeignKey('User', on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    
    profile = models.CharField(max_length=10, choices=ProfileChoices.choices, default=ProfileChoices.UNDEFINED)
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.PENDING)
    password2 = models.CharField(max_length=128, null=True)
    repeat_password = models.CharField(max_length=128, null=True)
    age = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(6),])

    def set_password(self, raw_password: str | None) -> None:
        self.password2 = stauth.Hasher([raw_password]).generate()[-1]
        return super().set_password(raw_password)
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'


class AdminUser(User):
    responsible_institution = models.ForeignKey('goldlistmethod.Institution', on_delete=models.SET_NULL, null=True, blank=True, related_name='responsable_people')

    class Meta:
        verbose_name = 'Administrator'
        verbose_name_plural = 'Administrators'
      
    def save(self, *args, **kwargs):
        self.profile = User.ProfileChoices.ADMIN
        super().save(*args, **kwargs)


class ProfessorUser(User):
    workplace = models.ForeignKey('goldlistmethod.Institution', on_delete=models.SET_NULL, null=True, blank=True, related_name='professors')
    
    class Meta:
        verbose_name = 'Professor'
        verbose_name_plural = 'Professors'

    def save(self, *args, **kwargs):
        self.profile = User.ProfileChoices.PROFESSOR
        super().save(*args, **kwargs)



class StudentUser(User):

    class Meta:
        verbose_name = 'Student'
        verbose_name_plural = 'Students'
      
    def save(self, *args, **kwargs):
        self.profile = User.ProfileChoices.STUDENT
        super().save(*args, **kwargs)