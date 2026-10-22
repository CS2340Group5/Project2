from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.db.models import Q, Count
from django.core.mail import send_mail
from accounts.models import GenericUser
from posts.models import JobPost, Application
from messaging.models import Message
from .models import Report


def is_admin(user):
    return user.is_superuser or user.role == 'ADMIN'


def redirect_back(request):
    referer = request.META.get('HTTP_REFERER')
    if referer and url_has_allowed_host_and_scheme(referer, allowed_hosts={request.get_host()},
                                                   require_https=request.is_secure()):
        return redirect(referer)
    return redirect('home.index')


def submit_report(request, target_type, reported_user=None, reported_post=None, summary=''):
    reason = request.POST.get('reason')
    details = request.POST.get('details', '').strip()[:1000]
    if reason not in Report.Reason.values:
        messages.warning(request, 'Please choose a reason for your report.')
        return
    existing = Report.objects.filter(reporter=request.user, target_type=target_type,
                                     status__in=Report.OPEN_STATUSES)
    if target_type == Report.TargetType.POST:
        existing = existing.filter(reported_post=reported_post)
    else:
        existing = existing.filter(reported_user=reported_user)
    if existing.exists():
        messages.info(request, 'You already have an open report about this. An administrator will review it soon.')
        return
    Report.objects.create(
        target_type=target_type,
        reporter=request.user,
        reported_user=reported_user,
        reported_post=reported_post,
        target_summary=summary[:255],
        reason=reason,
        details=details,
    )
    messages.success(request, 'Thank you. Your report was submitted and will be reviewed by an administrator.')


@login_required
def report_post(request, id):
    post = get_object_or_404(JobPost, pk=id)
    if request.method == 'POST':
        if post.recruiter == request.user:
            messages.warning(request, 'You cannot report your own job posting.')
        else:
            submit_report(request, Report.TargetType.POST, reported_user=post.recruiter, reported_post=post,
                          summary=f"{post.name} ({post.position})")
    return redirect_back(request)


@login_required
def report_user(request, id):
    target = get_object_or_404(GenericUser, id=id)
    if request.method == 'POST':
        if target == request.user:
            messages.warning(request, 'You cannot report yourself.')
        else:
            submit_report(request, Report.TargetType.USER, reported_user=target, summary=target.username)
    return redirect_back(request)


@login_required
def review_reports(request):
    if not is_admin(request.user):
        return HttpResponseForbidden("Only administrators can review reports.")

    status = request.GET.get('status', 'open')
    target_type = request.GET.get('type', '')
    reason = request.GET.get('reason', '')
    search = request.GET.get('search', '').strip()

    reports = Report.objects.select_related('reporter', 'reported_user', 'reported_post')
    if status == 'open':
        reports = reports.filter(status__in=Report.OPEN_STATUSES)
    elif status in Report.Status.values:
        reports = reports.filter(status=status)
    else:
        status = 'all'
    if target_type in Report.TargetType.values:
        reports = reports.filter(target_type=target_type)
    if reason in Report.Reason.values:
        reports = reports.filter(reason=reason)
    if search:
        reports = reports.filter(Q(target_summary__icontains=search) | Q(details__icontains=search) |
                                 Q(reporter__username__icontains=search) |
                                 Q(reported_user__username__icontains=search))

    open_reports = Report.objects.filter(status__in=Report.OPEN_STATUSES)
    post_counts = dict(open_reports.filter(target_type=Report.TargetType.POST, reported_post__isnull=False)
                       .values_list('reported_post').annotate(total=Count('id')))
    user_counts = dict(open_reports.filter(target_type=Report.TargetType.USER, reported_user__isnull=False)
                       .values_list('reported_user').annotate(total=Count('id')))
    reports = list(reports)
    for report in reports:
        if report.target_type == Report.TargetType.POST:
            report.open_on_target = post_counts.get(report.reported_post_id, 0)
        else:
            report.open_on_target = user_counts.get(report.reported_user_id, 0)

    status_counts = dict(Report.objects.values_list('status').annotate(total=Count('id')))
    status_tabs = [('open', 'Open', sum(status_counts.get(s, 0) for s in Report.OPEN_STATUSES))]
    status_tabs += [(value, label, status_counts.get(value, 0)) for value, label in Report.Status.choices]
    status_tabs.append(('all', 'All', sum(status_counts.values())))

    template_data = {
        'title': 'Review Reports',
        'reports': reports,
        'status': status,
        'status_tabs': status_tabs,
        'type': target_type,
        'reason': reason,
        'search': search,
        'type_choices': Report.TargetType.choices,
        'reason_choices': Report.Reason.choices,
    }
    return render(request, 'reports/review.html', {'template_data': template_data})


def close_reports(queryset, admin, status, action):
    queryset.update(status=status, action_taken=action, reviewed_by=admin, reviewed_at=timezone.now())


def close_report(report, admin, status, action):
    report.status = status
    report.action_taken = action
    report.reviewed_by = admin
    report.reviewed_at = timezone.now()


