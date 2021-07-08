from django.db import models
from django.contrib.auth.models import User


class MeetingRoom(models.Model):
    name = models.CharField(blank=False, null=False, max_length=15, unique=True)
    amount_people = models.IntegerField(blank=False, null=False)

    def __str__(self):
        return self.name


class Reservation(models.Model):
    title = models.CharField(blank=False, null=False, max_length=50)
    start_date_time = models.DateTimeField(blank=False, null=False)
    end_date_time = models.DateTimeField(blank=False, null=False)
    meeting_room = models.ForeignKey(MeetingRoom, blank=False, null=False, on_delete=models.CASCADE)
    employees = models.ManyToManyField(User)

    def __str__(self):
        return self.title
