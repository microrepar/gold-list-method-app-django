from typing import Any
from django import forms
from django.contrib import admin
from django.db.models.query import QuerySet
from django.http import HttpRequest
from goldlistmethod.models.classroom import ClassRoom
from usermanager.models import AdminUser, ProfessorUser, User


class ClassRoomRootUserAdminForm(forms.ModelForm):
    class Meta:
        model = ClassRoom
        exclude = ['created_by']


class ClassRoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'room_number', 'professor', 'institution', 'equipment', 'is_available', 'description', 'created_by',)

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
        if request.user.profile == request.user.ProfileChoices.ADMIN:
            user = AdminUser.objects.filter(id=request.user.id).first()
            institution_id = user.responsible_institution.id
            qs_institution = user.responsible_institution.__class__.objects.filter(id=institution_id)
            class ClassRoomAdminForm(forms.ModelForm):
                institution = forms.ModelChoiceField(queryset=qs_institution, 
                                                     initial=user.responsible_institution)
                class Meta:
                    model = ClassRoom
                    exclude = ['created_by']
                
                def __init__(self, *args, **kwargs):
                    super().__init__(*args, **kwargs)
                    self.fields['institution'].disabled = True

            Form = ClassRoomAdminForm
            
        elif request.user.profile == request.user.ProfileChoices.ROOT:
            Form = ClassRoomRootUserAdminForm
        
        elif request.user.profile == request.user.ProfileChoices.PROFESSOR:
            qs_professoruser = ProfessorUser.objects.filter(id=request.user.id)
            professoruser = qs_professoruser.first()
            institution_id = professoruser.workplace.id
            qs_institution = professoruser.workplace.__class__.objects.filter(id=institution_id)
            class ClassRoomProfessorUserAdminForm(forms.ModelForm):
                institution = forms.ModelChoiceField(queryset=qs_institution, 
                                                     initial=professoruser.workplace)
                professor = forms.ModelChoiceField(queryset=qs_professoruser, 
                                                     initial=professoruser)
                class Meta:
                    model = ClassRoom
                    exclude = ['created_by',]
                
                def __init__(self, *args, **kwargs):
                    super().__init__(*args, **kwargs)
                    self.fields['institution'].disabled = True
                    self.fields['professor'].disabled = True

            Form = ClassRoomProfessorUserAdminForm        
        else:
            Form
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