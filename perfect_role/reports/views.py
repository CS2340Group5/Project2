from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from accounts.models import GenericUser
from posts.models import JobPost
from .models import Report


def is_admin(user):
    return user.is_superuser or user.role == 'ADMIN'


def create_report(request, reported_user, reported_post, summary):
    reason = request.POST.get('reason')
    if reason not in Report.Reason.values:
        reason = Report.Reason.OTHER
    Report.objects.create(reporter=request.user, reported_user=reported_user, reported_post=reported_post,
                          target_summary=summary, reason=reason, details=request.POST.get('details', '').strip())
    messages.success(request, 'Thank you. Your report was submitted and will be reviewed by an administrator.')
    return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def report_post(request, id):
    post = get_object_or_404(JobPost, pk=id)
    if request.method != 'POST' or post.recruiter == request.user:
        return redirect('home.index')
    return create_report(request, post.recruiter, post, post.name)


@login_required
def report_user(request, id):
    target = get_object_or_404(GenericUser, id=id)
    if request.method != 'POST' or target == request.user:
        return redirect('home.index')
    return create_report(request, target, None, target.username)


@login_required
def review_reports(request):
    if not is_admin(request.user):
        return HttpResponseForbidden("Only administrators can review reports.")
    status = request.GET.get('status', Report.Status.PENDING)
    template_data = {'title': 'Review Reports'}
    template_data['status'] = status
    template_data['reports'] = Report.objects.filter(status=status)
    return render(request, 'reports/review.html', {'template_data': template_data})


@login_required
def report_detail(request, id):
    if not is_admin(request.user):
        return HttpResponseForbidden("Only administrators can review reports.")
    report = get_object_or_404(Report, pk=id)
    user = report.reported_user
    post = report.reported_post

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'dismiss':
            Report.objects.filter(pk=report.pk).update(status=Report.Status.RESOLVED, action='Dismissed')
        elif action == 'remove_post' and post:
            Report.objects.filter(reported_post=post, status=Report.Status.PENDING).update(
                status=Report.Status.RESOLVED, action='Job posting removed')
            post.delete()
        elif action == 'deactivate' and user and not user.is_superuser:
            user.is_active = False
            user.save()
            Report.objects.filter(reported_user=user, status=Report.Status.PENDING).update(
                status=Report.Status.RESOLVED, action='User deactivated')
        elif action == 'reactivate' and user:
            user.is_active = True
            user.save()
        messages.success(request, 'Done.')
        return redirect('reports.detail', id=report.id)

    template_data = {'title': 'Investigate Report'}
    template_data['report'] = report
    template_data['user'] = user
    template_data['post'] = post
    template_data['other_reports'] = Report.objects.filter(reported_user=user).exclude(pk=report.pk) if user else []
    return render(request, 'reports/detail.html', {'template_data': template_data})
