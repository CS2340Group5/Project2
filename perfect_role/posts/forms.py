from django import forms
from django.forms.utils import ErrorList
from django.utils.safestring import mark_safe
from .models import JobPost

class CustomErrorList(ErrorList):
    def __str__(self):
        if not self:
            return ''
        return mark_safe(''.join([f'<div class="alert alert-danger" role="alert">{e}</div>' for e in self]))

class JobPostForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('error_class', CustomErrorList)
        super(JobPostForm, self).__init__(*args, **kwargs)
        for fieldname in ['name', 'position', 'skills', 'salary_min', 'location']:
            self.fields[fieldname].help_text = None
            self.fields[fieldname].widget.attrs.update({'class': 'form-control'})

        for fieldname in ['is_remote', 'visa_sponsorship']:
            self.fields[fieldname].help_text = None
            self.fields[fieldname].widget.attrs.update({'class': 'form-check-input'})

    class Meta:
        model = JobPost
        fields = [
            'name',
            'position',
            'skills',
            'salary_min',
            'location',
            'is_remote',
            'visa_sponsorship',
        ]
        labels = {
            'name': 'Job Title',
            'salary_min': 'Minimum Salary',
            'is_remote': 'Remote Position',
            'visa_sponsorship': 'Visa Sponsorship Available',
        }