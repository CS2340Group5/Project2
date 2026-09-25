from django.db import models
from django.conf import settings

class Skill(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class JobPost(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    skills = models.ManyToManyField(Skill)
    position = models.CharField(max_length=150)
    salary_min = models.IntegerField()
    is_remote = models.BooleanField(default=False)
    visa_sponsorship = models.BooleanField(default=False)
    location = models.CharField(max_length=5)
    recruiter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)

    def skills_toString(self):
        sl = self.skills.all()
        return ", ".join([str(s) for s in sl])
    

    def __str__(self):
        return str(self.id) + ' - ' + self.name


class Bookmark(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    post = models.ForeignKey(JobPost, on_delete=models.CASCADE, null = True)

    def __str__(self):
        return self.user.username + ' - '  + str(self.post.id)

class Application(models.Model):
    class Status(models.TextChoices):
        APPLIED = "APPLIED", "Applied"
        REVIEW = "REVIEW", "In Review"
        INTERVIEW = "INTERVIEW", "Interview"
        OFFER = "OFFER", "Offer"
        CLOSED = "CLOSED", "Closed"

    status = models.CharField(max_length=10,
                            choices=Status.choices,
                            default=Status.APPLIED)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    post = models.ForeignKey(JobPost, on_delete=models.CASCADE, null=True)
    note = models.TextField(max_length=500, blank=True)

    def __str__(self):
        return self.user.username + ' - ' + self.post.name
