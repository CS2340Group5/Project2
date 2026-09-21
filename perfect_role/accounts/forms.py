from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.forms.utils import ErrorList
from django.utils.safestring import mark_safe
from .models import *

class GenericUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = GenericUser
        fields = UserCreationForm.Meta.fields + ('role', 'education', 'experience', 'headline')

class GenericUserChangeForm(UserChangeForm):
    class Meta:
        model = GenericUser
        fields = '__all__'

class CustomErrorList(ErrorList):
    def __str__(self):
        if not self:
            return ''
        return mark_safe(''.join([f'<div class="alert alert-danger" role="alert">{e}</div>' for e in self]))

class CustomUserCreationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
        for fieldname in ['username', 'role', 'password1', 'password2']:
            if fieldname in self.fields:
                self.fields[fieldname].help_text = None
                self.fields[fieldname].widget.attrs.update({'class': 'form-control'})

    class Meta(UserCreationForm.Meta):
        model = GenericUser
        fields = ('username', 'role')