from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("signup/", views.signup, name="signup"),
    path("parse_text/", views.parse_text, name="parse_text"),
    path("export/adif/", views.export_adif, name="export_adif"),
    path("export/csv/", views.export_csv, name="export_csv"),
    path("profile/", views.profile, name="profile"),
    path("save-input/", views.save_input, name="save_input"),
    path("delete-input/<int:input_id>/", views.delete_input, name="delete_input"),
    path("load-input/<int:input_id>/", views.load_input, name="load_input"),
]
