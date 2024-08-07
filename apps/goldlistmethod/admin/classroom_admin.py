from typing import Any
from django import forms
from django.contrib import admin
from django.db.models.query import QuerySet
from django.http import HttpRequest
from goldlistmethod.models.classroom import ClassRoom
from usermanager.models import AdminUser, ProfessorUser, User


class ClassRoomAdminForm(forms.ModelForm):
    class Meta:
        model = ClassRoom
        exclude = ['created_by', 'institution']


class ClassRoomRootUserAdminForm(forms.ModelForm):
    class Meta:
        model = ClassRoom
        exclude = ['created_by']


class ClassRoomProfessorUserAdminForm(forms.ModelForm):
    class Meta:
        model = ClassRoom
        exclude = ['created_by', 'institution', 'professor']


class ClassRoomAdmin(admin.ModelAdmin):
    list_display = ('created_by', 'institution', 'professor', 'name', 'room_number', 'equipment', 'is_available', 'description',)
    
    def save_model(self, request, obj, form, change):        
        if not obj.created_by_id:
            obj.created_by = request.user
        if not obj.institution_id:
            if request.user.profile == request.user.ProfileChoices.ADMIN:
                user = AdminUser.objects.filter(id=request.user.id).first()
                obj.institution = user.responsible_institution
            elif request.user.profile == request.user.ProfileChoices.PROFESSOR:
                user = ProfessorUser.objects.filter(id=request.user.id).first()
                obj.institution = user.workplace
                obj.professor = user        
        super().save_model(request, obj, form, change)
    
    def get_form(self, request, obj=None, **kwargs):
        Form = ClassRoomAdminForm
        if request.user.profile == request.user.ProfileChoices.ROOT:
            Form = ClassRoomRootUserAdminForm
        if request.user.profile == request.user.ProfileChoices.PROFESSOR:
            Form = ClassRoomProfessorUserAdminForm        
        kwargs['form'] = Form
        return super().get_form(request, obj, **kwargs)
    
    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        qs = super().get_queryset(request)
        if request.user.profile == User.ProfileChoices.ROOT:
            return qs
        elif request.user.profile == User.ProfileChoices.ADMIN:
            user = AdminUser.objects.filter(id=request.user.id).first()
            return qs.filter(institution=user.responsible_institution)
        elif request.user.profile == User.ProfileChoices.PROFESSOR:
            return qs.filter(professor=request.user)
        elif request.user.profile == User.ProfileChoices.STUDENT:
            return qs.filter(students=request.user)
        else:
            qs.none()

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "professor":
            if request.user.profile == User.ProfileChoices.ROOT:
                kwargs["queryset"] = ProfessorUser.objects.all().order_by('username')
            elif request.user.profile == User.ProfileChoices.ADMIN:
                user = AdminUser.objects.filter(id=request.user.id).first()
                kwargs["queryset"] = ProfessorUser.objects.filter(workplace=user.responsible_institution).order_by('username')
            else:
                kwargs["queryset"] = ProfessorUser.objects.none()        
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
        


admin.site.register(ClassRoom, ClassRoomAdmin)