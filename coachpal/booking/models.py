from django.db import models
from django.contrib.auth.models import User

class Booking(models.Model):
    coach = models.ForeignKey(User, on_delete=models.CASCADE, related_name="coach_bookings")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="client_bookings")
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    email = models.EmailField()
    date = models.DateField()
    time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True) 

    def __str__(self):
        return f"{self.user.username} → {self.coach.username} ({self.date} {self.time})"
    
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    coach = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='coachees')