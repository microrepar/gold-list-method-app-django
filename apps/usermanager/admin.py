from typing import Any

from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.contrib.auth.models import Group
from django.db.models.fields.related import ForeignKey
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

    def get_group_list(self, obj):
        return " | ".join([g.name for g in obj.groups.all()]) or 'Undefined'
    get_group_list.short_description = 'Groups'

    def get_profile(self, obj):
        adminuser = AdminUser.objects.filter(id=obj.id)
        professoruser = ProfessorUser.objects.filter(id=obj.id)
        studentuser = StudentUser.objects.filter(id=obj.id)
        if adminuser.exists():
            return adminuser.first().responsible_institution
        elif professoruser.exists():
            return professoruser.first().workplace
        elif studentuser.exists():
            return studentuser.first().student_classroom.institution
        else:
            return 'Undefined'
    get_profile.short_description = 'Institution'

    def get_list_display(self, request):
        if '/usermanager/adminuser/' in request.path:
            return ('username', 'profile', 'get_group_list', 'get_profile', 'created_by', 'is_superuser', 'is_staff', 'responsible_institution', 'email', 'first_name', 'last_name', 'date_joined')
        if '/usermanager/professoruser/' in request.path:
            return ('username', 'profile', 'get_group_list', 'get_profile', 'created_by', 'is_superuser', 'is_staff', 'workplace', 'email', 'first_name', 'last_name', 'date_joined')
        if '/usermanager/studentuser/' in request.path:
            return ('username', 'profile', 'get_group_list', 'get_profile', 'created_by', 'is_superuser', 'is_staff', 'student_classroom', 'email', 'first_name', 'last_name', 'date_joined')
        else:
            return ['username', 'profile', 'get_group_list', 'get_profile', 'created_by', 'is_superuser', 'is_staff', 'email', 'first_name', 'last_name', 'date_joined']

    def get_search_fields(self, request: HttpRequest) -> list[str]:
        if '/usermanager/adminuser/' in request.path:
            return ['username', 'email', 'first_name', 'last_name', 'profile', 'created_by__username', 'responsible_institution__name']
        if '/usermanager/professoruser/' in request.path:
            return ['username', 'email', 'first_name', 'last_name', 'profile', 'created_by__username', 'workplace__name']
        if '/usermanager/studentuser/' in request.path:
            return ['username', 'email', 'first_name', 'last_name', 'profile', 'created_by__username', 'student_classroom__institution__name']
        else:
            return ['username', 'email', 'first_name', 'last_name', 'profile', 'created_by__username']

    def save_model(self, request, obj: User, form, change):        
        if not obj.created_by_id:
            obj.created_by = request.user
        
        if request.user.profile == User.ProfileChoices.ADMIN:
            user = AdminUser.objects.filter(id=request.user.id).first()
            if '/usermanager/adminuser/add/' in request.path:
                obj.responsible_institution = user.responsible_institution            
            if '/usermanager/professoruser/add/' in request.path:
                obj.workplace = user.responsible_institution
        super().save_model(request, obj, form, change)

        if request.user.profile == User.ProfileChoices.ADMIN:
            if '/usermanager/adminuser/add/' in request.path:
                obj.groups.clear()
                default_group, created = Group.objects.get_or_create(name='Admin')
                obj.groups.add(default_group)

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        qs = super().get_queryset(request)
        if request.user.profile == User.ProfileChoices.ROOT:
            return qs        
        elif request.user.profile == User.ProfileChoices.ADMIN:
            user = AdminUser.objects.filter(id=request.user.id).first()
            if '/adminuser/' in request.path:
                if request.user.groups.filter(name='Admin'):
                    return qs.filter(id=user.id)
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
    
    def formfield_for_foreignkey(self, db_field: ForeignKey[Any], request: HttpRequest | None, **kwargs: Any) -> forms.ModelChoiceField | None:
        if db_field.name == "student_classroom":
            from goldlistmethod.models import ClassRoom
            if request.user.profile == User.ProfileChoices.ROOT:
                pass
            elif request.user.profile == User.ProfileChoices.ADMIN:
                adminuser = AdminUser.objects.filter(id=request.user.id).first()
                qs_classroom = ClassRoom.objects.filter(institution=adminuser.responsible_institution)
                kwargs["queryset"] = qs_classroom.order_by('name', 'room_number')
            elif request.user.profile == User.ProfileChoices.PROFESSOR:
                professoruser = ProfessorUser.objects.filter(id=request.user.id).first()
                qs_classroom = ClassRoom.objects.filter(professor=professoruser)
                kwargs["queryset"] = qs_classroom.order_by('name', 'room_number')            
        
        if db_field.name == "responsible_institution":
            if request.user.profile == User.ProfileChoices.ROOT:
                from goldlistmethod.models import Institution
                kwargs["queryset"] = Institution.objects.all()
        if db_field.name == "workplace":
            if request.user.profile == User.ProfileChoices.ROOT:
                from goldlistmethod.models import Institution
                kwargs["queryset"] = Institution.objects.all()
        if db_field.name == "student_classroom":
            if request.user.profile == User.ProfileChoices.ROOT:
                from goldlistmethod.models import ClassRoom
                kwargs["queryset"] = ClassRoom.objects.all()
        
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

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
                    class CustomUserCreationForm(UserCreationForm):
                        class Meta(UserCreationForm.Meta):
                            model = StudentUser
                            fields = UserCreationForm.Meta.fields + ('student_classroom',)
                    form = CustomUserCreationForm
                elif 'usermanager/adminuser/add/' in request.path:
                    class CustomUserCreationForm(UserCreationForm):
                        class Meta(UserCreationForm.Meta):
                            model = AdminUser
                            fields = UserCreationForm.Meta.fields + ('responsible_institution',)
                    form = CustomUserCreationForm
                elif 'usermanager/professoruser/add/' in request.path:
                    class CustomUserCreationForm(UserCreationForm):
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
                    # from goldlistmethod.models import ClassRoom
                    # qs_classroom = ClassRoom.objects.filter(institution=user.responsible_institution)
                    class CustomUserCreationForm(UserCreationForm):
                        # student_classroom = forms.ModelChoiceField(queryset=qs_classroom, required=True)                        
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
                        if not request.user.groups.filter(name='RootAdmin').exists():
                            self.fields['is_active'].disabled = True
                            self.fields['is_staff'].disabled = True
                        if '/usermanager/adminuser/' in request.path:
                            self.fields['responsible_institution'].disabled = True
                        if '/usermanager/professoruser/' in request.path:
                            self.fields['workplace'].disabled = True
                form = Form
        
        elif request.user.profile == User.ProfileChoices.PROFESSOR:
            if '/add/' in request.path:
                if 'usermanager/studentuser/add/' in request.path:
                    class CustomUserCreationForm(UserCreationForm):
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
                        if not request.user.groups.filter(name='RootAdmin').exists():
                            self.fields['is_active'].disabled = True
                            self.fields['is_staff'].disabled = True
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
                    if not request.user.groups.filter(name='RootAdmin').exists():
                            self.fields['is_active'].disabled = True
                            self.fields['is_staff'].disabled = True
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
