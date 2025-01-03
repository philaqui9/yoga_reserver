from selenium import webdriver
from datetime import datetime
import calendar
from utilities.mindbody_handler import MindbodyHandler
from config.config import (
    HYR_METUCHEN_URL,
    HYR_CRANFORD_URL
)

def get_studio_choice():
    """Prompts the user to select a yoga studio.
    
    Displays a menu of available studios and handles user input validation.
    
    Returns:
        str: The selected studio name ('metuchen' or 'cranford')
    
    Raises:
        ValueError: If the user enters invalid input
    """

    while True:
        try:
            print("-------------------------------------------------------")
            print("Select studio:")
            print(f"  Available studios:")
            print(f"    1. Metuchen")
            print(f"    2. Cranford")
            
            choice = int(input("\nEnter 1 for Metuchen or 2 for Cranford: "))
            
            if choice == 1:
                return "metuchen"
            elif choice == 2:
                return "cranford"
            else:
                print("Invalid choice. Please enter 1 or 2.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def get_target_month():
    """Prompts the user to select a target month for class booking.
    
    Displays a menu of months and handles user input validation.
    Allows selection of current month, specific month, or all remaining months.
    
    Returns:
        tuple: Contains:
            - int: Target year
            - int: Target month (1-12)
            - bool: Whether to book all remaining months
    
    Raises:
        ValueError: If the user enters invalid input
    """

    while True:
        try:
            # Get current month and year
            current_date = datetime.now()
            current_month = current_date.month
            current_year = current_date.year

            print("-------------------------------------------------------")
            print("Select month:")
            print(f"    Enter for current month")
            print(f"    0. All remaining months")
            for i, month in enumerate(calendar.month_name[1:], 1):
                print(f"    {i}. {month}")
            
            choice = input("\nEnter month number (0-12 or Enter for current): ").strip()
            
            if not choice:  # Empty input (Enter pressed)
                return current_year, current_month, False
            
            choice = int(choice)
            if choice == 0:
                return current_year, current_month, True
            elif 1 <= choice <= 12:
                if choice < current_month:
                    print("Cannot book classes in past months.")
                    continue
                return current_year, choice, False
            else:
                print("Invalid choice. Please enter a number between 0 and 12 or press Enter.")
        except ValueError:
            print("Invalid input. Please enter a number or press Enter.")

def get_target_day():
    """Prompts the user to select a target day of the week for class booking.
    
    Displays a menu of days and handles user input validation.
    Allows selection of specific day or any day.
    
    Returns:
        str or None: The selected day name or None if any day is selected
    
    Raises:
        ValueError: If the user enters invalid input
    """

    days = {
        1: "Monday",
        2: "Tuesday",
        3: "Wednesday",
        4: "Thursday",
        5: "Friday",
        6: "Saturday",
        7: "Sunday"
    }
    
    while True:
        try:
            print("-------------------------------------------------------")
            print("Select day:")
            print("Enter for any day")
            for num, day in days.items():
                print(f"    {num}. {day}")
            
            choice = input("\nEnter day number (1-7 or Enter for any day): ").strip()
            
            if not choice:  # Empty input (Enter pressed)
                return None
            
            choice = int(choice)
            if 1 <= choice <= 7:
                return days[choice]
            else:
                print("Invalid choice. Please enter a number between 1 and 7 or press Enter.")
        except ValueError:
            print("Invalid input. Please enter a number or press Enter.")

def get_target_time():
    """Prompts the user to enter a target time for class booking.
    
    Handles user input validation for time format.
    Allows selection of specific time or any time.
    
    Returns:
        datetime.time or None: The selected time or None if any time is selected
    
    Raises:
        ValueError: If the user enters invalid time format
        KeyboardInterrupt: If the user interrupts the process
    """

    while True:
        try:
            print("-------------------------------------------------------")
            print("Enter target time (or press Enter to book any time)")
            time_str = input("Time (HH:MM AM/PM), e.g. '9:30 AM': ").strip()
            
            if not time_str:
                return None
                
            try:
                # Parse the time string to validate format
                target_time = datetime.strptime(time_str, "%I:%M %p").time()
                return target_time
            except ValueError:
                print("Invalid time format. Please use HH:MM AM/PM format (e.g. '9:30 AM')")
        except KeyboardInterrupt:
            raise
        except:
            print("Invalid input. Please try again.")

def get_instructor():
    """Prompts the user to enter an instructor name for class filtering.
    
    Allows selection of specific instructor or any instructor.
    
    Returns:
        str or None: The instructor name or None if any instructor is selected
    
    Raises:
        KeyboardInterrupt: If the user interrupts the process
    """

    while True:
        try:
            print("-------------------------------------------------------")
            print("Enter instructor name (or press Enter for any instructor)")
            instructor = input("Instructor name: ").strip()
            return instructor if instructor else None
        except KeyboardInterrupt:
            raise
        except:
            print("Invalid input. Please try again.")

def read_all_inputs():
    """Collects all necessary inputs from the user for class booking.
    
    Prompts for studio, month, instructor, day, and time preferences.
    Provides feedback after each selection.
    
    Returns:
        tuple: Contains all booking parameters:
            - str: Studio name
            - int: Target year
            - int: Start month
            - bool: Whether to book all months
            - str or None: Target day
            - datetime.time or None: Target time
            - str or None: Instructor name
    """

    # Get studio choice
    studio = get_studio_choice()
    print(f"\nSelected studio: {'Metuchen' if 'metuchen' in studio.lower() else 'Cranford'}")
    print("-------------------------------------------------------")
    print("\n")
    
    # Get month choice
    target_year, start_month, book_all_months = get_target_month()
    if book_all_months:
        print("\nBooking classes for all remaining months of the year")
    else:
        print(f"\nSearching for classes in {calendar.month_name[start_month]} {target_year}")
    print("-------------------------------------------------------")
    print("\n")
    
    # Get instructor (optional)
    instructor = get_instructor()
    if instructor:
        print(f"\nSelected instructor: {instructor}")
    else:
        print("\nBooking classes with any instructor")
    print("-------------------------------------------------------")
    print("\n")

    # Get target day of week (optional)
    target_day = get_target_day()
    if target_day:
        print(f"\nSelected day: {target_day}")
    else:
        print("\nBooking classes on any day")
    print("-------------------------------------------------------")
    print("\n")

    # Get target time (optional)
    target_time = get_target_time()
    if target_time:
        print(f"\nSelected time: {target_time.strftime('%I:%M %p')}")
    else:
        print("\nBooking classes at any time")
    print("-------------------------------------------------------")
    print("\n")

    return studio, target_year, start_month, book_all_months, target_day, target_time, instructor

def begin_reservation_system(studio, target_year, start_month, book_all_months, target_day, target_time, instructor):
    """Initiates the class reservation process with the provided parameters.
    
    Sets up the webdriver and handles the reservation process for either a single month
    or all remaining months of the year.
    
    Args:
        studio (str): The selected studio name
        target_year (int): The target year for booking
        start_month (int): The starting month for booking
        book_all_months (bool): Whether to book for all remaining months
        target_day (str or None): The target day of week or None for any day
        target_time (datetime.time or None): The target time or None for any time
        instructor (str or None): The instructor name or None for any instructor
    
    Returns:
        tuple: (driver, bool) - The webdriver instance and whether to close it
    """

    driver = init_driver()

    if studio.lower() == 'cranford':
        driver.get(HYR_CRANFORD_URL.strip())
    else:
        driver.get(HYR_METUCHEN_URL.strip())

    if book_all_months:
        # Process each remaining month of the year
        try:
            for month in range(start_month, 13):
                print("-------------------------------------------------------")
                print(f"Processing {calendar.month_name[month]} {target_year}")
                print("-------------------------------------------------------")
                print("\n")
                result = mindbody_handler.reserve_classes(driver, studio, target_year, month, target_day, target_time, instructor)

                if result is None:  # Membership expired
                    return driver, True
                if not result:  # User interrupted
                    return driver, True
                
        except KeyboardInterrupt:
            return driver, True
        
    else:
        result = mindbody_handler.reserve_classes(driver, studio, target_year, start_month, target_day, target_time, instructor)
        if result is None:  # Membership expired
            return driver, True
        
    return driver, True

def init_driver():
    """Initializes and configures the Chrome webdriver.
    
    Sets up Chrome options for optimal performance and user experience.
    
    Returns:
        webdriver.Chrome: Configured Chrome webdriver instance
    """

    options = webdriver.ChromeOptions()
    options.add_argument('--start-maximized')
    options.add_argument('--disable-gpu')
    options.add_argument('--log-level=3')  # Suppress console logging
    options.add_experimental_option('excludeSwitches', ['enable-logging'])  # Suppress console logging
    options.add_experimental_option("detach", True)
    return webdriver.Chrome(options=options)

if __name__ == "__main__":
    driver = None
    mindbody_handler = MindbodyHandler()
    try:
        print("\nYoga Class Reservation System")
        print("-------------------------------------------------------")
        print(f"    Press Ctrl+C at any time to exit safely\n")
        
        studio, target_year, start_month, book_all_months, target_day, target_time, instructor = read_all_inputs()
        driver, should_close = begin_reservation_system(studio, target_year, start_month, book_all_months, target_day, target_time, instructor)
        
    except KeyboardInterrupt:
        print("\n\nKeyboard interrupt detected. Exiting safely...")
        should_close = True

    except Exception as e:
        print(f"\nAn error occurred: {e}")
        should_close = True

    finally:
        if driver and should_close:
            print("\nClosing browser...")
            driver.quit()
            print("Browser closed. Goodbye!")
        print("-------------------------------------------------------")

