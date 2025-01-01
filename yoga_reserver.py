from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from datetime import datetime, timedelta
import calendar
import time
import os
from utils.mindbody_handler import MindbodyHandler


def get_studio_choice():
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

def init_driver():
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
        
        driver = init_driver()

        if book_all_months:
            # Process each remaining month of the year
            try:
                for month in range(start_month, 13):
                    print("-------------------------------------------------------")
                    print(f"Processing {calendar.month_name[month]} {target_year}")
                    print("-------------------------------------------------------")
                    print("\n")
                    result = mindbody_handler.reserve_classes(driver, studio, target_year, month, target_day, target_time, instructor)
                    if not result:  # If reserve_classes returns False, user interrupted
                        break
            except KeyboardInterrupt:
                raise  # Re-raise to be caught by outer try block
        else:
            mindbody_handler.reserve_classes(driver, studio, target_year, start_month, target_day, target_time, instructor)
        
    except KeyboardInterrupt:
        print("\n\nKeyboard interrupt detected. Exiting safely...")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
    finally:
        if driver:
            print("\nClosing browser...")
            driver.quit()
            print("Browser closed. Goodbye!")
        print("-------------------------------------------------------")

