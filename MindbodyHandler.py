from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from datetime import datetime, timedelta
import calendar
import time
import os
from config.config import (
    MINDBODY_USERNAME, 
    MINDBODY_PASSWORD,
    HYR_METUCHEN_URL,
    HYR_CRANFORD_URL
)

# Global month dictionary
MONTHS = {
    "january": 1,
    "february": 2,
    "march": 3,
    "april": 4,
    "may": 5,
    "june": 6,
    "july": 7,
    "august": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12
}

class MindbodyHandler:
    def __init__(self):
        self.processed_first_days = set()  # Store first day of each week
    
    def handle_login(self, driver):
        try:

            WebDriverWait(driver, 10).until(
                EC.invisibility_of_element_located((By.ID, "pre-load-spinner"))
            )
            
            # Wait for login form
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "mb_client_session_username"))
            )
            time.sleep(1)

            # Fill in credentials
            driver.find_element(By.ID, "mb_client_session_username").send_keys(MINDBODY_USERNAME)
            driver.find_element(By.ID, "mb_client_session_password").send_keys(MINDBODY_PASSWORD)
            
            # Click sign in button
            driver.find_element(By.CSS_SELECTOR, "button.cta.signin__cta").click()
            time.sleep(2)

        except Exception as e:
            print(f"Login error: {e}")

    def check_header_title(self, driver):
        try:
            header= WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "header"))
            )

            header_bar = header.find_element(By.CLASS_NAME, "header__bar")
            header_title = header_bar.find_element(By.CLASS_NAME, "header__title")
            return header_title.text == "Sign In"
        except:
            return False
    
    def handle_booking_modal(self, driver):
        try:
            # Wait for the modal iframe to appear
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "modal-content"))
            )
            
            # Switch to the iframe
            iframe = driver.find_element(By.ID, "mindbody_branded_web_cart_modal")
            driver.switch_to.frame(iframe)
            
            # Wait for spinner to disappear
            WebDriverWait(driver, 10).until(
                EC.invisibility_of_element_located((By.ID, "pre-load-spinner"))
            )
            
            # Wait for and click the confirm button in the cart
            confirm_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a.cta.cart-cta-disable-me-on-click.cart-cta-preview-confirmation"))
            )
            time.sleep(1)
            confirm_button.click()
            time.sleep(2)

            # Check if we need to login
            if self.check_header_title(driver):
                self.handle_login(driver)
                time.sleep(2)  # Wait for login to complete
            
            # Check for error banner or thank you message
            try:
                # Check for error banner
                error_banner = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.c-banner.c-banner--error[role='alert']"))
                )
                if error_banner.is_displayed():
                    print("Class already booked or unavailable")
                    driver.switch_to.default_content()
                    driver.execute_script("""
                        var closeButton = document.querySelector('.modal-close');
                        if (closeButton) closeButton.click();
                    """)
                    time.sleep(1)
                    return False
            except:
                # Check for thank you message
                try:
                    thank_you = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "thank.thank-booking-complete"))
                    )
                    if thank_you.is_displayed():
                        print("Booking successful, closing thank you modal")
                        driver.switch_to.default_content()
                        driver.execute_script("""
                            var closeButton = document.querySelector('.modal-close');
                            if (closeButton) closeButton.click();
                        """)
                        time.sleep(1)
                        return True
                except:
                    pass  # No thank you message found
            
            # Switch back to main content
            driver.switch_to.default_content()
            return True
        
        except Exception as e:
            print(f"Error in booking modal: {e}")
            driver.switch_to.default_content()
            try:
                driver.execute_script("""
                    var closeButton = document.querySelector('.modal-close');
                    if (closeButton) closeButton.click();
                """)
                time.sleep(1)
            except:
                print("Could not close modal")
            return False

    def navigate_calendar(self, driver, target_year, target_month, calendar_container):
        try:
            if not calendar_container:
                calendar_container = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "bw-calendar-container"))
                )
                
            # Wait for calendar to load
            full_calendar = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "hc-pignose-calendar"))
            )

            # Navigate to correct month
            self.move_to_target_month(target_month, target_year, full_calendar)
            
            # Get calendar body
            full_calendar_body = full_calendar.find_element(By.CLASS_NAME, "hc-pignose-calendar-body")

            try:
                # Try to find current selected date
                current_selected = full_calendar_body.find_element(
                    By.CSS_SELECTOR, 
                    ".hc-pignose-calendar-unit-date.hc-pignose-calendar-unit-active.hc-pignose-calendar-unit-first-active"
                )
                current_row = current_selected.find_element(By.XPATH, "./ancestor::div[contains(@class, 'hc-pignose-calendar-row')]")
                calendar_rows = full_calendar_body.find_elements(By.CLASS_NAME, "hc-pignose-calendar-row")
                current_row_index = calendar_rows.index(current_row)
                
                # Get next row if it exists
                if current_row_index + 1 < len(calendar_rows):
                    next_row = calendar_rows[current_row_index + 1]
                else:
                    next_row = calendar_rows[0]  # Start from first row if at end
                    
            except:
                # If no active date, start with first row
                calendar_rows = full_calendar_body.find_elements(By.CLASS_NAME, "hc-pignose-calendar-row")
                next_row = calendar_rows[0]

            # Find first active date in the row
            first_day = next_row.find_element(
                By.CSS_SELECTOR, 
                ".hc-pignose-calendar-unit-date:not(.hc-pignose-calendar-unit-disabled)"
            )
            date_attr = first_day.get_attribute("data-date")
            
            if date_attr:
                date_obj = datetime.strptime(date_attr, "%Y-%m-%d")
                if date_obj.year == target_year and date_obj.month == target_month:
                    first_day.click()
                    time.sleep(2)
                    yield date_obj
            
        except Exception as e:
            print(f"Error navigating calendar: {e}")

    def move_to_next_week(self, driver, studio, target_year, target_month):
        try:
            calendar_container = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "bw-calendar-container"))
            )

            full_cal_field = calendar_container.find_element(By.CLASS_NAME, "bw-fullcal__field")

            if studio.lower() == 'cranford':
                datepicker = full_cal_field.find_element(By.CLASS_NAME, "bw-datepicker")
                datepicker_button = datepicker.find_element(By.CLASS_NAME, "bw-datepicker__button")
                datepicker_button.click()
            else:
                full_cal_button = calendar_container.find_element(By.CLASS_NAME, "bw-fullcal-button")
                full_cal_button.click()
            time.sleep(2)

            # Use the generator from navigate_calendar
            for date_obj in self.navigate_calendar(driver, target_year, target_month, calendar_container):
                ok_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "a.hc-pignose-calendar-button.hc-pignose-calendar-button-apply"))
                )
                ok_button.click()
                time.sleep(1)
                # We only need the first date returned
                return date_obj
            
        except Exception as e:
            print(f"Error moving to next week: {e}")
            return None

    def move_to_target_month(self, target_month, target_year, full_calendar):
        try:

            while True:
                # Get current month/year from calendar header
                try:
                    # Print raw elements for debugging
                    top_date = full_calendar.find_element(By.CLASS_NAME, "hc-pignose-calendar-top-date")
                    month_element = top_date.find_element(By.CLASS_NAME, "hc-pignose-calendar-top-month")
                    year_element = top_date.find_element(By.CLASS_NAME, "hc-pignose-calendar-top-year")
                    
                    current_month = month_element.get_attribute('textContent').strip()
                    current_year = year_element.get_attribute('textContent').strip()
                    
                    # Convert month name to number using our MONTHS dictionary
                    current_month_num = MONTHS[current_month.lower()]
                    current_year_num = int(current_year)
                    # If we're in the right month, break
                    if current_year_num == target_year and current_month_num == target_month:
                        break
                        
                    # If target date is after current date, click next
                    if (target_year > current_year_num) or (target_year == current_year_num and target_month > current_month_num):
                        next_button = full_calendar.find_element(By.CSS_SELECTOR, "a.hc-pignose-calendar-top-nav.hc-pignose-calendar-top-next")
                        next_button.click()
                    else:
                        prev_button = full_calendar.find_element(By.CSS_SELECTOR, "a.hc-pignose-calendar-top-nav.hc-pignose-calendar-top-prev")
                        prev_button.click()
                    time.sleep(1)
                    
                except Exception as inner_e:
                    print(f"Error processing calendar elements: {inner_e}")
                    # Print raw element text for debugging
                    print(f"Raw month element: {month_element}")
                    print(f"Raw year element: {year_element}")
                    raise
                
        except Exception as e:
            print(f"Error navigating to month: {e}")
    
    def get_sessions_from_days(self, driver, days, target_year, target_month, target_day=None, target_time=None, instructor=None):                                              
        for day in days:
            try:
                # Get date from the date div
                date_div = day.find_element(By.CLASS_NAME, "bw-widget__date")
                date_text = date_div.text
                if not date_text:
                    continue
                
                # Parse the date text
                try:
                    # Convert "Monday, December 30" to datetime object
                    class_date = datetime.strptime(date_text, "%A, %B %d")
                    # Add year since it's not in the text
                    class_date = class_date.replace(year=target_year)
                except ValueError:
                    print(f"Error parsing date: {date_text}")
                    continue
                
                # Check if day is in target month
                if class_date.year == target_year and class_date.month == target_month:
                    # Find sessions within this day
                    sessions = day.find_elements(By.CLASS_NAME, "bw-session")
                    
                    self.book_sessions(driver, sessions, class_date, target_day, target_time, instructor)

            except Exception as e:
                print(f"Error processing day: {e}")
                continue
    
    def book_sessions(self, driver, sessions, class_date, target_day=None, target_time=None, instructor=None):
        for session in sessions:
            try:
                # Get session basics
                session_basics = session.find_element(By.CLASS_NAME, "bw-session__basics")
                
                # Check if this is the instructor's class
                staff_name = session_basics.find_element(By.CLASS_NAME, "bw-session__staff").text
                session_name = session_basics.find_element(By.CLASS_NAME, "bw-session__name").text
                
                # Get time from the correct HTML structure
                session_info = session_basics.find_element(By.CLASS_NAME, "bw-session__info")
                session_time_div = session_info.find_element(By.CLASS_NAME, "bw-session__time")
                session_time_col = session_time_div.find_element(By.CLASS_NAME, "bw-session__column")
                session_time_span = session_time_col.find_element(By.CLASS_NAME, "hc_time")

                session_start_time = session_time_span.find_element(By.CLASS_NAME, "hc_starttime").text
                session_end_time = session_time_span.find_element(By.CLASS_NAME, "hc_endtime").text
                
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
                
                print("\n-------------------------------------------------------")
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
                cart_button = session.find_element(By.CLASS_NAME, "bw-widget__cart_button")
                cart_button.click()
                time.sleep(2)
                    
                # Handle the booking modal
                if self.handle_booking_modal(driver):
                    print(f"Successfully booked class for {class_date.strftime('%A, %B %d, %Y')} at {session_start_time} - {session_end_time}")
                    # Continue with next session instead of returning
                    continue
                print("-------------------------------------------------------")
        
            except Exception as e:
                print(f"Error processing session: {e}")
                continue

    def get_first_day_of_week(self, days, target_year):
        try:
            first_day = days[0]
            date_div = first_day.find_element(By.CLASS_NAME, "bw-widget__date")
            date_text = date_div.text
            
            if date_text:
                try:
                    first_date = datetime.strptime(date_text, "%A, %B %d")
                    first_date = first_date.replace(year=target_year)
                    return first_date.strftime("%Y-%m-%d")
                except ValueError:
                    print(f"Error parsing first day date: {date_text}")
            return None
        except Exception as e:
            print(f"Error getting first day of week: {e}")
            return None
            
    def reserve_classes(self, driver, studio, target_year, target_month, target_day=None, target_time=None, instructor=None):
        try:
            if studio.lower() == 'cranford':
                driver.get(HYR_CRANFORD_URL.strip())
            else:
                driver.get(HYR_METUCHEN_URL.strip())
            
            while True:
                try:
                    # Wait for sessions container
                    sessions_container = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "bw-widget__sessions"))
                    )
                
                    # Find all days
                    days = sessions_container.find_elements(By.CLASS_NAME, "bw-widget__day")
                    
                    # Check if we've seen this week before
                    first_day_key = self.get_first_day_of_week(days, target_year)
                    if first_day_key:
                        if first_day_key in self.processed_first_days:
                            print(f"\nReached a previously processed week")
                            return True
                        self.processed_first_days.add(first_day_key)
                    
                    self.get_sessions_from_days(driver, days, target_year, target_month, target_day, target_time, instructor)

                    # After processing current week, move to next week
                    print("Moving to next week...")
                    next_week_date = self.move_to_next_week(driver, studio, target_year, target_month) 
                    time.sleep(5)
                    if not next_week_date:
                        print(f"\nNo more weeks found in {calendar.month_name[target_month]} {target_year}")
                        return True

                except KeyboardInterrupt:
                    raise
                except Exception as e:
                    print(f"Error in week processing: {e}")
                    continue
                
        except KeyboardInterrupt:
            print("\nInterrupted by user. Stopping gracefully...")
            return False
        except Exception as e:
            print(f"Error in reserve_classes: {e}")
            return False
    