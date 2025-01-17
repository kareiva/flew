# Common regex patterns for ham radio validation
callsign_pattern = r"\b[A-Z0-9]{1,3}[0-9][A-Z0-9]*[A-Z]\b"
grid_pattern = r"\b[A-R]{2}[0-9]{2}(?:[A-X]{2}(?:[0-9]{2})?)?\b"
# Frequency must have decimal point or MHz suffix
frequency_pattern = r"\b\d+\.\d*(?:\s*(?:MHZ|MHz|Mhz))?\b|\b\d+(?:\s*(?:MHZ|MHz|Mhz))\b"
# Band pattern: number followed by 'm'
band_pattern = r"\b(\d+)m\b"
mode_pattern = r"\b(CW|SSB|FM|FT8|FT4|RTTY|PSK31)\b"
rst_pattern = r"\b[1-5][1-9]\b"

# Minute pattern: number 0-59 right before callsign, but not followed by MHz, decimal point, or 'm'
minute_pattern = r"\b([0-5]?[0-9])(?!\.\d|\s*MHz|\s*MHZ|\s*Mhz|m)\s+(?=[A-Z0-9]{1,3}[0-9][A-Z0-9]*[A-Z]\b)"

# Date patterns: YYYY-MM-DD, DD.MM.YYYY, MM/DD/YYYY, etc.
date_pattern = r"\b(?:\d{4}[-/.]\d{2}[-/.]\d{2}|\d{2}[-/.]\d{2}[-/.]\d{4})\b"

# Time pattern: HH:MM:SS, HH:MM, or HHMMSS
time_pattern = r"\b(?:\d{1,2}:\d{2}(?::\d{2})?|\d{6}|\d{4})\b"

# Combined datetime pattern - date alone or date with time
datetime_pattern = rf"(?:{date_pattern}(?:\s+{time_pattern})?)"
