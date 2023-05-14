from django.db import models

from MyUser.models import MyUser

class Group(models.Model):

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    currency = models.CharField(max_length=100, default="تومان")
    picture_id = models.IntegerField(blank=False, default=0)

class Members(models.Model):
    groupID = models.ForeignKey(
        Group, related_name='group', on_delete=models.CASCADE)

    userID = models.ForeignKey(MyUser, related_name='member', on_delete=models.CASCADE, null=True)
