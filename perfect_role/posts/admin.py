from django.contrib import admin
from .models import Skill, JobPost, Application

class JobPostAdmin(admin.ModelAdmin):
    model = JobPost
    list_display = ["name", "recruiter", "position", "location"]
    list_filter = ["salary_min", "is_remote", "visa_sponsorship"]
    ordering=["name"]
    search_fields=["name", "recruiter", "position"]

admin.site.register(Skill)
admin.site.register(JobPost, JobPostAdmin)
admin.site.register(Application)