from django.db import models

class Skill(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Position(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class JobPost(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    skills = models.ManyToManyField(Skill)
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    salary_min = models.IntegerField()
    is_remote = models.BooleanField(default=False)
    visa_sponsorship = models.BooleanField(default=False)
    location = models.CharField(max_length=5)


    def __str__(self):
        return str(self.id) + ' - ' + self.name