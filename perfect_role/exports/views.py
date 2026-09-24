from django.http import Http404
from django.shortcuts import render

from .exporters import EXPORTERS, all_exports_zip_response
from .permissions import admin_required


@admin_required
def index(request):
    template_data = {
        'title': 'Export Data',
        'exports': [
            {'exporter': exporter, 'row_count': exporter.count()}
            for exporter in EXPORTERS.values()
        ],
    }
    return render(request, 'exports/index.html', {'template_data': template_data})


@admin_required
def download(request, slug):
    exporter = EXPORTERS.get(slug)
    if exporter is None:
        raise Http404('Unknown export.')
    return exporter.as_response()


@admin_required
def download_all(request):
    return all_exports_zip_response()
# Create your views here.
