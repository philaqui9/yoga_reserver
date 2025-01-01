# Yoga Class Reservation Bot

A Python automation script to book yoga classes at Hot Yoga Revolution studios.

## Features

- Book classes at Metuchen or Cranford locations
- Filter classes by:
  - Specific day of the week
  - Specific time
  - Specific instructor
- Book classes for current or next month
- Automatic login handling
- Graceful error handling and exit

## Setup

1. Install Python 3.8 or higher
2. Install required packages:

   ```bash
   pip install selenium
   ```

3. Set up configuration:
   - Copy `config/config.template.py` to `config/config.py`
   - Edit `config.py` with your credentials:
   ```python
   MINDBODY_USERNAME = "your_email@example.com"
   MINDBODY_PASSWORD = "your_password"
   HYR_METUCHEN_URL = "https://www.hotyogarevolution.com/metuchen"
   HYR_CRANFORD_URL = "https://www.hotyogarevolution.com/cranford"
   ```

## Usage

Run the script:

```bash
python yoga_reserver.py
```

Follow the prompts to:

1. Select studio (Metuchen or Cranford)
2. Choose booking month (current or next)
3. Enter instructor name (optional)
4. Select day of week (optional)
5. Enter target time (optional)

The script will:

- Process all weeks in the target month
- Book classes matching your criteria
- Handle login automatically
- Exit after processing all weeks or if interrupted

## Controls

- Press Ctrl+C at any time to exit safely
- Close the browser window to stop the script immediately

## Notes

- The script uses Chrome browser automation
- Credentials are stored locally in `config.py`
- The `.gitignore` file ensures sensitive data isn't committed
- Time must be entered in "HH:MM AM/PM" format (e.g., "9:30 AM")
