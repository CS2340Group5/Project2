from django.shortcuts import render
from django.db.models import Q
from posts.models import JobPost, Bookmark, Application, Skill
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import D

def index(request):
    template_data = {}
    template_data['title'] = 'Perfect Role'
    
    if request.user.is_authenticated:
        postings = JobPost.objects.all()
        search = request.GET.get('search')
        skills = request.GET.getlist('skills')
        position = request.GET.get('position')
        salary_min = request.GET.get('salary')
        remote = request.GET.get('remote')
        visa = request.GET.get('visa')
        location = request.GET.get('location')
        distance = request.GET.get('distance')

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
            postings = postings.filter(location__icontains=location)
        if distance and request.user.coordinates:
            postings = postings.filter(coordinates__distance_lte=(request.user.coordinates, D(mi=distance)))
        if request.user.coordinates:
            postings = postings.annotate(distance=Distance('coordinates', request.user.coordinates)).order_by('distance')
        template_data['distance'] = distance

    
        template_data['bookmarks'] = []
        template_data['applied'] = []
        template_data['bookmarks'] = [bookmark.post.id for bookmark in Bookmark.objects.filter(user=request.user)]
        template_data['applied'] = [application.post.id for application in Application.objects.filter(user=request.user)]
        template_data['postings'] = postings.exclude(pk__in=template_data['applied'])
        template_data['skills'] = Skill.objects.all()

    return render(request, 'home/index.html', {'template_data': template_data})
