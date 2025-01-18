from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import CustomLoginView

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
    path("save-qsos/", views.save_qsos, name="save_qsos"),
    path("help/", views.help, name="help"),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/<str:uidb64>/<str:token>/', views.password_reset_confirm, name='password_reset_confirm'),
]
