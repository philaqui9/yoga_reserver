# Yoga Class Reservation System

An automated system to book yoga classes at Hot Yoga Revolution studios through the Mindbody platform.

## Features

- Book classes at either Metuchen or Cranford studio locations
- Filter classes by:
  - Specific month or all remaining months of the year
  - Day of the week
  - Time of day
  - Instructor
- Automated login and booking process
- Graceful error handling and exit options
- Progress tracking to avoid duplicate bookings

## Prerequisites

- Python 3.7 or higher
- Chrome browser
- ChromeDriver (compatible with your Chrome version)

## Installation

1. Clone the repository:

```bash
git clone [repository-url]
cd yoga-reservation
```

2. Install required packages:

```bash
pip install -r requirements.txt
```

3. Set up configuration:
   - Copy `config/config.template.py` to `config/config.py`
   - Update `config.py` with your credentials:
     ```python
     MINDBODY_USERNAME = "your_username"
     MINDBODY_PASSWORD = "your_password"
     HYR_METUCHEN_URL = "metuchen_studio_url"
     HYR_CRANFORD_URL = "cranford_studio_url"
     ```

## Usage

1. Run the script:

```bash
python yoga_reserver.py
```

2. Follow the interactive prompts to:

   - Select studio location (Metuchen or Cranford)
   - Choose target month or all remaining months
   - Optionally specify:
     - Instructor name
     - Day of the week
     - Time of day

3. The system will:

   - Log in to your Mindbody account
   - Navigate to the selected month
   - Find and book classes matching your criteria
   - Provide real-time feedback on the booking process

4. To exit at any time:
   - Press Ctrl+C for graceful shutdown
   - The system will complete current operations before closing

## Project Structure

```
yoga-reservation/
├── config/
│   ├── config.py           # User credentials (not in git)
│   └── config.template.py  # Template for config
├── resources/
│   └── html_selectors.py   # HTML class names and selectors
├── utilities/
│   └── mindbody_handler.py # Core booking functionality
└── yoga_reserver.py        # Main script
```

## Notes

- The system processes one week at a time to ensure reliable booking
- Already processed dates are tracked to avoid duplicate bookings
- The browser window must remain open during operation
- Login credentials are stored locally and never shared

## Error Handling

- Invalid inputs are caught and re-prompted
- Network issues are handled gracefully
- Browser closure is detected and handled
- Keyboard interrupts allow safe exit

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## License

[Your chosen license]
