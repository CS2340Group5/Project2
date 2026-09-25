from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *
from .forms import *

# Register your models here.

class CustomUserAdmin(UserAdmin):
    model = GenericUser
    list_display = ["email","first_name","last_name", "role", 'is_active']
    list_filter = ['role', 'is_active']
    ordering=["first_name"]
    search_fields=["first_name", "last_name", "email"]

    #Edit
    form = GenericUserChangeForm
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ("Personal Info", {'fields': ('first_name', 'last_name', 'email'),
                           'classes': ["collapse in"]}),
        ("Permissions & Roles", {
            'description': "<strong>User roles:</strong> \
            <br><strong>Applicant:</strong> Basic user \
            <br><strong>Recruiter:</strong> Can post jobs, search for applicants\
            <br><strong>Admin:</strong> Admin access to website",
            'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            "classes": ["collapse"]}),
        ("Important Dates", {'fields': ('last_login', 'date_joined'),
                             'classes':["collapse"]})
    )

    #Create
    add_form = GenericUserCreationForm
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Role', {
                'fields': ('role',),
                'description': "User account role"}),
    )

admin.site.register(GenericUser, CustomUserAdmin)
admin.site.register(ExperienceType)
admin.site.register(School)
#Uncomment to access SocialLink objects from admin pannel (not neccesary)
#admin.site.register(SocialLink)