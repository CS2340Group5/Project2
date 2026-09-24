import csv
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from accounts.models import GenericUser
from posts.models import JobPost

def is_admin(user):
    return user.is_superuser or user.role == 'ADMIN'

@login_required
def index(request):
    if not is_admin(request.user):
        return HttpResponseForbidden('Only administrators can export data.')
    template_data = {'title': 'Export Data'}
    template_data['user_count'] = GenericUser.objects.count()
    template_data['job_count'] = JobPost.objects.count()
    return render(request, 'exports/index.html', {'template_data': template_data})

@login_required
def users_csv(request):
    if not is_admin(request.user):
        return HttpResponseForbidden('Only administrators can export data.')
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="users.csv"'
    writer = csv.writer(response)
    writer.writerow(['Username', 'Email', 'Role', 'Date Joined', 'Headline', 'Skills'])
    for user in GenericUser.objects.all():
        skills = ', '.join(s.name for s in user.skills.all())
        writer.writerow([user.username, user.email, user.role, user.date_joined.date(), user.headline, skills])
    return response

@login_required
def jobs_csv(request):
    if not is_admin(request.user):
        return HttpResponseForbidden('Only administrators can export data.')
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="job_posts.csv"'
    writer = csv.writer(response)
    writer.writerow(['Title', 'Position', 'Recruiter', 'Skills', 'Minimum Salary', 'Location', 'Remote', 'Visa Sponsorship'])
    for job in JobPost.objects.all():
        recruiter = job.recruiter.username if job.recruiter else ''
        writer.writerow([job.name, job.position, recruiter, job.skills_toString(), job.salary_min, job.location, job.is_remote, job.visa_sponsorship])
    return response
