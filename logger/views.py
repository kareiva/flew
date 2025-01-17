from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.db.models import Count
from django.utils import timezone
from .models import QSOLog, UserDefaults
from .forms import ExtendedUserCreationForm, UserDefaultsForm
from .utils import (
    callsign_pattern,
    grid_pattern,
    frequency_pattern,
    mode_pattern,
    rst_pattern,
)
import re
import datetime
import csv
import adif_io

def signup(request):
    if request.method == "POST":
        form = ExtendedUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully. Please log in.')
            return redirect("login")
    else:
        form = ExtendedUserCreationForm()
    return render(request, "registration/signup.html", {"form": form})


def index(request):
    defaults = None
    if request.user.is_authenticated:
        defaults, _ = UserDefaults.objects.get_or_create(user=request.user)
    return render(request, "logger/index.html", {"defaults": defaults})


@csrf_protect
def parse_text(request):
    if request.method == "POST":
        text = request.POST.get("text", "")
        lines = text.split("\n")
        adif_records = []

        # Get default values
        default_values = {
            "mode": "SSB",
            "band": "20m",
            "freq": "14.200",
            "rst_sent": "59",
            "rst_rcvd": "59",
        }

        # If user is logged in, use their defaults
        if request.user.is_authenticated:
            defaults, _ = UserDefaults.objects.get_or_create(user=request.user)
            default_values.update({
                "mode": defaults.mode,
                "band": defaults.band,
                "freq": defaults.freq,
                "rst_sent": defaults.rst_sent,
                "rst_rcvd": defaults.rst_rcvd,
            })
            # Store operator info separately as they don't go into QSOLog
            operator_info = {
                "my_gridsquare": defaults.my_gridsquare,
                "station_callsign": defaults.station_callsign,
            }

        for line in lines:
            line = line.strip()
            if not line:
                continue

            if line.lower().startswith("default"):
                if request.user.is_authenticated:
                    update_default_values(line, defaults)
                continue

            record = parse_line(line, default_values)
            if record:
                # Add operator info to ADIF output but not to QSOLog
                if request.user.is_authenticated:
                    adif_record = {**record, **operator_info}
                    adif_records.append(adif_record)
                    # Create QSOLog with only the fields it supports
                    QSOLog.objects.create(user=request.user, **record)
                else:
                    adif_records.append(record)

        adif_output = convert_to_adif(adif_records)
        return JsonResponse({"adif": adif_output})

    return JsonResponse({"error": "Invalid request"})


def update_default_values(line, defaults):
    line = re.sub(r"^default\s*", "", line.lower())
    pairs = re.findall(r"(\w+)\s*=\s*([^\s]+)", line)

    for key, value in pairs:
        if hasattr(defaults, key):
            setattr(defaults, key, value.upper())
    defaults.save()


def parse_line(line, default_values):
    callsign = re.search(callsign_pattern, line.upper())
    frequency = re.search(frequency_pattern, line)
    mode = re.search(mode_pattern, line.upper())
    rst = re.search(rst_pattern, line)
    grid = re.search(grid_pattern, line.upper())

    if callsign:
        record = default_values.copy()
        now = datetime.datetime.now()

        record.update(
            {
                "call": callsign.group(),
                "qso_date": now.strftime("%Y%m%d"),
                "time_on": now.strftime("%H%M"),
            }
        )

        if frequency:
            freq = float(re.sub(r"[^\d.]", "", frequency.group()))
            record["freq"] = str(freq)
            record["band"] = frequency_to_band(freq)

        if mode:
            record["mode"] = mode.group()

        if rst:
            record["rst_sent"] = rst.group()
            record["rst_rcvd"] = rst.group()

        if grid:
            record["gridsquare"] = grid.group()

        return record

    return None


def frequency_to_band(freq):
    bands = {
        (1.8, 2.0): "160m",
        (3.5, 4.0): "80m",
        (7.0, 7.3): "40m",
        (10.1, 10.15): "30m",
        (14.0, 14.35): "20m",
        (18.068, 18.168): "17m",
        (21.0, 21.45): "15m",
        (24.89, 24.99): "12m",
        (28.0, 29.7): "10m",
        (50.0, 54.0): "6m",
        (144.0, 148.0): "2m",
    }

    for (low, high), band in bands.items():
        if low <= freq <= high:
            return band
    return ""


def convert_to_adif(records):
    adif_output = ""
    for record in records:
        for key, value in record.items():
            if value:
                adif_output += f"<{key}:{len(str(value))}>{value}"
        adif_output += "<eor>\n"
    return adif_output


@login_required
def export_adif(request):
    qsos = QSOLog.objects.filter(user=request.user)

    adif_output = ""
    for qso in qsos:
        for field in qso._meta.fields:
            if field.name not in ["id", "user", "created_at"] and getattr(
                qso, field.name
            ):
                value = getattr(qso, field.name)
                adif_output += f"<{field.name}:{len(str(value))}>{value}"
        adif_output += "<eor>\n"

    response = HttpResponse(adif_output, content_type="text/plain")
    response["Content-Disposition"] = 'attachment; filename="logbook.adi"'
    return response


@login_required
def export_csv(request):
    qsos = QSOLog.objects.filter(user=request.user)

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="logbook.csv"'

    writer = csv.writer(response)
    fields = [f.name for f in QSOLog._meta.fields if f.name not in ["id", "user"]]
    writer.writerow(fields)

    for qso in qsos:
        row = [getattr(qso, field) for field in fields]
        writer.writerow(row)

    return response


@login_required
def profile(request):
    user_defaults = UserDefaults.objects.get(user=request.user)
    
    if request.method == "POST":
        form = UserDefaultsForm(request.POST, instance=user_defaults)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('profile')
    else:
        form = UserDefaultsForm(instance=user_defaults)
    
    qso_count = QSOLog.objects.filter(user=request.user).count()
    last_login = request.user.last_login or request.user.date_joined
    
    context = {
        'qso_count': qso_count,
        'last_login': last_login,
        'user': request.user,
        'form': form,
    }
    return render(request, 'logger/profile.html', context)
