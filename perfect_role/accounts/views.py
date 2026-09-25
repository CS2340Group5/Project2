from .forms import GenericUserCreationForm, CustomErrorList, ProfileForm, SocialLinkForm, PrivacyForm
from .models import SocialLink, GenericUser
from posts.models import Skill
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth import login as auth_login, authenticate, logout as auth_logout
from django.contrib.auth.decorators import login_required


def signup(request):
    template_data = {}
    template_data['title'] = 'Sign Up'
    if request.method == 'GET':
        template_data['form'] = GenericUserCreationForm()
        return render(request, 'accounts/signup.html', {'template_data': template_data})
    elif request.method == "POST":
        form = GenericUserCreationForm(request.POST, error_class=CustomErrorList)
        if form.is_valid():
            form.save()
            return redirect('accounts.login')
        else:
            template_data['form'] = form
            return render(request, 'accounts/signup.html', {'template_data': template_data})

def login(request):
    template_data = {}
    template_data['title'] = 'Login'
    if request.method == 'GET':
        return render(request, 'accounts/login.html',
            {'template_data': template_data})
    elif request.method == 'POST':
        user = authenticate(request, username = request.POST['username'], password = request.POST['password'])
        if user is None:
            template_data['error'] = 'The username or password is incorrect.'
            return render(request, 'accounts/login.html',
                {'template_data': template_data})
        else:
            auth_login(request, user)
            return redirect('home.index')

@login_required
def logout(request):
    auth_logout(request)
    return redirect('home.index')

@login_required
def profile(request, id=None):
    if id is None:
        profile_user = request.user
    else:
        profile_user = get_object_or_404(GenericUser, id=id)
    template_data = {}
    template_data['title'] = 'Profile'
    template_data['profile_user'] = profile_user
    template_data['links'] = profile_user.sociallinks.all()
    template_data['is_owner'] = profile_user == request.user
    return render(request, 'accounts/profile.html', {'template_data': template_data})

@login_required
def edit_profile(request):
    template_data = {}
    template_data['title'] = 'Edit Profile'
    if request.method == 'GET':
        template_data['form'] = ProfileForm(instance=request.user)
        template_data['link_form'] = SocialLinkForm()
        template_data['links'] = request.user.sociallinks.all()
        template_data['all_skills'] = Skill.objects.all()
        return render(request, 'accounts/edit_profile.html', {'template_data': template_data})
    elif request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user, error_class=CustomErrorList)
        if form.is_valid():
            form.save()
            return redirect('accounts.profile')
        else:
            template_data['form'] = form
            template_data['link_form'] = SocialLinkForm()
            template_data['links'] = request.user.sociallinks.all()
            template_data['all_skills'] = Skill.objects.all()
            return render(request, 'accounts/edit_profile.html', {'template_data': template_data})

@login_required
def add_link(request):
    if request.method == 'POST':
        form = SocialLinkForm(request.POST)
        if form.is_valid():
            link = form.save(commit=False)
            link.user = request.user
            link.save()
    return redirect(reverse('accounts.edit_profile') + '#links')

@login_required
def delete_link(request, id):
    link = get_object_or_404(SocialLink, id=id, user=request.user)
    link.delete()
    return redirect(reverse('accounts.edit_profile') + '#links')

@login_required
def privacy(request):
    template_data = {}
    template_data['title'] = 'Privacy Settings'
    if request.method == 'GET':
        template_data['form'] = PrivacyForm(instance=request.user)
        return render(request, 'accounts/privacy.html', {'template_data': template_data})
    elif request.method == 'POST':
        form = PrivacyForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
        return redirect('accounts.profile')

@login_required
def add_skill(request):
    name = request.POST.get('name', '').strip()
    if name:
        skill = Skill.objects.filter(name__iexact=name).first()
        if skill is None:
            skill = Skill.objects.create(name=name)
        request.user.skills.add(skill)
    return redirect(reverse('accounts.edit_profile') + '#skills')

@login_required
def remove_skill(request, id):
    skill = get_object_or_404(Skill, id=id)
    request.user.skills.remove(skill)
    return redirect(reverse('accounts.edit_profile') + '#skills')

@login_required
def candidatesearch(request):
    candidates = GenericUser.objects.filter(role='APPLICANT', is_public="True")
    skills = request.GET.getlist('skills')
    # location = request.GET.get('zip')
    workexp = request.GET.get('workexp')
    
    # ----WAITING FOR LOCATION IMPLEMENTATION----

    if skills:
        candidates = candidates.filter(skills__name__in=skills).distinct()
    # if location:
    #     candidates = candidates.filter(location=location)
    if workexp:
        candidates = candidates.filter(experience__icontains=workexp)

    template_data = {}
    template_data['candidates'] = candidates
    template_data['skills'] = Skill.objects.all()
    return render(request, 'accounts/candidatesearch.html', {'template_data': template_data})
