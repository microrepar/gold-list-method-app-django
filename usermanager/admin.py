from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from usermanager.models import User, ProfessorUser, AdminUser, StudentUser

admin.site.site_header = "Gold List Method App Admin"
admin.site.index_title = "App Admin"
admin.site.site_title = "Gold List Method App"


class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'groups')
    
    fieldsets = UserAdmin.fieldsets + (
        ('Other information', {'fields': ('status', 'profile', 'name', 'age')}),
    )

    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    # exclude = ('password2', 'repeat_password')


class CustomAdminUserAdmin(UserAdmin):
    ...


class CustomProfessorUserAdmin(UserAdmin):
    ...


class CustomStudentUserAdmin(UserAdmin):
    ...


admin.site.register(User, CustomUserAdmin)
admin.site.register(AdminUser, CustomAdminUserAdmin)
admin.site.register(ProfessorUser, CustomProfessorUserAdmin)
admin.site.register(StudentUser, CustomStudentUserAdmin)

