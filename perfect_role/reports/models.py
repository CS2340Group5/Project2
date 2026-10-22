from django.db import models
from django.conf import settings


class Report(models.Model):
    class TargetType(models.TextChoices):
        USER = "USER", "User"
        POST = "POST", "Job Posting"

    class Reason(models.TextChoices):
        INAPPROPRIATE = "INAPPROPRIATE", "Inappropriate content"
        MISLEADING = "MISLEADING", "Misleading or fraudulent"
        ABUSIVE = "ABUSIVE", "Abusive or harassing behavior"
        SPAM = "SPAM", "Spam"
        OTHER = "OTHER", "Other"

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        INVESTIGATING = "INVESTIGATING", "Under Investigation"
        RESOLVED = "RESOLVED", "Resolved"
        DISMISSED = "DISMISSED", "Dismissed"

    class Action(models.TextChoices):
        NONE = "NONE", "No action"
        USER_WARNED = "USER_WARNED", "User warned"
        POST_REMOVED = "POST_REMOVED", "Job posting removed"
        USER_DEACTIVATED = "USER_DEACTIVATED", "User deactivated"

    OPEN_STATUSES = [Status.PENDING, Status.INVESTIGATING]

    target_type = models.CharField(max_length=10, choices=TargetType.choices)
    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
                                 related_name="reports_made")
    reported_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                                      related_name="reports_received")
    reported_post = models.ForeignKey('posts.JobPost', on_delete=models.SET_NULL, null=True, blank=True,
                                      related_name="reports")
    target_summary = models.CharField(max_length=255, blank=True)
    reason = models.CharField(max_length=15, choices=Reason.choices, default=Reason.INAPPROPRIATE)
    details = models.TextField(max_length=1000, blank=True)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)
    action_taken = models.CharField(max_length=20, choices=Action.choices, default=Action.NONE)
    admin_notes = models.TextField(max_length=2000, blank=True)
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name="reports_reviewed")
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    @property
    def is_open(self):
        return self.status in self.OPEN_STATUSES

    def __str__(self):
        return f"{self.get_target_type_display()} report: {self.target_summary} ({self.get_status_display()})"
