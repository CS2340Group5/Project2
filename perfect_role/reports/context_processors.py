from .models import Report


def reports(request):
    data = {'report_reasons': Report.Reason.choices}
    user = getattr(request, 'user', None)
    if user is not None and user.is_authenticated and (user.is_superuser or user.role == 'ADMIN'):
        data['open_report_count'] = Report.objects.filter(status__in=Report.OPEN_STATUSES).count()
    return data
