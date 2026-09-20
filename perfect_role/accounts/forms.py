from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import *

class GenericUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = GenericUser
        fields = UserCreationForm.Meta.fields + ('role', 'education', 'experience', 'headline')

class GenericUserChangeForm(UserChangeForm):
    class Meta:
        model = GenericUser
        fields = '__all__'