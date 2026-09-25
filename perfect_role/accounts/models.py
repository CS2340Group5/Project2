from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid

# Create your models here.
'''
GenericUser class
Holds extra information about a user which is needed
to create an account.
This class is used rather than the normal User class
in order to force users to choose 1 role to take upon
account creation
'''
class GenericUser(AbstractUser):
    class Role(models.TextChoices):
        APPLICANT = "APPLICANT", "Applicant"
        RECRUITER = "RECRUITER", "Recruiter"
        ADMIN = "ADMIN", "Admin"
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # String for the different roles available to a user
    # Used to differentiate the roles when needed
    role = models.CharField(max_length=10,
                            choices=Role.choices,
                            default=Role.APPLICANT)

    # Will need to improve later, but for now users will simply
    # type their fields in
    education = models.TextField(max_length=50, blank=True)
    experience = models.TextField(max_length=500, blank=True)

    headline = models.TextField(max_length=150, blank=True)
    skills = models.ManyToManyField('posts.Skill', blank=True)

    # Privacy options: what recruiters can see on this profile
    is_public = models.BooleanField(default=True)
    show_education = models.BooleanField(default=True)
    show_experience = models.BooleanField(default=True)
    show_links = models.BooleanField(default=True)
    def __str__(self):
        return f"{super().__str__()} - Role: {self.role}"
    
    def skills_toString(self):
            sl = self.skills.all()
            return ", ".join([str(s) for s in sl])


# Example of improved field with the social links
'''
User creates SocialLink object when adding a link
User defines url and name, and the object is then linked
to the user through the foreign key
'''
class SocialLink(models.Model):
    user = models.ForeignKey(GenericUser,
                             on_delete=models.CASCADE,
                             related_name="sociallinks")
    url = models.URLField()
    title = models.CharField(max_length=30)
    def __str__(self):
        return f"{self.title}"


class ExperienceType(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name


class WorkExperience(models.Model):
    user = models.ForeignKey(GenericUser, on_delete=models.CASCADE, related_name="experiences")
    kind = models.ForeignKey(ExperienceType, on_delete=models.CASCADE)
    company = models.CharField(max_length=100)
    description = models.TextField(max_length=500, blank=True)
    def __str__(self):
        return f"{self.kind} at {self.company}"


class School(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name


class Education(models.Model):
    user = models.ForeignKey(GenericUser, on_delete=models.CASCADE, related_name="educations")
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    degree = models.CharField(max_length=100)
    description = models.TextField(max_length=500, blank=True)
    def __str__(self):
        return f"{self.degree} at {self.school}"
