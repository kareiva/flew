# Generated by Django 5.1.5 on 2025-01-18 10:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("logger", "0004_qsolog_srx_qsolog_stx"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="qsolog",
            options={},
        ),
        migrations.AlterModelOptions(
            name="savedinput",
            options={},
        ),
        migrations.RemoveField(
            model_name="qsolog",
            name="comment",
        ),
        migrations.AddField(
            model_name="qsolog",
            name="my_gridsquare",
            field=models.CharField(blank=True, max_length=6),
        ),
        migrations.AddField(
            model_name="qsolog",
            name="station_callsign",
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AlterField(
            model_name="qsolog",
            name="band",
            field=models.CharField(blank=True, max_length=6),
        ),
        migrations.AlterField(
            model_name="qsolog",
            name="freq",
            field=models.CharField(blank=True, max_length=10),
        ),
        migrations.AlterField(
            model_name="qsolog",
            name="mode",
            field=models.CharField(blank=True, max_length=10),
        ),
        migrations.AlterField(
            model_name="qsolog",
            name="rst_rcvd",
            field=models.CharField(blank=True, max_length=3),
        ),
        migrations.AlterField(
            model_name="qsolog",
            name="rst_sent",
            field=models.CharField(blank=True, max_length=3),
        ),
        migrations.AlterField(
            model_name="qsolog",
            name="time_on",
            field=models.CharField(max_length=4),
        ),
        migrations.AlterField(
            model_name="savedinput",
            name="adif_text",
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name="userdefaults",
            name="band",
            field=models.CharField(default="20m", max_length=6),
        ),
        migrations.AlterField(
            model_name="userdefaults",
            name="my_gridsquare",
            field=models.CharField(blank=True, max_length=6),
        ),
        migrations.AlterField(
            model_name="userdefaults",
            name="station_callsign",
            field=models.CharField(blank=True, max_length=20),
        ),
    ]
