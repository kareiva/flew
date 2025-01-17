from django.db import models
from django.contrib.auth.models import User


class QSOLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    call = models.CharField(max_length=20)
    qso_date = models.CharField(max_length=8)
    time_on = models.CharField(max_length=6)
    mode = models.CharField(max_length=10)
    freq = models.CharField(max_length=10)
    band = models.CharField(max_length=6)
    rst_sent = models.CharField(max_length=3)
    rst_rcvd = models.CharField(max_length=3)
    stx = models.CharField(max_length=10, blank=True)
    srx = models.CharField(max_length=10, blank=True)
    gridsquare = models.CharField(max_length=6, blank=True)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class UserDefaults(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    station_callsign = models.CharField(max_length=10, blank=True)
    my_gridsquare = models.CharField(max_length=8, blank=True)
    mode = models.CharField(max_length=10, default="SSB")
    band = models.CharField(max_length=10, default="20m")
    freq = models.CharField(max_length=10, default="14.200")

    def __str__(self):
        return f"Defaults for {self.user.username}"


class SavedInput(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    input_text = models.TextField()
    adif_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
