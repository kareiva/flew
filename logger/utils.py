import re
from datetime import datetime, timedelta

# Patterns
callsign_pattern = r"\b[A-Z0-9]{1,3}[0-9][A-Z0-9]*[A-Z]\b"
grid_pattern = r"\b[A-R]{2}[0-9]{2}(?:[A-X]{2})?\b"
frequency_pattern = r"\b\d+\.\d*(?:\s*(?:MHZ|MHz|Mhz))?\b|\b\d+(?:\s*(?:MHZ|MHz|Mhz))\b"
mode_pattern = r"\b(CW|SSB|FM|FT8|FT4|RTTY|PSK31)\b"
rst_pattern = r"\b[1-5][1-9]\b"
band_pattern = r"\b(\d+)m\b"
minute_pattern = r"\b([0-5]?[0-9])(?!\.\d|\s*MHz|\s*MHZ|\s*Mhz|m)\s+(?=[A-Z0-9]{1,3}[0-9][A-Z0-9]*[A-Z]\b)"
date_pattern = r"\b\d{4}-\d{2}-\d{2}\b"
time_pattern = r"\b[0-2]\d[0-5]\d\b"
datetime_pattern = rf"(?:{date_pattern}(?:\s+{time_pattern})?)"
stx_pattern = r"\s,(\d+)\b"  # Space comma number
srx_pattern = r"\s\.(\d+)\b"  # Space dot number


def parse_datetime(text):
    """Parse date and time from text."""
    date_match = re.search(date_pattern, text)
    time_match = re.search(time_pattern, text)
    return (
        date_match.group() if date_match else None,
        time_match.group() if time_match else None,
    )


def frequency_to_band(freq):
    """Convert frequency to band."""
    freq = float(freq)
    if 1.8 <= freq <= 2.0:
        return "160m"
    elif 3.5 <= freq <= 4.0:
        return "80m"
    elif 5.3 <= freq <= 5.4:
        return "60m"
    elif 7.0 <= freq <= 7.3:
        return "40m"
    elif 10.1 <= freq <= 10.15:
        return "30m"
    elif 14.0 <= freq <= 14.35:
        return "20m"
    elif 18.068 <= freq <= 18.168:
        return "17m"
    elif 21.0 <= freq <= 21.45:
        return "15m"
    elif 24.89 <= freq <= 24.99:
        return "12m"
    elif 28.0 <= freq <= 29.7:
        return "10m"
    elif 50.0 <= freq <= 54.0:
        return "6m"
    elif 144.0 <= freq <= 148.0:
        return "2m"
    return None


def band_to_frequency(band):
    """Convert band to default frequency."""
    band_freq = {
        "160": 1.840,
        "80": 3.573,
        "60": 5.357,
        "40": 7.074,
        "30": 10.136,
        "20": 14.074,
        "17": 18.100,
        "15": 21.074,
        "12": 24.915,
        "10": 28.074,
        "6": 50.313,
        "2": 144.174,
    }
    return band_freq.get(str(band))


def parse_line(line, mode="CW"):
    """Parse a single line of text into a QSO record."""
    record = {}
    original_line = line

    # Find and remove patterns we understand
    band = re.search(band_pattern, line)
    if band:
        record["band"] = f"{band.group(1)}m"
        if not re.search(
            frequency_pattern, line
        ):  # Only set default freq if no explicit freq
            freq = band_to_frequency(band.group(1))
            if freq:
                record["freq"] = str(freq)
        line = re.sub(band_pattern, "", line)

    frequency = re.search(frequency_pattern, line)
    if frequency:
        freq = float(re.sub(r"[^\d.]", "", frequency.group()))
        record["freq"] = str(freq)
        derived_band = frequency_to_band(freq)
        if derived_band:
            record["band"] = derived_band
        line = re.sub(frequency_pattern, "", line)

    callsign = re.search(callsign_pattern, line.upper())
    if callsign:
        record["call"] = callsign.group()
        line = re.sub(callsign_pattern, "", line, flags=re.IGNORECASE)

    grid = re.search(grid_pattern, line.upper())
    if grid:
        record["gridsquare"] = grid.group()
        line = re.sub(grid_pattern, "", line, flags=re.IGNORECASE)

    mode_match = re.search(mode_pattern, line.upper())
    if mode_match:
        record["mode"] = mode_match.group()
        line = re.sub(mode_pattern, "", line, flags=re.IGNORECASE)

    minute = re.search(minute_pattern, line)
    if minute:
        record["time_on"] = f"{datetime.now().strftime('%H')}{minute.group(1).zfill(2)}"
        line = re.sub(minute_pattern, "", line)

    stx = re.search(stx_pattern, line)
    if stx:
        record["stx"] = stx.group(1)
        line = re.sub(stx_pattern, "", line)

    srx = re.search(srx_pattern, line)
    if srx:
        record["srx"] = srx.group(1)
        line = re.sub(srx_pattern, "", line)

    # RST handling
    rst = re.search(rst_pattern, line)
    if rst:
        rst_val = rst.group()
        if len(rst_val) == 2:
            if mode.upper() == "CW":
                rst_val = "5" + rst_val
            else:
                rst_val = rst_val
        record["rst_sent"] = rst_val
        record["rst_rcvd"] = rst_val
        line = re.sub(rst_pattern, "", line)

    # Add remaining unparsed text as comment
    remaining_text = " ".join(line.split())  # Normalize whitespace
    if remaining_text.strip():
        record["comment"] = remaining_text.strip()

    return record
