from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.db.models import Count
from django.utils import timezone
from .models import QSOLog, UserDefaults, SavedInput
from .forms import ExtendedUserCreationForm, ProfileForm
from .utils import (
    callsign_pattern,
    grid_pattern,
    frequency_pattern,
    mode_pattern,
    rst_pattern,
    datetime_pattern,
    time_pattern,
    minute_pattern,
    band_pattern,
    date_pattern,
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
            messages.success(request, "Account created successfully. Please log in.")
            return redirect("login")
    else:
        form = ExtendedUserCreationForm()
    return render(request, "registration/signup.html", {"form": form})


def index(request):
    defaults = None
    saved_inputs = []
    initial_input = None

    if request.user.is_authenticated:
        defaults, _ = UserDefaults.objects.get_or_create(user=request.user)
        saved_inputs = SavedInput.objects.filter(user=request.user)

        # Handle loading saved input
        load_id = request.GET.get("load")
        if load_id:
            try:
                initial_input = SavedInput.objects.get(id=load_id, user=request.user)
            except SavedInput.DoesNotExist:
                pass

    context = {
        "defaults": defaults,
        "saved_inputs": saved_inputs,
        "initial_input": initial_input,
    }
    return render(request, "logger/index.html", context)


def parse_datetime(line):
    """Parse date and time from a line, returns (date, time) in ADIF format."""
    try:
        # First try to parse as full datetime
        for fmt in [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M",
            "%Y/%m/%d %H:%M:%S",
            "%Y/%m/%d %H:%M",
            "%d-%m-%Y %H:%M:%S",
            "%d-%m-%Y %H:%M",
            "%d/%m/%Y %H:%M:%S",
            "%d/%m/%Y %H:%M",
            "%Y.%m.%d %H:%M:%S",
            "%Y.%m.%d %H:%M",
            "%d.%m.%Y %H:%M:%S",
            "%d.%m.%Y %H:%M",
        ]:
            try:
                # Replace separators consistently
                test_str = (
                    line.replace("/", fmt[4]).replace(".", fmt[4]).replace(":", fmt[11])
                )
                dt = datetime.datetime.strptime(test_str, fmt)
                return dt.strftime("%Y%m%d"), dt.strftime("%H%M")
            except ValueError:
                continue

        # Try to parse time only (HHMMSS, HHMM, or HH:MM:SS)
        time_match = re.search(time_pattern, line)
        if time_match:
            time_str = time_match.group().replace(":", "")
            if len(time_str) == 6:  # HHMMSS format
                return None, time_str[:4]  # Return just HHMM for ADIF
            elif len(time_str) == 4:  # HHMM format
                return None, time_str
            else:
                try:
                    # Try to parse as time
                    t = datetime.datetime.strptime(
                        time_match.group(), "%H:%M:%S"
                    ).time()
                    return None, t.strftime("%H%M")
                except ValueError:
                    try:
                        t = datetime.datetime.strptime(
                            time_match.group(), "%H:%M"
                        ).time()
                        return None, t.strftime("%H%M")
                    except ValueError:
                        pass

        # Try to parse date only
        for fmt in [
            "%Y-%m-%d",
            "%Y/%m/%d",
            "%Y.%m.%d",
            "%d-%m-%Y",
            "%d/%m/%Y",
            "%d.%m.%Y",
        ]:
            try:
                test_str = line.replace("/", fmt[4]).replace(".", fmt[4])
                dt = datetime.datetime.strptime(test_str, fmt)
                return dt.strftime("%Y%m%d"), None
            except ValueError:
                continue

        return None, None
    except Exception:
        return None, None


def parse_date_line(line):
    """Parse a line that contains only a date."""
    try:
        line = line.strip()
        # Try YYYY-MM-DD format first
        if re.match(r"^\d{4}-\d{2}-\d{2}$", line):
            dt = datetime.datetime.strptime(line, "%Y-%m-%d")
            return dt.strftime("%Y%m%d")
        # Try other formats if needed
        for fmt in ["%Y/%m/%d", "%Y.%m.%d"]:
            try:
                dt = datetime.datetime.strptime(line, fmt)
                return dt.strftime("%Y%m%d")
            except ValueError:
                continue
        return None
    except Exception:
        return None


@csrf_protect
def parse_text(request):
    if request.method == "POST":
        text = request.POST.get("text", "")
        lines = text.split("\n")
        adif_records = []
        now = datetime.datetime.now()
        current_date = now.strftime("%Y%m%d")
        current_time = now.strftime("%H%M")
        current_hour = now.strftime("%H")

        # Get default values
        default_values = {
            "mode": "SSB",
            "band": "20m",
            "freq": "14.200",
        }

        # If user is logged in, use their defaults
        if request.user.is_authenticated:
            defaults, _ = UserDefaults.objects.get_or_create(user=request.user)
            default_values.update(
                {
                    "mode": defaults.mode,
                    "band": defaults.band,
                    "freq": defaults.freq,
                }
            )
            # Store operator info separately as they don't go into QSOLog
            operator_info = {}
            if defaults.my_gridsquare:
                operator_info["my_gridsquare"] = defaults.my_gridsquare
            if defaults.station_callsign:
                operator_info["STATION_CALLSIGN"] = defaults.station_callsign

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Handle mycall command
            if line.lower().startswith("mycall "):
                if request.user.is_authenticated:
                    callsign = re.search(callsign_pattern, line[7:].upper())
                    if callsign:
                        defaults.station_callsign = callsign.group()
                        defaults.save()
                        operator_info["STATION_CALLSIGN"] = defaults.station_callsign
                continue

            # Handle mygrid command
            if line.lower().startswith("mygrid "):
                if request.user.is_authenticated:
                    grid = re.search(grid_pattern, line[7:].upper())
                    if grid:
                        defaults.my_gridsquare = grid.group()
                        defaults.save()
                        operator_info["my_gridsquare"] = defaults.my_gridsquare
                continue

            # First check if line is just a date or datetime without a callsign
            if not re.search(callsign_pattern, line):
                # Try parsing as date first
                parsed_date = parse_date_line(line)
                if parsed_date:
                    current_date = parsed_date
                    continue

                # Then try parsing as datetime
                parsed_date, parsed_time = parse_datetime(line)
                if parsed_date:
                    current_date = parsed_date
                    if parsed_time:
                        current_time = parsed_time
                        current_hour = parsed_time[:2]
                    continue

            if line.lower().startswith("default"):
                if request.user.is_authenticated:
                    update_default_values(line, defaults)
                continue

            # Check for time in the QSO line itself
            time_match = re.search(time_pattern, line)
            if time_match:
                _, line_time = parse_datetime(line)
                if line_time:
                    current_time = line_time
                    current_hour = line_time[:2]

            # Check for minute before callsign
            minute_match = re.search(minute_pattern, line)
            if minute_match:
                minute = minute_match.group(1).zfill(2)
                current_time = f"{current_hour}{minute}"

            record = parse_line(line, default_values, current_date, current_time)
            if record:
                # Add operator info to ADIF output
                if request.user.is_authenticated:
                    adif_record = {**record, **operator_info}
                    adif_records.append(adif_record)
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


def parse_rst(text, mode):
    """Parse RST values from text according to the rules:
    - Default R=5, S=9, T=9
    - One digit sets S (e.g., 7 -> 57/579)
    - Two digits set RS (e.g., 58)
    - Three digits set RST explicitly (e.g., 589)
    Returns tuple (rst_sent, rst_rcvd)
    """
    # Default values
    default_r = "5"
    default_s = "9"
    default_t = "9"

    # Find all numbers after removing any MHz/frequency/time patterns
    numbers = []
    for match in re.finditer(r"\b\d{1,3}\b", text):
        num = match.group()
        # Skip if it's part of a frequency or time
        if not re.search(
            r"MHz|MHZ|Mhz", text[match.start() : match.end() + 3]
        ) and not re.match(r"\d{4}|\d{6}|\d{1,2}:\d{2}(:\d{2})?", num):
            numbers.append(num)

    def process_rst(num):
        if len(num) == 1:  # Single digit sets S
            rst = default_r + num
            if mode in ["CW", "FT8", "FT4", "RTTY", "PSK31"]:
                rst += default_t
        elif len(num) == 2:  # Two digits set RS
            rst = num
            if mode in ["CW", "FT8", "FT4", "RTTY", "PSK31"]:
                rst += default_t
        else:  # Three digits set RST
            rst = num[:3]  # Limit to 3 digits
        return rst

    rst_sent = rst_rcvd = default_r + default_s
    if mode in ["CW", "FT8", "FT4", "RTTY", "PSK31"]:
        rst_sent += default_t
        rst_rcvd += default_t

    # Process found numbers
    if numbers:
        rst_sent = process_rst(numbers[0])
        if len(numbers) > 1:
            rst_rcvd = process_rst(numbers[1])
        else:
            rst_rcvd = rst_sent

    return rst_sent, rst_rcvd


def parse_line(line, default_values, qso_date=None, qso_time=None):
    # First find all key patterns in the line
    mode = re.search(mode_pattern, line.upper())
    grid = re.search(grid_pattern, line.upper())
    band = re.search(band_pattern, line)  # Don't convert to upper case for band pattern
    frequency = re.search(frequency_pattern, line)

    # Check for time in this line
    time_match = re.search(time_pattern, line)
    if time_match:
        qso_time = time_match.group().replace(":", "")

    # First check for minute before callsign
    minute_match = None

    # Remove band pattern from line before searching for callsign if band is at start
    line_for_call = line
    if band and line.strip().startswith(band.group()):
        line_for_call = line[band.end() :].strip()

    # Now search for callsign in the modified line
    callsign = re.search(callsign_pattern, line_for_call.upper())

    if callsign:
        # Get the text before callsign for minute check
        call_start = line_for_call.upper().find(callsign.group())
        if call_start > 0:
            before_call = line_for_call[:call_start].strip()
            # Check if it's a minute (1-59)
            if re.match(r"^[0-5]?[0-9]$", before_call):
                minute_match = re.match(r"^([0-5]?[0-9])$", before_call)
                if minute_match:
                    qso_time = f"{qso_time[:2]}{minute_match.group(1).zfill(2)}"

        record = default_values.copy()
        now = datetime.datetime.now()

        record.update(
            {
                "call": callsign.group(),
                "qso_date": qso_date or now.strftime("%Y%m%d"),
                "time_on": qso_time or now.strftime("%H%M"),
            }
        )

        # Handle frequency and band
        if frequency:
            # Frequency takes precedence - always use it and derive band from it
            freq_str = re.sub(r"[^\d.]", "", frequency.group())
            try:
                freq = float(freq_str)
                record["freq"] = str(freq)
                derived_band = frequency_to_band(freq)
                if derived_band:
                    record["band"] = derived_band
            except ValueError:
                pass
        elif band:
            # Use band if no frequency is provided
            record["band"] = f"{band.group(1)}m"
            # Use default frequency for this band
            freq = band_to_frequency(band.group(1))
            if freq:
                record["freq"] = str(freq)

        if mode:
            record["mode"] = mode.group()

        # Get text after callsign for RST, STX, and SRX parsing
        after_call = line_for_call[
            line_for_call.upper().find(callsign.group()) + len(callsign.group()) :
        ]

        # Look for STX (numbers prefixed with comma)
        stx_match = re.search(r",(\d+)", after_call)
        if stx_match:
            record["stx"] = stx_match.group(1)
            # Remove the matched STX from after_call to not interfere with RST parsing
            after_call = after_call.replace(stx_match.group(0), "")

        # Look for SRX (numbers prefixed with dot)
        srx_match = re.search(r"\.(\d+)", after_call)
        if srx_match:
            record["srx"] = srx_match.group(1)
            # Remove the matched SRX from after_call to not interfere with RST parsing
            after_call = after_call.replace(srx_match.group(0), "")

        # Parse RST from remaining text
        rst_sent, rst_rcvd = parse_rst(after_call, record.get("mode", "SSB"))
        record["rst_sent"] = rst_sent
        record["rst_rcvd"] = rst_rcvd

        if grid:
            record["gridsquare"] = grid.group()

        return record

    return None


def band_to_frequency(band_value):
    """Convert band (in meters) to a default frequency."""
    band_defaults = {
        "160": "1.830",
        "80": "3.573",
        "40": "7.074",
        "30": "10.136",
        "20": "14.074",
        "17": "18.100",
        "15": "21.074",
        "12": "24.915",
        "10": "28.074",
        "6": "50.313",
        "2": "144.174",
    }
    return band_defaults.get(str(band_value))


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
                # Ensure proper ADIF field format
                adif_output += f"<{key.upper()}:{len(str(value))}>{value}"
        adif_output += "<EOR>\n"
    return adif_output


@login_required
def export_adif(request):
    qsos = QSOLog.objects.filter(user=request.user)

    # If no QSOs to export, return early
    if not qsos.exists():
        messages.warning(request, "No QSOs to export.")
        return redirect("profile")

    defaults = UserDefaults.objects.get(user=request.user)
    now = datetime.datetime.now()

    # Generate ADIF header
    header = (
        f"Generated by FLEW - Free Log Entry for the Web\n"
        f"<ADIF_VER:5>3.1.4\n"
        f"<CREATED_TIMESTAMP:{14}>{now.strftime('%Y%m%d %H%M%S')}\n"
        f"<PROGRAMID:4>FLEW\n"
        f"<PROGRAMVERSION:5>1.0.0\n"
    )

    if defaults.station_callsign:
        header += f"<STATION_CALLSIGN:{len(defaults.station_callsign)}>{defaults.station_callsign}\n"

    header += "<EOH>\n\n"

    # Generate QSO records
    qso_records = ""
    for qso in qsos:
        # Add regular QSO fields
        for field in qso._meta.fields:
            if field.name not in ["id", "user", "created_at"] and getattr(
                qso, field.name
            ):
                value = getattr(qso, field.name)
                qso_records += f"<{field.name}:{len(str(value))}>{value}"

        # Add station callsign if set
        if defaults.station_callsign:
            value = defaults.station_callsign
            qso_records += f"<STATION_CALLSIGN:{len(value)}>{value}"

        qso_records += "<eor>\n"

    adif_output = header + qso_records

    # Prepare response
    response = HttpResponse(adif_output, content_type="text/plain")
    response["Content-Disposition"] = 'attachment; filename="logbook.adi"'

    # Delete QSOs after successful preparation of export
    qso_count = qsos.count()
    qsos.delete()
    messages.success(request, f"Successfully exported and cleared {qso_count} QSOs.")

    return response


@login_required
def export_csv(request):
    qsos = QSOLog.objects.filter(user=request.user)

    # If no QSOs to export, return early
    if not qsos.exists():
        messages.warning(request, "No QSOs to export.")
        return redirect("profile")

    # Prepare CSV data
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="logbook.csv"'

    writer = csv.writer(response)
    fields = [f.name for f in QSOLog._meta.fields if f.name not in ["id", "user"]]
    writer.writerow(fields)

    for qso in qsos:
        row = [getattr(qso, field) for field in fields]
        writer.writerow(row)

    # Delete QSOs after successful preparation of export
    qso_count = qsos.count()
    qsos.delete()
    messages.success(request, f"Successfully exported and cleared {qso_count} QSOs.")

    return response


@login_required
def profile(request):
    user_defaults = UserDefaults.objects.get(user=request.user)

    if request.method == "POST":
        form = ProfileForm(request.POST, instance=user_defaults)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("profile")
    else:
        form = ProfileForm(instance=user_defaults)

    qso_count = QSOLog.objects.filter(user=request.user).count()
    last_login = request.user.last_login or request.user.date_joined
    saved_inputs = SavedInput.objects.filter(user=request.user)

    context = {
        "qso_count": qso_count,
        "last_login": last_login,
        "user": request.user,
        "form": form,
        "saved_inputs": saved_inputs,
    }
    return render(request, "logger/profile.html", context)


@login_required
def save_input(request):
    if request.method == "POST":
        name = request.POST.get("name")
        input_text = request.POST.get("input_text", "").strip()
        adif_text = request.POST.get("adif_text")

        if name and input_text:
            # Check if first line is a date/datetime
            first_line = input_text.split("\n")[0].strip()
            if not re.search(datetime_pattern, first_line) or re.search(
                callsign_pattern, first_line
            ):
                # Prepend current date and time
                now = datetime.datetime.now()
                datetime_line = now.strftime("%Y-%m-%d %H:%M:%S")
                input_text = f"{datetime_line}\n{input_text}"

                # Regenerate ADIF text with the new datetime
                lines = input_text.split("\n")
                adif_records = []
                current_date = now.strftime("%Y%m%d")
                current_time = now.strftime("%H%M")

                # Get user defaults
                defaults, _ = UserDefaults.objects.get_or_create(user=request.user)
                default_values = {
                    "mode": defaults.mode,
                    "band": defaults.band,
                    "freq": defaults.freq,
                }
                operator_info = {
                    "my_gridsquare": defaults.my_gridsquare,
                    "station_callsign": defaults.station_callsign,
                }

                for line in lines:
                    line = line.strip()
                    if not line:
                        continue

                    if re.search(datetime_pattern, line) and not re.search(
                        callsign_pattern, line
                    ):
                        date, time = parse_datetime(line)
                        if date:
                            current_date = date
                        if time:
                            current_time = time
                        continue

                    if line.lower().startswith("default"):
                        continue

                    # Check for time in the QSO line itself
                    time_match = re.search(time_pattern, line)
                    if time_match:
                        _, line_time = parse_datetime(line)
                        if line_time:
                            current_time = line_time

                    record = parse_line(
                        line, default_values, current_date, current_time
                    )
                    if record:
                        adif_record = {**record, **operator_info}
                        adif_records.append(adif_record)

                adif_text = convert_to_adif(adif_records)

            SavedInput.objects.create(
                user=request.user,
                name=name,
                input_text=input_text,
                adif_text=adif_text or "",
            )
            messages.success(request, f'Input saved as "{name}"')
            return JsonResponse(
                {"status": "success", "input_text": input_text, "adif_text": adif_text}
            )

    return JsonResponse({"status": "error"})


@login_required
def delete_input(request, input_id):
    saved_input = get_object_or_404(SavedInput, id=input_id, user=request.user)
    saved_input.delete()
    messages.success(request, f'Input "{saved_input.name}" deleted')
    return redirect("profile")


@login_required
def load_input(request, input_id):
    saved_input = get_object_or_404(SavedInput, id=input_id, user=request.user)
    return JsonResponse(
        {"input_text": saved_input.input_text, "adif_text": saved_input.adif_text}
    )


@login_required
def save_qsos(request):
    if request.method == "POST":
        user_defaults = UserDefaults.objects.get(user=request.user)
        if not user_defaults.station_callsign:
            return JsonResponse(
                {
                    "status": "error",
                    "message": "Please set your station callsign in your profile settings before saving QSOs.",
                }
            )

        adif_text = request.POST.get("adif_text", "")
        if not adif_text:
            return JsonResponse({"status": "error", "message": "No QSOs to save"})

        try:
            qsos, header = adif_io.read_from_string(adif_text)
            for qso in qsos:
                # Convert all keys to lowercase for consistency
                qso = {k.lower(): v for k, v in qso.items()}
                QSOLog.objects.create(user=request.user, **qso)

            return JsonResponse(
                {
                    "status": "success",
                    "message": f"Successfully saved {len(qsos)} QSOs to your log.",
                }
            )
        except Exception as e:
            return JsonResponse(
                {"status": "error", "message": f"Error saving QSOs: {str(e)}"}
            )

    return JsonResponse({"status": "error", "message": "Invalid request method"})


def help(request):
    return render(request, "logger/help.html")
