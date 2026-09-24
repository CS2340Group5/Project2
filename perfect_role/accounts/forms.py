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
        fields = UserCreationForm.Meta.fields + ('role',)

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

class ProfileForm(forms.ModelForm):
    class Meta:
        model = GenericUser
        fields = ('headline', 'education', 'experience')
        labels = {'experience': 'Work experience'}

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

class SocialLinkForm(forms.ModelForm):
    class Meta:
        model = SocialLink
        fields = ('title', 'url')

    def __init__(self, *args, **kwargs):
        super(SocialLinkForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

class PrivacyForm(forms.ModelForm):
    class Meta:
        model = GenericUser
        fields = ('is_public', 'show_education', 'show_experience', 'show_links')
        labels = {
            'is_public': 'Profile visible to recruiters',
            'show_education': 'Show education',
            'show_experience': 'Show work experience',
            'show_links': 'Show links',
        }

    def __init__(self, *args, **kwargs):
        super(PrivacyForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-check-input'})
