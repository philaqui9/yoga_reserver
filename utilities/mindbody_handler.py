from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from datetime import datetime, timedelta
import calendar
import time
from config.config import (
    MINDBODY_USERNAME, 
    MINDBODY_PASSWORD
)
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
    
    def handle_login(self, driver):
        """Helper method to handle login to Mindbody"""

        try:

            print(f"    Logging into Mindbody...")

            # Wait for loading animation to disappear
            WebDriverWait(driver, 10).until(
                EC.invisibility_of_element_located((By.ID, MODAL_SPINNER))
            )
            
            # Wait for login form
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, LOGIN_USERNAME))
            )
            time.sleep(1)

            # Fill in credentials
            driver.find_element(By.ID, LOGIN_USERNAME).send_keys(MINDBODY_USERNAME)
            driver.find_element(By.ID, LOGIN_PASSWORD).send_keys(MINDBODY_PASSWORD)
            
            # Click sign in button
            driver.find_element(By.CSS_SELECTOR, LOGIN_BUTTON).click()
            time.sleep(2)

            print(f"    Successfully logged into Mindbody!")

        except Exception as e:
            print(f"Login error: {e}")

    def is_modal_header_title_login(self, driver):
        """Helper method to check if the current modal header is a login prompt"""

        try:

            # Wait for header to load
            header = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, LOGIN_HEADER))
            )

            # Get header bar and title
            header_bar = header.find_element(By.CLASS_NAME, LOGIN_HEADER_BAR)
            header_title = header_bar.find_element(By.CLASS_NAME, LOGIN_HEADER_TITLE)

            # Check if the title is "Sign In"
            return header_title.text == "Sign In"
        except:
            return False
    
    def handle_booking_modal(self, driver):
        """Helper method to handle the booking confirmation modal"""
        
        try:

            # Wait for and switch to modal iframe
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, MODAL_CONTENT))
            )
            iframe = driver.find_element(By.ID, MODAL_IFRAME)
            driver.switch_to.frame(iframe)
            
            # Wait for spinner to disappear
            WebDriverWait(driver, 10).until(
                EC.invisibility_of_element_located((By.ID, MODAL_SPINNER))
            )
            
            # Click confirm button
            confirm_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, f"a.{MODAL_CONFIRM_BASE}.{MODAL_CONFIRM_DISABLE}.{MODAL_CONFIRM_PREVIEW}"))
            )
            time.sleep(1)
            confirm_button.click()
            time.sleep(2)

            # Handle login if needed
            if self.is_modal_header_title_login(driver):
                self.handle_login(driver)
                time.sleep(2)
            
            # Check for error banner
            try:
                error_banner = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, MODAL_ERROR_BANNER))
                )
                if error_banner.is_displayed():
                    return self.close_modal(driver, "Class already booked or unavailable", False)
            except:
                pass

            # Check for thank you message
            try:
                thank_you = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CLASS_NAME, MODAL_THANK_YOU))
                )
                if thank_you.is_displayed():
                    return self.close_modal(driver, "Successfully booked class!", True)
            except:
                pass

            # If no error or thank you message found, assume success
            driver.switch_to.default_content()
            return True
            
        except Exception as e:
            print(f"Error in booking modal: {e}")
            return self.close_modal(driver, None, False)

    def close_modal(self, driver, message=None, success=False):
        """Helper method to close the modal and return status
        
        Args:
            driver: Selenium webdriver instance
            message: Optional message to print before closing
            success: Boolean indicating if operation was successful
            
        Returns:
            Boolean indicating success/failure
        """
        
        # Switch back to main content
        driver.switch_to.default_content()
        try:
            if message:
                print(message)

            # Click close button
            driver.execute_script(f"""
                var closeButton = document.querySelector('.{MODAL_CLOSE}');
                if (closeButton) closeButton.click();
            """)
            time.sleep(1)
            
        except:
            print("Could not close modal")
        return success

    def open_calendar(self, driver, studio):
        """Helper method to open the calendar for either studio
        
        Args:
            driver: Selenium webdriver instance
            studio: Studio name ('cranford' or 'metuchen')
            
        Returns:
            None
        """

        calendar_container = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, CALENDAR_CONTAINER))
            )

        full_cal_field = calendar_container.find_element(By.CLASS_NAME, FULLCAL_FIELD)

        if studio.lower() == 'cranford':
            datepicker = full_cal_field.find_element(By.CLASS_NAME, DATEPICKER)
            datepicker_button = datepicker.find_element(By.CLASS_NAME, DATEPICKER_BUTTON)
            datepicker_button.click()
            time.sleep(2)
        else:  # Metuchen
            full_cal_button = calendar_container.find_element(By.CLASS_NAME, FULLCAL_BUTTON)
            full_cal_button.click()
            time.sleep(2)

    def move_to_next_date_in_calendar(self, driver, target_year, target_month, full_calendar):
        """Helper method to select the next available date in the calendar and apply it
        
        Args:
            driver: Selenium webdriver instance
            target_year: Year to filter by
            target_month: Month to filter by
            full_calendar: Calendar element
            
        Returns:
            datetime object of selected date or None if no valid date found
        """

        # Use the generator from navigate_calendar
        for date_obj in self.find_next_unprocessed_date_in_calendar(driver, target_year, target_month, full_calendar):
            ok_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, f"a.{CALENDAR_OK_BUTTON}.{CALENDAR_OK_BUTTON_APPLY}"))
            )
            ok_button.click()
            time.sleep(2)
            return date_obj
            
    def find_next_unprocessed_date_in_calendar(self, driver, target_year, target_month, full_calendar=None):
        """Helper method to find and select the next unprocessed date in the calendar view
        
        Args:
            driver: Selenium webdriver instance
            target_year: Year to filter by
            target_month: Month to filter by
            calendar_container: Calendar container element
            isMovingToNextWeek: Boolean indicating if we're moving to next week
            
        Returns:
            datetime object of selected date or None if no valid date found
        """
        
        try:

            print("\n-------------------------------------------------------")
            print(f"Finding next unprocessed date in calendar...")
            print("-------------------------------------------------------")

            # Wait for calendar to load
            if not full_calendar:
                full_calendar = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, FULL_CALENDAR))
                )
            
            # Get calendar body
            full_calendar_body = full_calendar.find_element(By.CLASS_NAME, CALENDAR_BODY)
            calendar_rows = full_calendar_body.find_elements(By.CLASS_NAME, CALENDAR_ROW)

            # Find the current selected date
            try:
                current_selected = full_calendar_body.find_element(
                    By.CSS_SELECTOR, 
                    f".{CALENDAR_DATE}.{CALENDAR_UNIT_ACTIVE}.{CALENDAR_UNIT_FIRST_ACTIVE}"
                )
                current_row = current_selected.find_element(By.XPATH, f"./ancestor::div[contains(@class, '{CALENDAR_ROW}')]")
                current_row_index = calendar_rows.index(current_row)
            except:
                # If no date is selected, start from the first row
                current_row_index = -1

            # Look through each row starting from the current row
            for row_index in range(current_row_index + 1, len(calendar_rows)):
                row = calendar_rows[row_index]
                dates = row.find_elements(By.CLASS_NAME, CALENDAR_DATE)
                
                for date in dates:
                    # Skip disabled dates
                    if CALENDAR_UNIT_DISABLED in date.get_attribute("class"):
                        continue
                    
                    # Get the date value
                    date_attr = date.get_attribute("data-date")
                    if date_attr:
                        date_obj = datetime.strptime(date_attr, "%Y-%m-%d")
                        
                        # Check if this date is in our target month and year
                        if date_obj.year == target_year and date_obj.month == target_month:
                            # Check if we've already processed this date
                            date_key = date_obj.strftime("%Y-%m-%d")
                            if date_key not in self.processed_dates:
                                date.click()
                                time.sleep(1)
                                
                                yield date_obj
                                return
            
        except Exception as e:
            print(f"Error navigating calendar: {e}")
            return

    def get_current_month_and_year(self, full_calendar):
        """Helper method to get the current month and year from the calendar header
        
        Args:
            driver: Selenium webdriver instance
            
        Returns:
            Tuple containing current month and year
        """
        
        top_date = full_calendar.find_element(By.CLASS_NAME, CALENDAR_TOP_DATE)
        month_element = top_date.find_element(By.CLASS_NAME, CALENDAR_TOP_MONTH)
        year_element = top_date.find_element(By.CLASS_NAME, CALENDAR_TOP_YEAR)
        
        current_month = month_element.get_attribute('textContent').strip()
        current_year = year_element.get_attribute('textContent').strip()

        current_month_num = MONTHS[current_month.lower()][0]  # Get first value of tuple
        current_year_num = int(current_year)

        return current_month_num, current_year_num

    def move_to_next_month(self, target_month, target_year, current_month, current_year, full_calendar):
        """Navigate to the next month in the calendar if needed.
        
        Args:
            target_month (int): Month to navigate to (1-12)
            target_year (int): Year to navigate to
            current_month (int): Current month number (1-12)
            current_year (int): Current year
            full_calendar (WebElement): Calendar element to navigate
            
        Returns:
            None: Method returns early if navigation is performed
        """

        if current_month and current_year:
            if current_month != target_month or current_year != target_year:
                while current_month != target_month or current_year != target_year:

                    print("\n------------------------------------------------------")
                    print("Moving to next month...")
                    print("------------------------------------------------------")

                    next_button = full_calendar.find_element(By.CSS_SELECTOR, f"a.{CALENDAR_TOP_NAV}.{CALENDAR_TOP_NEXT}")
                    next_button.click()
                    time.sleep(1)

                    current_month, current_year = self.get_current_month_and_year(full_calendar)

                return True
            
        
        return False

    def move_to_next_week(self, driver, studio, target_month, target_year, current_month, current_year):
        """Helper method to navigate calendar to target month and select first available day
        
        Args:`
            driver: Selenium webdriver instance
            target_month: Month to navigate to
            target_year: Year to navigate to
            full_calendar: Calendar element
            
        Returns:
            Boolean indicating success/failure
        """
        
        try:

            self.open_calendar(driver, studio)

             # Wait for calendar to load and navigate to target month
            full_calendar = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, FULL_CALENDAR))
            )

            if self.move_to_next_month(target_month, target_year, current_month, current_year, full_calendar):
                self.move_to_next_date_in_calendar(driver, target_year, target_month, full_calendar)
                return
            
            try:
                
                current_month, current_year = self.get_current_month_and_year(full_calendar)
                    
                self.move_to_next_month(target_month, target_year, current_month, current_year, full_calendar)
               
                print("\n------------------------------------------------------")
                print("Moving to the next unprocessed date...")
                print("------------------------------------------------------")
                next_date = self.move_to_next_date_in_calendar(driver, target_year, target_month, full_calendar)
                if next_date:
                    return next_date


            except Exception as inner_e:
                print(f"Error processing calendar elements: {inner_e}")
                raise
                
        except Exception as e:
            print(f"Error navigating to next unprocessed date: {e}")
            return False
    
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
            self.move_to_next_week(driver, studio, target_month, target_year, current_month, current_year)
            print("\n-------------------------------------------------------")
            print("Month changed while processing batch")
            print("-------------------------------------------------------")
            return True
        
        elif class_day == MONTHS[current_month_name][1]:

            if current_month == 12:
                current_month = 0
            else:
                current_month += 1

            self.move_to_next_week(driver, studio, current_month, current_year, target_month, target_year)
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
                if self.handle_booking_modal(driver):
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
                 
                self.move_to_next_week(driver, studio, target_month, target_year, None, None) 

                time.sleep(5)
                
        except KeyboardInterrupt:
            print("\nInterrupted by user. Stopping gracefully...")
            return False
        
        except Exception as e:
            print(f"Error in reserve_classes: {e}")
            return False
    
