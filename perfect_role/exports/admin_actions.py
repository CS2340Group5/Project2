from django.contrib import admin, messages
from .exporters import get_exporter_for_model

@admin.action(description='Export selected to CSV')
def export_selected_as_csv(modeladmin, request, queryset):
    exporter = get_exporter_for_model(queryset.model)
    if exporter is None:
        modeladmin.message_user(request, 'CSV export not available',
                                level=messages.ERROR)
        return None
    return exporter.as_response(queryset)