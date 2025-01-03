from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import calendar
import time

from utilities.mindbody_utils.modal_utils import ModalUtils
from utilities.mindbody_utils.calendar_utils import CalendarUtils
from resources.html_selectors import *

# Global month dictionary
MONTHS = {
    "january": (1, 31),
    "february": (2, 28),  # Note: Will need special handling for leap years
    "march": (3, 31),
    "april": (4, 30),
    "may": (5, 31),
    "june": (6, 30),
    "july": (7, 31),
    "august": (8, 31),
    "september": (9, 30),
    "october": (10, 31),
    "november": (11, 30),
    "december": (12, 31)
}

class MindbodyHandler:
    """Class to handle all Mindbody website interactions"""

    def __init__(self):
        """Initialize the MindbodyHandler with an empty set of processed dates"""
        self.processed_dates = set()  # Store processed dates
        self.modal_utils = ModalUtils()
        self.calendar_utils = CalendarUtils()
    
    def is_month_changed_in_batch(self, driver, studio, target_month, target_year, current_month_name, current_month, current_year, class_day):
        """Check if we need to change months while processing a batch of days.
        
        Args:
            driver: Selenium webdriver instance
            studio: Studio name ('cranford' or 'metuchen')
            target_month: Month we're targeting (1-12)
            target_year: Year we're targeting
            current_month_name: Name of the current month (lowercase)
            current_month: Current month number (1-12)
            current_year: Current year
            class_day: Day of the month we're processing
            
        Returns:
            bool: True if we should stop processing current batch, False otherwise
        """
         
         # If we've reached the end of the month, return False
        
        if current_month != target_month or current_year != target_year:
            self.calendar_utils.move_to_next_week(driver, studio, target_month, target_year, current_month, current_year, self.processed_dates)
            print("\n-------------------------------------------------------")
            print("Month changed while processing batch")
            print("-------------------------------------------------------")
            return True
        
        elif class_day == MONTHS[current_month_name][1]:

            if current_month == 12:
                current_month = 0
            else:
                current_month += 1

            self.calendar_utils.move_to_next_week(driver, studio, current_month, current_year, target_month, target_year, self.processed_dates)
            print("\n-------------------------------------------------------")
            print("Month changed while processing batch")
            print("-------------------------------------------------------")
            return True
        
        return False
                    
    def process_days(self, driver, studio, target_year, target_month, target_day=None, target_time=None, instructor=None):
        """Helper method to process and book sessions for given days
        
        Args:
            driver: Selenium webdriver instance
            days: List of day elements to process
            target_year: Year to filter by
            target_month: Month to filter by
            target_day: Optional day of week to filter by
            target_time: Optional time to filter by
            instructor: Optional instructor name to filter by
            
        Returns:
            Boolean indicating if processing should continue
        """
        
        sessions_container = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, SESSIONS_CONTAINER))
        )
        time.sleep(2)
                
        # Find all days in the current week
        days = sessions_container.find_elements(By.CLASS_NAME, SESSION_DAY)
        
        if not days:
            print("-------------------------------------------------------")
            print("No classes found in current week")
            print("-------------------------------------------------------") 
            print("\n")
            return True
        
        for day in days:
            try:
                # Check if this is an empty day
                day_classes = day.get_attribute("class")
                if "bw-widget__day--empty" in day_classes:
                    date_div = day.find_element(By.CLASS_NAME, SESSION_DATE)
                    print("-------------------------------------------------------")
                    print(f"No classes for {date_div.text}")
                    print("-------------------------------------------------------")
                    continue

                # Get date from the date div
                date_div = day.find_element(By.CLASS_NAME, SESSION_DATE)
                date_text = date_div.text
                current_month_name = date_text.split(", ")[1].split(" ")[0].lower()
                if not date_text:
                    continue
                
                # Parse the date text
                try:
                    # Convert "Monday, December 30" to datetime object
                    class_date = datetime.strptime(date_text, "%A, %B %d")
                    class_day = class_date.day

                    # Add year since it's not in the text
                    class_date = class_date.replace(year=target_year)

                    # Get current month and year
                    current_month = class_date.month
                    current_year = class_date.year
                    
                    # Check if we've reached the end of the month
                    early_month_change = self.is_month_changed_in_batch(driver, studio, target_month, target_year, current_month_name, current_month, current_year, class_day)
                    if early_month_change:
                        return False
                    
                    # Check if we've already processed this date
                    date_key = class_date.strftime("%Y-%m-%d")
                    if date_key in self.processed_dates:
                        print("\n-------------------------------------------------------")
                        print(f"Already processed {date_text}, skipping...")
                        print("-------------------------------------------------------")
                        continue
                    self.processed_dates.add(date_key)
                    
                except ValueError:
                    print(f"Error parsing date: {date_text}")
                    continue
                
                # Check if day is in target month
                if class_date.year == target_year and class_date.month == target_month:
                    # Find sessions within this day
                    sessions = day.find_elements(By.CLASS_NAME, SESSION)
                    self.book_sessions(driver, sessions, class_date, target_day, target_time, instructor)

            except Exception as e:
                print(f"Error processing day: {e}")
                continue

        return True

    def book_sessions(self, driver, sessions, class_date, target_day=None, target_time=None, instructor=None):
        """Helper method to book individual sessions
        
        Args:
            driver: Selenium webdriver instance
            sessions: List of session elements to process
            class_date: Date of the class
            target_day: Optional day of week to filter by
            target_time: Optional time to filter by
            instructor: Optional instructor name to filter by
        """
        
        for session in sessions:
            try:
                # Get session basics
                session_basics = session.find_element(By.CLASS_NAME, SESSION_BASICS)
                
                # Check if this is the instructor's class
                staff_name = session_basics.find_element(By.CLASS_NAME, SESSION_STAFF).text
                session_name = session_basics.find_element(By.CLASS_NAME, SESSION_NAME).text
                
                # Get time from the correct HTML structure
                session_info = session_basics.find_element(By.CLASS_NAME, SESSION_INFO)
                session_time_div = session_info.find_element(By.CLASS_NAME, SESSION_TIME)
                session_time_col = session_time_div.find_element(By.CLASS_NAME, SESSION_COLUMN)
                session_time_span = session_time_col.find_element(By.CLASS_NAME, SESSION_TIME_SPAN)

                session_start_time = session_time_span.find_element(By.CLASS_NAME, SESSION_START_TIME).text
                session_end_time = session_time_span.find_element(By.CLASS_NAME, SESSION_END_TIME).text
                
                # Only check time if target_time is specified
                if target_time:
                    try:
                        session_time_obj = datetime.strptime(session_start_time, "%I:%M %p").time()
                        if session_time_obj != target_time:
                            continue
                    except ValueError:
                        print(f"Error parsing session time: {session_start_time}")
                        continue
                
                # Only check day if target_day is specified
                if target_day and class_date.strftime("%A") != target_day:
                    continue
                
                # Only check instructor if specified
                if instructor and instructor not in staff_name:
                    continue
                
                print("\n----------------------------------------------")
                print("Found a class!")
                print(f" Class Information:")
                print(f"    Class: {session_name}")
                print(f"    Date: {class_date.strftime('%A, %B %d, %Y')}")
                print(f"    Time: {session_start_time} - {session_end_time}")
                print(f"    Instructor: {staff_name}")
                print("\nAttempting to book class...")
                
                # Click to expand details
                session_basics.click()
                time.sleep(2)
                    
                # Find and click book button
                cart_button = session.find_element(By.CLASS_NAME, SESSION_CART_BUTTON)
                cart_button.click()
                time.sleep(2)
                    
                # Handle the booking modal
                if self.modal_utils.handle_booking_modal(driver):
                    print(f"Successfully booked class for {class_date.strftime('%A, %B %d, %Y')} at {session_start_time} - {session_end_time}")
                    # Continue with next session instead of returning
                    continue
                print("----------------------------------------------")
        
            except Exception as e:
                print(f"Error processing session: {e}")
                continue

    def reserve_classes(self, driver, studio, target_year, target_month, target_day=None, target_time=None, instructor=None):
        """Main method to handle class reservation process
        
        Args:
            driver: Selenium webdriver instance
            studio: Studio name ('cranford' or 'metuchen')
            target_year: Year to book classes for
            target_month: Month to book classes for
            target_day: Optional day of week to filter by
            target_time: Optional time to filter by
            instructor: Optional instructor name to filter by
            
        Returns:
            Boolean indicating success/failure
        """
       
        try:
            
            while True:
                
                continue_processing = self.process_days(driver, studio, target_year, target_month, target_day, target_time, instructor)

                if not continue_processing:
                    print("\n-------------------------------------------------------")
                    print(f"Finished processing {calendar.month_name[target_month]} {target_year}")
                    print("-------------------------------------------------------")
                    print("\n")
                    return True
                 
                self.calendar_utils.move_to_next_week(driver, studio, target_month, target_year, None, None, self.processed_dates) 

                time.sleep(5)
                
        except KeyboardInterrupt:
            print("\nInterrupted by user. Stopping gracefully...")
            return False
        
        except Exception as e:
            print(f"Error in reserve_classes: {e}")
            return False
    
