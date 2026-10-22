from django.contrib import admin
from .models import Report


class ReportAdmin(admin.ModelAdmin):
    model = Report
    list_display = ["target_summary", "target_type", "reason", "reporter", "status", "action_taken", "created_at"]
    list_filter = ["status", "target_type", "reason", "action_taken"]
    ordering = ["-created_at"]
    search_fields = ["target_summary", "details", "reporter__username", "reported_user__username"]
    readonly_fields = ["created_at", "reviewed_at"]


admin.site.register(Report, ReportAdmin)
