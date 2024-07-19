from typing import Any

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from goldlistmethod.models.customuser import CustomUser

admin.site.site_header = "Gold List Method App Admin"
admin.site.index_title = "App Admin"
admin.site.site_title = "Gold List Method App"

    
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'groups')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    fieldsets = UserAdmin.fieldsets + (
        ('Other information', {'fields': ('status', 'profile', 'name', 'age')}),
    )
    
    # exclude = ('password2', 'repeat_password')

admin.site.register(CustomUser, CustomUserAdmin)
