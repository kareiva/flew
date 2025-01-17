# Common regex patterns for ham radio validation
callsign_pattern = r"\b[A-Z0-9]{1,3}[0-9][A-Z0-9]*[A-Z]\b"
grid_pattern = r"\b[A-R]{2}[0-9]{2}(?:[A-X]{2})?\b"
frequency_pattern = r"\b\d+\.?\d*\s*(?:MHZ|MHz|Mhz)?\b"
mode_pattern = r"\b(CW|SSB|FM|FT8|FT4|RTTY|PSK31)\b"
rst_pattern = r"\b[1-5][1-9]\b" 