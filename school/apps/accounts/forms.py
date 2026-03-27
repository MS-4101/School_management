from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser, Role, Permission, School


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'Username', 'autofocus': True
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control', 'placeholder': 'Password'
    }))


class RegisterForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name', 'phone',
                  'department', 'student_id', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label


class UserEditForm(forms.ModelForm):
    roles = forms.ModelMultipleChoiceField(
        queryset=Role.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'checkbox-list'}),
        required=False
    )

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'phone', 'address',
                  'department', 'student_id', 'profile_image', 'role',
                  'whatsapp_number', 'roles', 'is_active']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name not in ('roles', 'is_active', 'profile_image'):
                field.widget.attrs['class'] = 'form-control'


class ProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'phone', 'address',
                  'department', 'student_id', 'profile_image', 'whatsapp_number']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name != 'profile_image':
                field.widget.attrs['class'] = 'form-control'


class RoleForm(forms.ModelForm):
    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'checkbox-list'}),
        required=False
    )

    class Meta:
        model = Role
        fields = ['name', 'description', 'permissions']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Role Name'})
        self.fields['description'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Description', 'rows': 3})


class PermissionForm(forms.ModelForm):
    class Meta:
        model = Permission
        fields = ['name', 'codename', 'description']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label


class UserCreateForm(UserCreationForm):
    """Form for creating a new user with role assignment."""
    roles = forms.ModelMultipleChoiceField(
        queryset=Role.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='Assign Roles',
        help_text='Select one or more predefined roles for this user.'
    )

    class Meta:
        model = CustomUser
        fields = [
            'first_name', 'last_name', 'username', 'email',
            'phone', 'department', 'whatsapp_number',
            'password1', 'password2', 'is_active', 'roles',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        exclude_class = ('roles', 'is_active')
        for field_name, field in self.fields.items():
            if field_name not in exclude_class:
                field.widget.attrs.update({'class': 'form-control'})
                field.widget.attrs.setdefault('placeholder', field.label or field_name.replace('_', ' ').title())

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            roles = self.cleaned_data.get('roles')
            if roles:
                user.roles.set(roles)
        return user


class SchoolCreateForm(forms.ModelForm):
    """Form for creating a new School tenant."""

    class Meta:
        model = School
        fields = [
            'name', 'address', 'city', 'state', 'pincode',
            'phone', 'email', 'admin_user', 'logo',
            'school_start_time', 'school_end_time', 'is_active',
        ]
        widgets = {
            'school_start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'school_end_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        exclude_class = ('logo', 'is_active', 'school_start_time', 'school_end_time')
        for field_name, field in self.fields.items():
            if field_name not in exclude_class:
                field.widget.attrs.update({'class': 'form-control'})
