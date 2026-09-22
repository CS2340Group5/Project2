from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.forms.utils import ErrorList
from django.utils.safestring import mark_safe
from .models import *

class GenericUserChangeForm(UserChangeForm):
    class Meta:
        model = GenericUser
        fields = '__all__'

class CustomErrorList(ErrorList):
    def __str__(self):
        if not self:
            return ''
        return mark_safe(''.join([f'<div class="alert alert-danger" role="alert">{e}</div>' for e in self]))

class GenericUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = GenericUser
        fields = UserCreationForm.Meta.fields + ('role', 'education', 'experience', 'headline')

    ROLE_CHOICES = [
        ("APPLICANT", "Applicant"),
        ('RECRUITER', 'Recruiter')
    ]
    
    role = forms.ChoiceField(
        choices=ROLE_CHOICES, 
        widget=forms.RadioSelect, 
        label="I am an:"
    )
    
    def __init__(self, *args, **kwargs):
        super(GenericUserCreationForm, self).__init__(*args, **kwargs)
        for fieldname in ['username', 'password1', 'password2']:
            self.fields[fieldname].help_text = None
            self.fields[fieldname].widget.attrs.update({'class': 'form-control'})
