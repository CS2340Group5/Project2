from django.shortcuts import render
from .models import JobPost, Position, Skill
from .forms import JobPostForm, CustomErrorList
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

def index(request):
    postings = JobPost.objects.all()
    search = request.GET.get('search')
    skills = request.GET.getlist('skills')
    position = request.GET.get('position')
    salary_min = request.GET.get('salary')
    remote = request.GET.get('remote')
    visa = request.GET.get('visa')
    location = request.GET.get('zip')


    if search:
        postings = postings.filter(name__icontains=search)
    if skills:
        postings = postings.filter(skills__name__in=skills).distinct()
    if position:
        postings = postings.filter(position__name=position)
    if salary_min:
        postings = postings.filter(salary_min__gte=salary_min)
    if remote:
        postings = postings.filter(is_remote=True)
    if visa:
        postings = postings.filter(visa_sponsorship=True)
    if location:
        postings = postings.filter(location=location)

    template_data = {}
    template_data['postings'] = postings
    template_data['positions'] = Position.objects.all()
    template_data['skills'] = Skill.objects.all()
    return render(request, 'posts/index.html', {'template_data': template_data})

@login_required
def postjobs(request):
    if request.user.role != 'RECRUITER':
        return HttpResponseForbidden("Only recruiters can post jobs.")

    template_data = {'title': 'Post a Job'}

    if request.method == 'GET':
        template_data['form'] = JobPostForm()
        return render(request, 'posts/postjob.html', {'template_data': template_data})

    elif request.method == 'POST':
        form = JobPostForm(request.POST, error_class=CustomErrorList)
        if form.is_valid():
            form.save()
            return redirect('home.index')
        else:
            template_data['form'] = form
            return render(request, 'posts/postjob.html', {'template_data': template_data})