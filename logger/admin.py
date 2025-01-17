from django.contrib import admin
from .models import QSOLog, UserDefaults


@admin.register(QSOLog)
class QSOLogAdmin(admin.ModelAdmin):
    list_display = ("call", "qso_date", "time_on", "mode", "band", "user")
    list_filter = ("mode", "band", "user")
    search_fields = ("call", "comment")
    date_hierarchy = "created_at"


@admin.register(UserDefaults)
class UserDefaultsAdmin(admin.ModelAdmin):
    list_display = ("user", "mode", "band", "freq", "station_callsign")
    list_filter = ("mode", "band")
    search_fields = ("user__username", "station_callsign")
