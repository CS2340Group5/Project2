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
        fields = UserCreationForm.Meta.fields + ('email', 'role',)

    ROLE_CHOICES = [
        ("APPLICANT", "Applicant"),
        ('RECRUITER', 'Recruiter')
    ]

    email = forms.EmailField(required=False, label="Email")
    
    role = forms.ChoiceField(
        choices=ROLE_CHOICES, 
        widget=forms.RadioSelect, 
        label="I am an:"
    )
    
    def __init__(self, *args, **kwargs):
        super(GenericUserCreationForm, self).__init__(*args, **kwargs)
        for fieldname in ['username', 'email', 'password1', 'password2']:
            self.fields[fieldname].help_text = None
            self.fields[fieldname].widget.attrs.update({'class': 'form-control'})

    def clean(self):
        cleaned_input = super().clean()
        role = cleaned_input.get('role')
        email = cleaned_input.get('email', '').lower()

        if role == GenericUser.Role.RECRUITER:
            cleaned_input['email'] = ''
        elif role == GenericUser.Role.APPLICANT:
            if not email:
                self.add_error('email', "Applicants must provide an email.")
            elif GenericUser.objects.filter(email=email).exists():
                self.add_error('email', "An account is already using this email.")
            else:
                cleaned_input['email'] = email

        return cleaned_input

class ProfileForm(forms.ModelForm):
    class Meta:
        model = GenericUser
        fields = ('email', 'headline', 'location', 'commute_radius')
        labels = {'commute_radius': 'Preferred commute radius (miles)'}

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        if self.instance.role == GenericUser.Role.APPLICANT:
            self.fields['email'].required = True
        else:
            del self.fields['email']
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

    def clean(self):
        cleaned_input = super().clean()
        email = cleaned_input.get('email')

        if email:
            email = email.lower()
            if GenericUser.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
                self.add_error('email', "An account is already using this email.")
            else:
                cleaned_input['email'] = email
                
        return cleaned_input

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

class WorkExperienceForm(forms.ModelForm):
    class Meta:
        model = WorkExperience
        fields = ('company', 'description')

    def __init__(self, *args, **kwargs):
        super(WorkExperienceForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

class EducationForm(forms.ModelForm):
    class Meta:
        model = Education
        fields = ('degree', 'description')

    def __init__(self, *args, **kwargs):
        super(EducationForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
