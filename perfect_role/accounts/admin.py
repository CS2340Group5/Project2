from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

# Register your models here.

class CustomUserAdmin(UserAdmin):
    model = GenericUser
    list_display = ["email","first_name","last_name", "role"]
    ordering=["first_name"]
    search_fields=["first_name","last_name", "email", "id"]

admin.site.register(GenericUser, CustomUserAdmin)