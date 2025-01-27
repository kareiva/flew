# Generated by Django 5.1.5 on 2025-01-17 18:53

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="QSOLog",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("call", models.CharField(max_length=20)),
                ("qso_date", models.CharField(max_length=8)),
                ("time_on", models.CharField(max_length=6)),
                ("mode", models.CharField(max_length=10)),
                ("freq", models.CharField(max_length=10)),
                ("band", models.CharField(max_length=6)),
                ("rst_sent", models.CharField(max_length=3)),
                ("rst_rcvd", models.CharField(max_length=3)),
                ("gridsquare", models.CharField(blank=True, max_length=6)),
                ("comment", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="UserDefaults",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("mode", models.CharField(default="SSB", max_length=10)),
                ("band", models.CharField(default="20m", max_length=6)),
                ("freq", models.CharField(default="14.200", max_length=10)),
                ("rst_sent", models.CharField(default="59", max_length=3)),
                ("rst_rcvd", models.CharField(default="59", max_length=3)),
                ("my_gridsquare", models.CharField(blank=True, max_length=6)),
                ("station_callsign", models.CharField(blank=True, max_length=20)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
