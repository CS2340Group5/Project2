from django.contrib import admin
from .models import Skill, JobPost, Application

admin.site.register(Skill)
admin.site.register(JobPost)
admin.site.register(Application)