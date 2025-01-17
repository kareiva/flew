# FLEW - Free-text Log Entry for the Web

FLEW is a modern web application designed to simplify ham radio contact logging through natural language input. Created by Simonas Kareiva (LY2EN), this tool bridges the gap between casual logging and standardized ADIF format requirements.

## About

In amateur radio, logging contacts (QSOs) is a fundamental practice that helps operators track their communications and apply for various awards. While traditional logging software requires filling out multiple fields for each contact, FLEW takes a different approach by allowing operators to input their contacts in free text, just as they would write them in a paper log.

For example, instead of filling out separate fields, you can simply type:
```
W1AW 14.074 FT8 599 FN31
K1ABC 7.125 SSB 59
```

FLEW automatically parses these entries and converts them into proper ADIF format, making it compatible with other ham radio logging software and online services.

## Features

- Free-text input for natural logging experience
- Real-time parsing and ADIF conversion
- Support for common ham radio modes (SSB, CW, FT8, FT4, RTTY, etc.)
- Automatic band detection from frequency
- Grid square parsing
- Customizable default values for frequent operating modes/bands
- Export to ADIF and CSV formats
- User accounts for saving logs
- Mobile-friendly interface

## Installation

1. Clone the repository
2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```
3. Install dependencies:
```bash
pip install django python-dotenv adif-io
```
4. Run migrations:
```bash
python manage.py migrate
```
5. Create a superuser:
```bash
python manage.py createsuperuser
```
6. Start the development server:
```bash
python manage.py runserver
```

## Usage

1. Visit the website and optionally create an account
2. Enter your QSOs in free text format in the main input area
3. The system will automatically parse your input and display the ADIF output
4. Logged-in users can:
   - Save their QSOs
   - Set default values (mode, band, RST, etc.)
   - Export their logs in ADIF or CSV format

### Setting Defaults

Logged-in users can set defaults using lines starting with "default":
```
default mode=FT8 freq=7.074 rst_sent=599
```

## Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

Areas where we'd particularly appreciate contributions:
- Additional input parsing patterns
- Support for more ADIF fields
- UI/UX improvements
- Documentation translations
- Bug fixes and testing

## Credits

- Principal author and concept: Simonas Kareiva (LY2EN)
- Development assistance: This project was developed with the help of AI tools, particularly in generating boilerplate code and implementing standard patterns
- Thanks to the ham radio community for inspiration and feedback

## License

This project is licensed under the MIT License - see the LICENSE file for details. 