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

    def skills_string(self):
        sl = self.skills.all()
        return ", ".join([str(s) for s in sl])
    

    def __str__(self):
        return str(self.id) + ' - ' + self.name