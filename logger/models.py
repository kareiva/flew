from django.db import models
from django.contrib.auth.models import User


class QSOLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    call = models.CharField(max_length=20)
    qso_date = models.CharField(max_length=8)
    time_on = models.CharField(max_length=4)
    freq = models.CharField(max_length=10, blank=True)
    band = models.CharField(max_length=6, blank=True)
    mode = models.CharField(max_length=10, blank=True)
    rst_sent = models.CharField(max_length=3, blank=True)
    rst_rcvd = models.CharField(max_length=3, blank=True)
    gridsquare = models.CharField(max_length=8, blank=True)
    station_callsign = models.CharField(max_length=20, blank=True)
    my_gridsquare = models.CharField(max_length=8, blank=True)
    stx = models.CharField(max_length=10, blank=True)
    srx = models.CharField(max_length=10, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.qso_date} {self.time_on} - {self.call}"


class UserDefaults(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    station_callsign = models.CharField(max_length=20, blank=True)
    my_gridsquare = models.CharField(max_length=8, blank=True)
    mode = models.CharField(max_length=10, default="SSB")
    band = models.CharField(max_length=6, default="20m")
    freq = models.CharField(max_length=10, default="14.200")

    def __str__(self):
        return f"Defaults for {self.user.username}"


class SavedInput(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    input_text = models.TextField()
    adif_text = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.user.username}"


class LoginAttempt(models.Model):
    username = models.CharField(max_length=255)
    ip_address = models.GenericIPAddressField()
    attempt_time = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-attempt_time']
    
    @classmethod
    def cleanup_old_attempts(cls):
        from django.utils import timezone
        from datetime import timedelta
        from django.conf import settings
        
        # Remove attempts older than the timeout period
        expiration = timezone.now() - timedelta(seconds=settings.LOGIN_ATTEMPT_TIMEOUT)
        cls.objects.filter(attempt_time__lt=expiration).delete()
    
    @classmethod
    def get_recent_attempts(cls, username, ip_address):
        cls.cleanup_old_attempts()
        return cls.objects.filter(
            username=username,
            ip_address=ip_address,
            attempt_time__gte=timezone.now() - timedelta(seconds=settings.LOGIN_ATTEMPT_TIMEOUT)
        ).count()
