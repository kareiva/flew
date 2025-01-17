from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("signup/", views.signup, name="signup"),
    path("parse_text/", views.parse_text, name="parse_text"),
    path("export/adif/", views.export_adif, name="export_adif"),
    path("export/csv/", views.export_csv, name="export_csv"),
]
