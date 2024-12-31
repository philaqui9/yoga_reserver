from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from datetime import datetime, timedelta
import calendar
import time
import os
from MindbodyHandler import MindbodyHandler


def get_studio_choice():
    while True:
        try:
            print("Available studios:")
            print("1. Metuchen")
            print("2. Cranford")
            
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
            
            # Calculate next month and year
            next_month = current_month + 1 if current_month < 12 else 1
            next_year = current_year if current_month < 12 else current_year + 1
            
            print("Available months:")
            print(f"1. Current month ({calendar.month_name[current_month]} {current_year})")
            print(f"2. Next month ({calendar.month_name[next_month]} {next_year})")
            
            choice = int(input("\nEnter 1 for current month or 2 for next month: "))
            
            if choice == 1:
                return current_year, current_month
            elif choice == 2:
                return next_year, next_month
            else:
                print("Invalid choice. Please enter 1 or 2.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def get_target_day():
    days = {
        0: "Any day",
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
            print("Available days:")
            for num, day in days.items():
                print(f"{num}. {day}")
            
            choice = int(input("\nEnter the number for the day of the week (0-7): "))
            
            if 0 <= choice <= 7:
                return None if choice == 0 else days[choice]
            else:
                print("Invalid choice. Please enter a number between 0 and 7.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def get_target_time():
    while True:
        try:
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
            print("\nEnter instructor name (or press Enter for any instructor)")
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
        print("Press Ctrl+C at any time to exit safely\n")
        
        # Get studio choice
        studio = get_studio_choice()
        print(f"\nSelected studio: {'Metuchen' if 'metuchen' in studio.lower() else 'Cranford'}")
        print("-------------------------------------------------------")
        
        # Get month choice
        target_year, target_month = get_target_month()
        print(f"\nSearching for classes in {calendar.month_name[target_month]} {target_year}")
        print("-------------------------------------------------------")
        
        # Get instructor (optional)
        instructor = get_instructor()
        if instructor:
            print(f"\nSelected instructor: {instructor}")
        else:
            print("\nBooking classes with any instructor")
        print("-------------------------------------------------------")
        
        # Get target day of week (optional)
        target_day = get_target_day()
        if target_day:
            print(f"\nSelected day: {target_day}")
        else:
            print("\nBooking classes on any day")
        print("-------------------------------------------------------")

        # Get target time (optional)
        target_time = get_target_time()
        if target_time:
            print(f"\nSelected time: {target_time.strftime('%I:%M %p')}")
        else:
            print("\nBooking classes at any time")
        print("-------------------------------------------------------")
        
        driver = init_driver()

        mindbody_handler.reserve_classes(driver, studio, target_year, target_month, target_day, target_time, instructor)
        
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

