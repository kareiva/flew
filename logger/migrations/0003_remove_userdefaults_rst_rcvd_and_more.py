# Generated by Django 5.1.5 on 2025-01-17 22:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("logger", "0002_savedinput"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="userdefaults",
            name="rst_rcvd",
        ),
        migrations.RemoveField(
            model_name="userdefaults",
            name="rst_sent",
        ),
        migrations.AlterField(
            model_name="userdefaults",
            name="band",
            field=models.CharField(default="20m", max_length=10),
        ),
        migrations.AlterField(
            model_name="userdefaults",
            name="my_gridsquare",
            field=models.CharField(blank=True, max_length=8),
        ),
        migrations.AlterField(
            model_name="userdefaults",
            name="station_callsign",
            field=models.CharField(blank=True, max_length=10),
        ),
    ]
