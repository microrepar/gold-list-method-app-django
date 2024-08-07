from django import forms
from django.contrib import admin
from goldlistmethod.models import Notebook
from usermanager.models import AdminUser, ProfessorUser, StudentUser, User


class NotebookAdminForm(forms.ModelForm):
    class Meta:
        model = Notebook
        exclude = ['created_by']


class NotebookAdmin(admin.ModelAdmin):
    form = NotebookAdminForm

    list_display = ('name', 'created_by', 'user', 'foreign_idiom', 'mother_idiom')
    list_display_link = ('name', 'user', 'foreign_idiom', 'mother_idiom')

    def save_model(self, request, obj, form, change):        
        if not obj.created_by_id:
            obj.created_by = request.user            
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        user = request.user
        if user.profile == user.ProfileChoices.STUDENT :
            return qs.filter(user__id=request.user.id)
        return qs

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "user":
            if request.user.profile == User.ProfileChoices.ROOT:
                kwargs["queryset"] = StudentUser.objects.all().order_by('username')            
            elif request.user.profile == User.ProfileChoices.ADMIN:
                user = AdminUser.objects.filter(id=request.user.id).first()
                kwargs["queryset"] = StudentUser.objects.filter(student_classroom__institution=user.responsible_institution).order_by('username')            
            elif request.user.profile == User.ProfileChoices.PROFESSOR:
                kwargs["queryset"] = StudentUser.objects.filter(student_classroom__professor=request.user).order_by('username')            
            else:
                kwargs["queryset"] = StudentUser.objects.none()        
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
        


admin.site.register(Notebook, NotebookAdmin)