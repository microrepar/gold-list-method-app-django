from typing import Any
from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.db.models.query import QuerySet
from django.http import HttpRequest
from usermanager.models import AdminUser, ProfessorUser, StudentUser, User

admin.site.site_header = "Gold List Method App Admin"
admin.site.index_title = "App Admin"
admin.site.site_title = "Gold List Method App"


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = '__all__'


class CustomAdminUserChangeForm(UserChangeForm):
    class Meta:
        model = AdminUser
        fields = '__all__'


class CustomProfessorUserChangeForm(UserChangeForm):
    class Meta:
        model = ProfessorUser
        fields = '__all__'


class CustomStudentUserChangeForm(UserChangeForm):
    class Meta:
        model = StudentUser
        fields = '__all__'


class CustomUserAdmin(UserAdmin):
    list_filter = ('is_staff', 'is_superuser', 'groups')
    
    fieldsets = UserAdmin.fieldsets + (
        ('Other informations', {'fields': ('created_by', 'profile', 'status', 'name', 'age'),}),
    )
    
    ordering = ('profile', 'username',)

    def get_list_display(self, request):
        if '/usermanager/adminuser/' in request.path:
            return ('username', 'profile', 'created_by', 'responsible_institution', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser', 'date_joined')
        if '/usermanager/professoruser/' in request.path:
            return ('username', 'profile', 'created_by', 'workplace', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser', 'date_joined')
        if '/usermanager/studentuser/' in request.path:
            return ('username', 'profile', 'created_by', 'student_classroom', 'institution_name', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser', 'date_joined')
        else:
            return ['username', 'profile', 'email', 'created_by', 'first_name', 'last_name', 'is_staff', 'is_superuser', 'date_joined']

    def get_search_fields(self, request: HttpRequest) -> list[str]:
        if '/usermanager/adminuser/' in request.path:
            return ['username', 'email', 'first_name', 'last_name', 'profile', 'created_by__username', 'responsible_institution__name']
        if '/usermanager/professoruser/' in request.path:
            return ['username', 'email', 'first_name', 'last_name', 'profile', 'created_by__username', 'workplace__name']
        if '/usermanager/studentuser/' in request.path:
            return ['username', 'email', 'first_name', 'last_name', 'profile', 'created_by__username', 'student_classroom__institution__name']
        else:
            return ['username', 'email', 'first_name', 'last_name', 'profile', 'created_by__username']
    
    def institution_name(self, obj):
        return obj.student_classroom.institution.name
    institution_name.short_description = 'Institution name'

    def save_model(self, request, obj, form, change):        
        if not obj.created_by_id:
            obj.created_by = request.user
        
        if request.user.profile == User.ProfileChoices.ADMIN:
            user = AdminUser.objects.filter(id=request.user.id).first()
            if '/usermanager/adminuser/add/' in request.path:
                obj.responsible_institution = user.responsible_institution
            
            if '/usermanager/professoruser/add/' in request.path:
                obj.workplace = user.responsible_institution

        super().save_model(request, obj, form, change)

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        qs = super().get_queryset(request)
        if request.user.profile == User.ProfileChoices.ROOT:
            return qs        
        elif request.user.profile == User.ProfileChoices.ADMIN:
            user = AdminUser.objects.filter(id=request.user.id).first()
            if '/adminuser/' in request.path:
                return qs.filter(responsible_institution=user.responsible_institution)
            elif '/studentuser/' in request.path:                
                return qs.filter(student_classroom__institution=user.responsible_institution).distinct()
            elif '/professoruser/' in request.path:
                return qs.filter(workplace=user.responsible_institution)
        elif request.user.profile == User.ProfileChoices.PROFESSOR:
            if '/studentuser/' in request.path:
                return qs.filter(student_classroom__professor=request.user).distinct()
            else:
                return qs.filter(id=request.user.id)
        elif request.user.profile == User.ProfileChoices.STUDENT:
            return qs.filter(id=request.user.id)        
        return qs.none()
    
    def get_form(self, request, obj=None, **kwargs):        
        form = None            
        if '/usermanager/adminuser/' in request.path:
            CustomForm = CustomAdminUserChangeForm
        elif '/usermanager/professoruser/' in request.path:
            CustomForm = CustomProfessorUserChangeForm
        elif '/usermanager/studentuser/' in request.path:
            CustomForm = CustomStudentUserChangeForm
        else:
            CustomForm = CustomUserChangeForm
        
        if request.user.profile == User.ProfileChoices.ROOT:
            if '/add/' in request.path:
                if 'usermanager/studentuser/add/' in request.path:
                    from goldlistmethod.models import ClassRoom
                    qs_classroom = ClassRoom.objects.all()
                    class CustomUserCreationForm(UserCreationForm):
                        student_classroom = forms.ModelChoiceField(queryset=qs_classroom, required=True)                        
                        class Meta(UserCreationForm.Meta):
                            model = StudentUser
                            fields = UserCreationForm.Meta.fields + ('student_classroom',)
                    form = CustomUserCreationForm
                elif 'usermanager/adminuser/add/' in request.path:
                    from goldlistmethod.models import Institution
                    qs_institution = Institution.objects.all()
                    class CustomUserCreationForm(UserCreationForm):
                        responsible_institution = forms.ModelChoiceField(queryset=qs_institution, required=True)                        
                        class Meta(UserCreationForm.Meta):
                            model = AdminUser
                            fields = UserCreationForm.Meta.fields + ('responsible_institution',)
                    form = CustomUserCreationForm
                elif 'usermanager/professoruser/add/' in request.path:
                    from goldlistmethod.models import Institution
                    qs_institution = Institution.objects.all()
                    class CustomUserCreationForm(UserCreationForm):
                        workplace = forms.ModelChoiceField(queryset=qs_institution, required=True)                        
                        class Meta(UserCreationForm.Meta):
                            model = ProfessorUser
                            fields = UserCreationForm.Meta.fields + ('workplace',)
                    form = CustomUserCreationForm
                else:
                    form = UserCreationForm
            else:
                class Form(CustomForm):
                    def __init__(self, *args, **kwargs):
                        super().__init__(*args, **kwargs)
                        self.fields['profile'].disabled = True
                form = Form
                
        elif request.user.profile == User.ProfileChoices.ADMIN:
            if '/add/' in request.path:
                user = AdminUser.objects.filter(id=request.user.id).first()

                if 'usermanager/studentuser/add/' in request.path:
                    from goldlistmethod.models import ClassRoom
                    qs_classroom = ClassRoom.objects.filter(institution=user.responsible_institution)
                    class CustomUserCreationForm(UserCreationForm):
                        student_classroom = forms.ModelChoiceField(queryset=qs_classroom, required=True)                        
                        class Meta(UserCreationForm.Meta):
                            model = StudentUser
                            fields = UserCreationForm.Meta.fields + ('student_classroom',)
                    form = CustomUserCreationForm                    
                else:
                    form = UserCreationForm
            else:
                class Form(CustomForm):
                    def __init__(self, *args, **kwargs):
                        super().__init__(*args, **kwargs)
                        self.fields['is_superuser'].widget = forms.HiddenInput()
                        self.fields['username'].disabled = True
                        self.fields['profile'].disabled = True
                        self.fields['created_by'].disabled = True
                        self.fields['is_superuser'].disabled = True
                        self.fields['groups'].disabled = True
                        self.fields['user_permissions'].disabled = True
                        if '/usermanager/adminuser/' in request.path:
                            self.fields['responsible_institution'].disabled = True
                        if '/usermanager/professoruser/' in request.path:
                            self.fields['workplace'].disabled = True
                form = Form
        
        elif request.user.profile == User.ProfileChoices.PROFESSOR:
            if '/add/' in request.path:
                if 'usermanager/studentuser/add/' in request.path:
                    user = ProfessorUser.objects.filter(id=request.user.id).first()
                    from goldlistmethod.models import ClassRoom
                    qs_classroom = ClassRoom.objects.filter(professor=request.user)
                    class CustomUserCreationForm(UserCreationForm):
                        student_classroom = forms.ModelChoiceField(queryset=qs_classroom, required=True)                        
                        class Meta(UserCreationForm.Meta):
                            model = StudentUser
                            fields = UserCreationForm.Meta.fields + ('student_classroom',)
                    form = CustomUserCreationForm
                else:
                    form = UserCreationForm
            else:
                class Form(CustomForm):
                    def __init__(self, *args, **kwargs):
                        super().__init__(*args, **kwargs)
                        self.fields['is_superuser'].widget = forms.HiddenInput()
                        self.fields['username'].disabled = True
                        self.fields['status'].disabled = True
                        self.fields['profile'].disabled = True
                        self.fields['created_by'].disabled = True
                        self.fields['is_superuser'].disabled = True
                        self.fields['groups'].disabled = True
                        self.fields['user_permissions'].disabled = True
                        self.fields['last_login'].widget = forms.SplitDateTimeWidget(
                            date_attrs={'widget': forms.DateInput(attrs={'type': 'date'}), 'style': 'margin-right: 5px;'},
                            time_attrs={'widget': forms.TimeInput(attrs={'type': 'time'})}
                        )
                        self.fields['date_joined'].widget = forms.SplitDateTimeWidget(
                            date_attrs={'widget': forms.DateInput(attrs={'type': 'date'}), 'style': 'margin-right: 5px;'},
                            time_attrs={'widget': forms.TimeInput(attrs={'type': 'time'})}
                        )
                        self.fields['last_login'].disabled = True
                        self.fields['date_joined'].disabled = True
                        if '/usermanager/professoruser/' in request.path:
                            self.fields['workplace'].disabled = True
                form = Form
            
        elif request.user.profile == User.ProfileChoices.STUDENT:
            class Form(CustomForm):
                def __init__(self, *args, **kwargs):
                    super().__init__(*args, **kwargs)
                    self.fields['is_superuser'].widget = forms.HiddenInput()
                    self.fields['status'].disabled = True
                    self.fields['profile'].disabled = True
                    self.fields['created_by'].disabled = True
                    self.fields['is_superuser'].disabled = True
                    self.fields['groups'].disabled = True
                    self.fields['user_permissions'].disabled = True
                    self.fields['student_classroom'].disabled = True
                    self.fields['last_login'].widget = forms.SplitDateTimeWidget(
                        date_attrs={'widget': forms.DateInput(attrs={'type': 'date'}), 'style': 'margin-right: 5px;'},
                        time_attrs={'widget': forms.TimeInput(attrs={'type': 'time'})}
                    )
                    self.fields['date_joined'].widget = forms.SplitDateTimeWidget(
                        date_attrs={'widget': forms.DateInput(attrs={'type': 'date'}), 'style': 'margin-right: 5px;'},
                        time_attrs={'widget': forms.TimeInput(attrs={'type': 'time'})}
                    )
                    self.fields['last_login'].disabled = True
                    self.fields['date_joined'].disabled = True
            form = Form
        kwargs['form'] = form
        return super().get_form(request, obj, **kwargs)
    
    def get_fieldsets(self, request: HttpRequest, obj: Any | None = ...):
        if '/usermanager/studentuser/add/' in request.path:
            self.add_fieldsets = (
                (None, {'fields': ('username', 'password1', 'password2', 'student_classroom'),}),
            )
        elif '/usermanager/adminuser/add/' in request.path:
            if request.user.profile == User.ProfileChoices.ROOT:
                self.add_fieldsets = (
                    (None, {'fields': ('username', 'password1', 'password2', 'responsible_institution'),}),
                )
        elif '/usermanager/professoruser/add/' in request.path:
            if request.user.profile == User.ProfileChoices.ROOT:
                self.add_fieldsets = (
                    (None, {'fields': ('username', 'password1', 'password2', 'workplace'),}),
                )
        elif '/usermanager/adminuser/' in request.path:
            self.fieldsets = UserAdmin.fieldsets + (
                ('Other informations', {'fields': ('created_by', 'profile', 'status', 'responsible_institution', 'name', 'age'),}),
            )
        elif '/usermanager/professoruser/' in request.path:
            self.fieldsets = UserAdmin.fieldsets + (
                ('Other informations', {'fields': ('created_by', 'profile', 'status', 'workplace', 'name', 'age'),}),
            )
        elif '/usermanager/studentuser/' in request.path:
            self.fieldsets = UserAdmin.fieldsets + (
                ('Other informations', {'fields': ('created_by', 'profile', 'status', 'student_classroom', 'name', 'age'),}),
            )
        else:
            self.fieldsets = UserAdmin.fieldsets + (
                ('Other informations', {'fields': ('created_by', 'profile', 'status', 'name', 'age'),}),
            )
        return super().get_fieldsets(request, obj)
    

admin.site.register(User, CustomUserAdmin)
admin.site.register(AdminUser, CustomUserAdmin)
admin.site.register(ProfessorUser, CustomUserAdmin)
admin.site.register(StudentUser, CustomUserAdmin)
