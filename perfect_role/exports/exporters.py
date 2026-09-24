import csv
import io
import zipfile
from datetime import datetime, timedelta

from django.conf import settings
from django.db.models import Avg, Count
from django.http import HttpResponse
from django.utils import timezone

from accounts.models import GenericUser
from posts.models import JobPost, Skill


# Spreadsheet apps (Excel, Sheets) treat a cell starting with one of these
# characters as a formula. Since users type their own headlines, job titles,
# etc., we escape them so an export can never run a formula ("CSV injection").
FORMULA_PREFIXES = ('=', '+', '-', '@', '\t', '\r')


def sanitize_cell(value):
    """Convert a Python value into a safe, readable CSV cell."""
    if value is None:
        return ''
    if isinstance(value, bool):
        return 'Yes' if value else 'No'
    if isinstance(value, datetime):
        if timezone.is_aware(value):
            value = timezone.localtime(value)
        return value.strftime('%Y-%m-%d %H:%M:%S')
    if isinstance(value, str) and value.startswith(FORMULA_PREFIXES):
        return "'" + value
    return value


class CsvExporter:
    """Base class: describes one downloadable CSV dataset."""
    slug = ''          # used in the download URL: /exports/<slug>/
    title = ''         # shown on the Export Data page
    description = ''   # shown on the Export Data page
    headers = []       # first row of the CSV
    model = None       # model this exporter handles in the Django admin (optional)

    def rows(self, queryset=None):
        """Yield one list of values per CSV row (excluding the header)."""
        raise NotImplementedError

    def count(self):
        """Number of data rows the export will contain."""
        raise NotImplementedError

    def filename(self):
        return f'perfect_role_{self.slug}_{timezone.localdate():%Y-%m-%d}.csv'

    def write_csv(self, file_obj, queryset=None):
        writer = csv.writer(file_obj)
        writer.writerow(self.headers)
        for row in self.rows(queryset):
            writer.writerow([sanitize_cell(value) for value in row])

    def as_response(self, queryset=None):
        """Return an HttpResponse that downloads this export as a .csv file."""
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="{self.filename()}"'
        # Byte-order mark so Excel opens the file as UTF-8 (names with accents, etc.)
        response.write('﻿')
        self.write_csv(response, queryset)
        return response

    def as_text(self):
        buffer = io.StringIO()
        buffer.write('﻿')
        self.write_csv(buffer)
        return buffer.getvalue()


class QuerysetExporter(CsvExporter):
    """Exporter backed by a model: one CSV row per database object."""

    def get_queryset(self):
        raise NotImplementedError

    def to_row(self, obj):
        raise NotImplementedError

    def rows(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        for obj in queryset:
            yield self.to_row(obj)

    def count(self):
        return self.get_queryset().count()


class UserExporter(QuerysetExporter):
    slug = 'users'
    title = 'Users'
    description = ('Every account on the platform with its role, status, sign-up '
                   'and last-login dates, and profile details. Passwords are never exported.')
    model = GenericUser
    headers = [
        'User ID', 'Username', 'Email', 'First Name', 'Last Name', 'Role',
        'Active', 'Staff', 'Superuser', 'Date Joined', 'Last Login',
        'Headline', 'Education', 'Experience', 'Social Links',
    ]

    def get_queryset(self):
        return GenericUser.objects.prefetch_related('sociallinks').order_by('date_joined')

    def to_row(self, user):
        links = '; '.join(f'{link.title}: {link.url}' for link in user.sociallinks.all())
        return [
            user.id, user.username, user.email, user.first_name, user.last_name,
            user.get_role_display(), user.is_active, user.is_staff, user.is_superuser,
            user.date_joined, user.last_login,
            user.headline, user.education, user.experience, links,
        ]


class JobPostExporter(QuerysetExporter):
    slug = 'job-posts'
    title = 'Job Posts'
    description = 'All job postings with position, required skills, salary, location, remote and visa options.'
    model = JobPost
    headers = [
        'Job ID', 'Title', 'Position', 'Skills', 'Minimum Salary',
        'Remote', 'Visa Sponsorship', 'Location (ZIP)',
    ]

    def get_queryset(self):
        return JobPost.objects.prefetch_related('skills').order_by('id')

    def to_row(self, job):
        skills = '; '.join(sorted(skill.name for skill in job.skills.all()))
        return [
            job.id, job.name, job.position, skills, job.salary_min,
            job.is_remote, job.visa_sponsorship, job.location,
        ]


class SkillDemandExporter(QuerysetExporter):
    slug = 'skills'
    title = 'Skill Demand'
    description = 'Each skill and how many job posts require it, most in-demand first.'
    model = Skill
    headers = ['Skill', 'Job Posts Requiring Skill']

    def get_queryset(self):
        return (Skill.objects
                .annotate(job_post_count=Count('jobpost'))
                .order_by('-job_post_count', 'name'))

    def to_row(self, skill):
        return [skill.name, skill.job_post_count]


class UsageSummaryExporter(CsvExporter):
    slug = 'usage-summary'
    title = 'Usage Summary'
    description = 'Headline platform metrics: users by role, sign-ups, recent logins and job post totals.'
    headers = ['Metric', 'Value']

    def metrics(self):
        now = timezone.now()
        last_7_days = now - timedelta(days=7)
        last_30_days = now - timedelta(days=30)
        users = GenericUser.objects.all()
        jobs = JobPost.objects.all()

        rows = [[f'Report generated ({settings.TIME_ZONE})', now]]
        rows.append(['Total users', users.count()])
        for value, label in GenericUser.Role.choices:
            rows.append([f'Users with role: {label}', users.filter(role=value).count()])
        rows += [
            ['Active accounts', users.filter(is_active=True).count()],
            ['New users (last 7 days)', users.filter(date_joined__gte=last_7_days).count()],
            ['New users (last 30 days)', users.filter(date_joined__gte=last_30_days).count()],
            ['Users who logged in (last 30 days)', users.filter(last_login__gte=last_30_days).count()],
            ['Total job posts', jobs.count()],
            ['Remote job posts', jobs.filter(is_remote=True).count()],
            ['Job posts offering visa sponsorship', jobs.filter(visa_sponsorship=True).count()],
        ]
        average_salary = jobs.aggregate(avg=Avg('salary_min'))['avg']
        rows.append(['Average minimum salary',
                     round(average_salary, 2) if average_salary is not None else None])
        rows.append(['Skills in catalog', Skill.objects.count()])
        return rows

    def rows(self, queryset=None):
        return self.metrics()

    def count(self):
        return len(self.metrics())


# Registry of every available export, keyed by URL slug (order = order on the page).
EXPORTERS = {
    exporter.slug: exporter
    for exporter in [
        UsageSummaryExporter(),
        UserExporter(),
        JobPostExporter(),
        SkillDemandExporter(),
    ]
}


def get_exporter_for_model(model):
    """Return the exporter responsible for a model (used by the admin action)."""
    for exporter in EXPORTERS.values():
        if exporter.model is model:
            return exporter
    return None


def all_exports_zip_response():
    """Return a single .zip download containing every export."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as archive:
        for exporter in EXPORTERS.values():
            archive.writestr(exporter.filename(), exporter.as_text().encode('utf-8'))
    response = HttpResponse(buffer.getvalue(), content_type='application/zip')
    response['Content-Disposition'] = (
        f'attachment; filename="perfect_role_exports_{timezone.localdate():%Y-%m-%d}.zip"'
    )
    return response