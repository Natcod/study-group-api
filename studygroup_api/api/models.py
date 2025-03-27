from django.db import models
from django.contrib.auth.models import User

class StudyGroup(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_groups')
    members = models.ManyToManyField(User, related_name='study_groups')

    def __str__(self):
        return self.name