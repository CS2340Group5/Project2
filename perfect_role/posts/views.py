from django.shortcuts import render
from .models import JobPost, Skill, Bookmark, Application
from .forms import JobPostForm, CustomErrorList
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Count

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
        postings = postings.filter(position__icontains=position)
    if salary_min:
        postings = postings.filter(salary_min__gte=salary_min)
    if remote:
        postings = postings.filter(is_remote=True)
    if visa:
        postings = postings.filter(visa_sponsorship=True)
    if location:
        postings = postings.filter(location=location)

    template_data = {}
    template_data['bookmarks'] = []
    template_data['applied'] = []
    if request.user.is_authenticated:
        template_data['bookmarks'] = [bookmark.post.id for bookmark in Bookmark.objects.filter(user=request.user)]
        template_data['applied'] = [application.post.id for application in Application.objects.filter(user=request.user)]
    template_data['postings'] = postings
    template_data['skills'] = Skill.objects.all()
    return render(request, 'posts/index.html', {'template_data': template_data})

@login_required
def bookmarktoggle(request, id):
    post = JobPost.objects.get(id=id)
    bookmarkCheck = Bookmark.objects.filter(user=request.user, post=post)

    if len(bookmarkCheck) == 0:
        Bookmark.objects.create(user=request.user, post=post)
    else:
        bookmarkCheck.delete()

    return redirect(request.META.get('HTTP_REFERER', 'posts.index'))

@login_required
def viewbookmarks(request):
    bookmarks = Bookmark.objects.filter(user=request.user)
    template_data = {}
    template_data['bookmarks'] = [bookmark.post for bookmark in bookmarks]
    template_data['applied'] = [application.post.id for application in Application.objects.filter(user=request.user)]

    return render(request, 'posts/bookmarks.html', {'template_data': template_data})

@login_required
def submitapplication(request, id):
    post = JobPost.objects.get(id=id)
    bookmarkCheck = Bookmark.objects.filter(user=request.user, post=post)

    if request.method == 'POST':
        if len(bookmarkCheck) != 0:
            bookmarkCheck.delete()
        note = request.POST.get('note')
        Application.objects.create(user=request.user, post=post, note=note)

    return redirect(request.META.get('HTTP_REFERER', 'posts.index'))

@login_required
def applications(request): 
    applied = Application.objects.filter(user=request.user)
    template_data = {}
    template_data['applications'] = applied

    return render(request, 'posts/applications.html', {'template_data': template_data})

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
            job_post = form.save(commit=False)
            job_post.recruiter = request.user
            job_post.save()
            form.save_m2m()
            
            return redirect('home.index')
        else:
            template_data['form'] = form
            return render(request, 'posts/postjob.html', {'template_data': template_data})

@login_required
def viewjobs(request):
    template_data = JobPost.objects.filter(recruiter=request.user)
    
    return render(request, 'posts/viewjobs.html', {'template_data': template_data})

@login_required
def editjob(request, id):
    post = JobPost.objects.get(pk=id)
    if request.user != post.recruiter:
        return redirect('home.index')
    template_data = {}
    template_data['title'] = "Edit Job"
    template_data['id'] = id
    
    if request.method == 'GET':
        template_data['form'] = JobPostForm(instance=post)
        return render(request, 'posts/editjob.html', {'template_data': template_data})
    elif request.method == 'POST':
        form = JobPostForm(request.POST, error_class=CustomErrorList, instance=post)
        if form.is_valid():
            form.save()
            return redirect('posts.viewjobs')
        else:
            template_data['form'] = form
            return render(request, 'posts/editjob.html', {'template_data': template_data})

@login_required
def recommended(request):
    my_skills = request.user.skills.all()
    postings = JobPost.objects.filter(skills__in=my_skills).annotate(
        matches=Count('skills')).order_by('-matches')
    template_data = {'title': 'Recommended Jobs'}
    template_data['postings'] = postings
    template_data['has_skills'] = my_skills.exists()
    return render(request, 'posts/recommended.html', {'template_data': template_data})

@login_required
def pipeline(request, id):
    post = get_object_or_404(JobPost, pk=id)
    if request.user != post.recruiter:
        return redirect('home.index')
    template_data = {'title': 'Applicant Pipeline'}
    template_data['post'] = post
    template_data['stages'] = Application.Status.choices
    template_data['applications'] = Application.objects.filter(post=post)
    return render(request, 'posts/pipeline.html', {'template_data': template_data})

@login_required
def move_application(request, id):
    application = get_object_or_404(Application, pk=id)
    if request.user != application.post.recruiter:
        return redirect('home.index')
    if request.method == 'POST' and request.POST.get('status') in Application.Status.values:
        application.status = request.POST['status']
        application.save()
    return redirect('posts.pipeline', id=application.post.id)

@login_required
def viewpostapplications(request, id):
    post = get_object_or_404(JobPost, pk=id)
    if request.user != post.recruiter:
        return redirect('home.index')
    
    if request.method == 'POST':
        application_id = request.POST.get('application_id')
        new_status = request.POST.get('status')
        application = get_object_or_404(Application, pk=application_id, post=post)
        application.status = new_status
        application.save()
        
        return redirect('posts.view_post_applications', id=post.id)
    
    template_data = {}
    template_data['applications'] = Application.objects.filter(post=post)
    return render(request, 'posts/viewpostapplications.html', {'template_data': template_data})
    