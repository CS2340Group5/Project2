from django.db import models
from django.conf import settings


class Report(models.Model):
    class Reason(models.TextChoices):
        INAPPROPRIATE = "INAPPROPRIATE", "Inappropriate content"
        MISLEADING = "MISLEADING", "Misleading or fraudulent"
        ABUSIVE = "ABUSIVE", "Abusive or harassing behavior"
        SPAM = "SPAM", "Spam"
        OTHER = "OTHER", "Other"

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        RESOLVED = "RESOLVED", "Resolved"

    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="reports_made")
    reported_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="reports_received")
    reported_post = models.ForeignKey('posts.JobPost', on_delete=models.SET_NULL, null=True, blank=True, related_name="reports")
    target_summary = models.CharField(max_length=255)
    reason = models.CharField(max_length=15, choices=Reason.choices, default=Reason.INAPPROPRIATE)
    details = models.TextField(max_length=1000, blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    action = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.target_summary} ({self.get_status_display()})"
