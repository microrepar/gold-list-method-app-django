from typing import Any

from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from goldlistmethod.models.customuser import CustomUser


class CustomUserAdminForm(forms.ModelForm):
    
    class Meta:
        model = CustomUser
        exclude = ('password2', 'repeat_password')
        fields = ['username', 'email', 'password']

    def __init__(self, *args, **kwargs):
        super(CustomUserAdminForm, self).__init__(*args, **kwargs)
        self.fields['password'].disabled = True

    
class CustomUserAdmin(UserAdmin):
    form = CustomUserAdminForm


admin.site.register(CustomUser, CustomUserAdmin)