@login_required
def report_detail(request, id):
    if not is_admin(request.user):
        return HttpResponseForbidden("Only administrators can review reports.")

    report = get_object_or_404(Report.objects.select_related('reporter', 'reported_user', 'reported_post',
                                                             'reviewed_by'), pk=id)
    target_user = report.reported_user
    post = report.reported_post

    if request.method == 'POST':
        action = request.POST.get('action')
        report.admin_notes = request.POST.get('admin_notes', '').strip()[:2000]
        post_to_delete = None

        if action == 'save_notes':
            messages.success(request, 'Investigation notes saved.')

        elif action == 'investigate' and report.status == Report.Status.PENDING:
            report.status = Report.Status.INVESTIGATING
            report.reviewed_by = request.user
            report.reviewed_at = timezone.now()
            messages.success(request, 'Report marked as under investigation.')

        elif action == 'dismiss' and report.is_open:
            close_report(report, request.user, Report.Status.DISMISSED, Report.Action.NONE)
            messages.success(request, 'Report dismissed. No action was taken.')

        elif action == 'warn' and report.is_open and target_user:
            warning = request.POST.get('warning_message', '').strip()[:500]
            if not warning:
                messages.warning(request, 'Please write a warning message before sending it.')
            else:
                Message.objects.create(recruiter=request.user, applicant=target_user, message_text=warning)
                if target_user.email:
                    send_mail("A warning from the Perfect Role team",
                              f"{warning}\n\n** Please note: This email is sent from an unattended mailbox. Replies will not be read **",
                              None, [target_user.email], fail_silently=True)
                close_report(report, request.user, Report.Status.RESOLVED, Report.Action.USER_WARNED)
                messages.success(request, f'A warning was sent to {target_user.username} and the report was resolved.')

        elif action == 'remove_post' and report.is_open and post:
            close_reports(Report.objects.filter(reported_post=post, status__in=Report.OPEN_STATUSES)
                          .exclude(pk=report.pk), request.user, Report.Status.RESOLVED, Report.Action.POST_REMOVED)
            close_report(report, request.user, Report.Status.RESOLVED, Report.Action.POST_REMOVED)
            if post.recruiter and post.recruiter.email:
                send_mail("Your job posting was removed",
                          f"Your job posting \"{post.name}\" was removed by the Perfect Role team after a review of reports submitted about it."
                          f"\n\n** Please note: This email is sent from an unattended mailbox. Replies will not be read **",
                          None, [post.recruiter.email], fail_silently=True)
            post_to_delete = post
            messages.success(request, f'The job posting "{post.name}" was removed and all open reports about it were resolved.')

        elif action == 'deactivate' and report.is_open and target_user:
            if target_user == request.user or target_user.is_superuser:
                messages.warning(request, 'This account cannot be deactivated from here.')
            else:
                target_user.is_active = False
                target_user.save(update_fields=['is_active'])
                close_reports(Report.objects.filter(reported_user=target_user, status__in=Report.OPEN_STATUSES)
                              .exclude(pk=report.pk), request.user, Report.Status.RESOLVED,
                              Report.Action.USER_DEACTIVATED)
                close_report(report, request.user, Report.Status.RESOLVED, Report.Action.USER_DEACTIVATED)
                messages.success(request, f'{target_user.username} was deactivated and all open reports against them were resolved.')

        elif action == 'reactivate' and target_user and not target_user.is_active:
            target_user.is_active = True
            target_user.save(update_fields=['is_active'])
            messages.success(request, f'{target_user.username} was reactivated.')

        elif action == 'reopen' and not report.is_open:
            report.status = Report.Status.PENDING
            report.action_taken = Report.Action.NONE
            report.reviewed_at = None
            messages.success(request, 'Report reopened.')

        else:
            messages.warning(request, 'That action is not available for this report.')

        report.save()
        if post_to_delete:
            post_to_delete.delete()
        return redirect('reports.detail', id=report.id)

    related = Q(pk__in=[])
    if post:
        related |= Q(reported_post=post)
    if target_user:
        related |= Q(reported_user=target_user)
    related_reports = Report.objects.filter(related).exclude(pk=report.pk).select_related('reporter')

    conversation = Message.objects.none()
    if target_user and report.reporter:
        conversation = Message.objects.filter(
            Q(recruiter=target_user, applicant=report.reporter) |
            Q(recruiter=report.reporter, applicant=target_user)
        ).select_related('recruiter').order_by('-date')

    reporter_history = None
    if report.reporter:
        made = Report.objects.filter(reporter=report.reporter)
        reporter_history = {
            'total': made.count(),
            'dismissed': made.filter(status=Report.Status.DISMISSED).count(),
            'actioned': made.filter(status=Report.Status.RESOLVED).exclude(action_taken=Report.Action.NONE).count(),
        }

    template_data = {
        'title': 'Investigate Report',
        'report': report,
        'post': post,
        'target_user': target_user,
        'related_reports': related_reports,
        'conversation': conversation,
        'reporter_history': reporter_history,
        'can_deactivate': bool(target_user and target_user.is_active and target_user != request.user
                               and not target_user.is_superuser),
    }
    if post:
        template_data['application_count'] = Application.objects.filter(post=post).count()
    if target_user:
        template_data['user_posts'] = JobPost.objects.filter(recruiter=target_user)
        template_data['user_links'] = target_user.sociallinks.all()
        template_data['user_experiences'] = target_user.experiences.select_related('kind')
        template_data['user_educations'] = target_user.educations.select_related('school')
    if report.target_type == Report.TargetType.POST:
        subject = f'your job posting "{report.target_summary}"'
    else:
        subject = 'your account'
    name = target_user.username if target_user else ''
    template_data['default_warning'] = (
        f"Hello {name}, our team reviewed a report about {subject}. Please make sure your content and conduct "
        f"follow the Perfect Role community guidelines. Further violations may result in your account being deactivated."
    )
    return render(request, 'reports/detail.html', {'template_data': template_data})
