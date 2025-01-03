from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
from datetime import datetime
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

class CalendarUtils:
    def __init__(self):
        pass

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

    def move_to_next_date_in_calendar(self, driver, target_year, target_month, full_calendar, processed_dates):
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
        for date_obj in self.find_next_unprocessed_date_in_calendar(driver, target_year, target_month, processed_dates, full_calendar):
            ok_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, f"a.{CALENDAR_OK_BUTTON}.{CALENDAR_OK_BUTTON_APPLY}"))
            )
            ok_button.click()
            time.sleep(2)
            return date_obj
            
    def find_next_unprocessed_date_in_calendar(self, driver, target_year, target_month, processed_dates, full_calendar=None):
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
                            if date_key not in processed_dates:
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

    def move_to_next_week(self, driver, studio, target_month, target_year, current_month, current_year, processed_dates):
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
                self.move_to_next_date_in_calendar(driver, target_year, target_month, full_calendar, processed_dates)
                return
            
            try:
                
                current_month, current_year = self.get_current_month_and_year(full_calendar)
                    
                self.move_to_next_month(target_month, target_year, current_month, current_year, full_calendar)
               
                print("\n------------------------------------------------------")
                print("Moving to the next unprocessed date...")
                print("------------------------------------------------------")
                next_date = self.move_to_next_date_in_calendar(driver, target_year, target_month, full_calendar, processed_dates)
                if next_date:
                    return next_date


            except Exception as inner_e:
                print(f"Error processing calendar elements: {inner_e}")
                raise
                
        except Exception as e:
            print(f"Error navigating to next unprocessed date: {e}")
            return False
    

    