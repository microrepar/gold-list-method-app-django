from typing import Any
from django import forms
from django.contrib import admin
from django.db.models.query import QuerySet
from django.http import HttpRequest
from goldlistmethod.models import Institution


class InstitutionAdminForm(forms.ModelForm):
    class Meta:
        model = Institution
        exclude = ['created_by']


class InstitutionAdmin(admin.ModelAdmin):
    form = InstitutionAdminForm

    readonly_fields = ('list_professors', 'list_responsible_people')

    def list_professors(self, obj):
        return " | ".join([professor.username for professor in obj.professors.all()])
    list_professors.short_description = 'Professors'

    def list_responsible_people(self, obj):
        return " | ".join([person.username for person in obj.responsible_people.all()])
    list_responsible_people.short_description = 'Responsible people'
    
    def save_model(self, request, obj, form, change):        
        if not obj.created_by_id:
            obj.created_by = request.user            
        super().save_model(request, obj, form, change)

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        qs = super().get_queryset(request)
        User = request.user.__class__
        if request.user.profile == User.ProfileChoices.ROOT:
            return qs
        elif request.user.profile == User.ProfileChoices.ADMIN:
            return qs.filter(responsible_people=request.user)
        elif request.user.profile == User.ProfileChoices.PROFESSOR:
            return qs.filter(professors=request.user)
        else:
            qs.none()


admin.site.register(Institution, InstitutionAdmin)
