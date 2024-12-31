from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
import calendar
import time
import os
from config.config import (
    MINDBODY_USERNAME, 
    MINDBODY_PASSWORD,
    HYR_INSTRUCTOR,
    HYR_METUCHEN_URL,
    HYR_CRANFORD_URL
)
from selenium.webdriver.common.keys import Keys

# Global month dictionary
MONTHS = {
    1: "January",
    2: "February",
    3: "March",
    4: "April",
    5: "May",
    6: "June",
    7: "July",
    8: "August",
    9: "September",
    10: "October",
    11: "November",
    12: "December"
}

def get_studio_choice():
    while True:
        try:
            print("\nAvailable studios:")
            print("1. Metuchen")
            print("2. Cranford")
            
            choice = int(input("\nEnter 1 for Metuchen or 2 for Cranford: "))
            
            if choice == 1:
                return HYR_METUCHEN_URL
            elif choice == 2:
                return HYR_CRANFORD_URL
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
            
            print("\nAvailable months:")
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

def init_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--start-maximized')
    options.add_argument('--disable-gpu')
    options.add_experimental_option("detach", True)
    return webdriver.Chrome(options=options)

def handle_login(driver):
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

def check_header_title(driver):
    try:
        header= WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "header"))
        )

        header_bar = header.find_element(By.CLASS_NAME, "header__bar")
        header_title = header_bar.find_element(By.CLASS_NAME, "header__title")
        return header_title.text == "Sign In"
    except:
        return False

def handle_booking_modal(driver):
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
        if check_header_title(driver):
            handle_login(driver)
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

def navigate_calendar(driver, target_year, target_month, calendar_container):
    try:
        print("Navigating calendar")
        if not calendar_container:
            calendar_container = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "bw-calendar-container"))
            )
        print("Calendar container found")
            
        # Wait for calendar to load
        full_calendar = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "hc-pignose-calendar"))
        )

        # Navigate to correct month
        move_to_target_month(target_month, full_calendar)
        
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
            print("No active date found, starting from first row")
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
                print(f"Selecting first day: {date_obj.strftime('%Y-%m-%d')}")
                first_day.click()
                time.sleep(2)
                yield date_obj
        
    except Exception as e:
        print(f"Error navigating calendar: {e}")

def move_to_next_week(driver, target_year, target_month):
    print("Moving to next week")
    try:
        calendar_container = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "bw-calendar-container"))
        )

        print("Calendar container found")
        full_cal_field = calendar_container.find_element(By.CLASS_NAME, "bw-fullcal__field")
        datepicker = full_cal_field.find_element(By.CLASS_NAME, "bw-datepicker")

        datepicker_button = datepicker.find_element(By.CLASS_NAME, "bw-datepicker__button")
        datepicker_button.click()
        time.sleep(2)

        print("Opening calendar")
        # Use the generator from navigate_calendar
        for date_obj in navigate_calendar(driver, target_year, target_month, calendar_container):
            print("loopin")
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

def move_to_target_month(target_month, full_calendar):
    try:
        
        print("Calendar found")

        while True:
            # Get current month/year from calendar header
            print("Getting current month/year")
            try:
                # Print raw elements for debugging
                top_date = full_calendar.find_element(By.CLASS_NAME, "hc-pignose-calendar-top-date")
                month_element = top_date.find_element(By.CLASS_NAME, "hc-pignose-calendar-top-month")
                year_element = top_date.find_element(By.CLASS_NAME, "hc-pignose-calendar-top-year")
                
                current_month = month_element.get_attribute('textContent').strip()
                current_year = year_element.get_attribute('textContent').strip()
                
                print(f"Current calendar shows: {current_month} {current_year}")
                
                # Convert month name to number using our MONTHS dictionary
                current_month_num = [k for k, v in MONTHS.items() if v == current_month][0]
                current_year_num = int(current_year)
                
                print(f"Current month: {current_month_num}, Target month: {target_month}")
                # If we're in the right month, break
                if current_year_num == target_year and current_month_num == target_month:
                    print(f"Found target month: {MONTHS[target_month]} {target_year}")
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



        print("Calendar container found")

def get_metuchen_sessions(driver, target_year, target_month):
    try:
        driver.get(HYR_METUCHEN_URL.strip())
        time.sleep(3)
        
        # Navigate through each day in the calendar
        for current_date in navigate_calendar(driver, target_year, target_month):
            print(f"\nProcessing date: {current_date.strftime('%Y-%m-%d')}")
            
            # Wait for sessions to load
            sessions_container = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "bw-widget__sessions"))
            )
            
            sessions = sessions_container.find_elements(By.CLASS_NAME, "bw-session")
            print(f"Found {len(sessions)} sessions")
            
            for session in sessions:
                try:
                    basics = session.find_element(By.CLASS_NAME, "bw-session__basics")
                    staff_name = basics.find_element(By.CLASS_NAME, "bw-session__staff").text
                    
                    if HYR_INSTRUCTOR in staff_name:
                        print(f"Found class with {staff_name}")
                        print("Booking class...")
                        
                        basics.click()
                        time.sleep(2)
                        
                        cart_button = session.find_element(By.CLASS_NAME, "bw-widget__cart_button")
                        cart_button.click()
                        time.sleep(2)
                        
                        if handle_booking_modal(driver):
                            print(f"Successfully booked class for {current_date.strftime('%Y-%m-%d')}")
                        else:
                            print("Failed to complete booking")
                
                except Exception as e:
                    print(f"Error processing session: {e}")
                    continue
            
            # Go back to calendar view
            full_cal_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "bw-fullcal-button"))
            )
            full_cal_button.click()
            time.sleep(2)
        
        return True
        
    except Exception as e:
        print(f"Error in get_sessions: {e}")
        return False

def get_cranford_sessions(driver, target_year, target_month):
    try:
        driver.get(HYR_CRANFORD_URL.strip())
        
        while True:
            # Wait for sessions container
            sessions_container = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "bw-widget__sessions"))
            )
        
            # Find all days
            days = sessions_container.find_elements(By.CLASS_NAME, "bw-widget__day")
            print(f"Found {len(days)} days")
            
            for day in days:
                try:
                    # Get date from the date div
                    date_div = day.find_element(By.CLASS_NAME, "bw-widget__date")
                    date_text = date_div.text
                    print(f"Date text: {date_text}")
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
                        
                        for session in sessions:
                            try:
                                # Get session basics
                                basics = session.find_element(By.CLASS_NAME, "bw-session__basics")
                                
                                # Check if this is the instructor's class
                                staff_name = basics.find_element(By.CLASS_NAME, "bw-session__staff").text
                                if HYR_INSTRUCTOR in staff_name:
                                    print(f"\nFound class on {class_date.strftime('%Y-%m-%d')}")
                                    print(f"Instructor: {staff_name}")

                                    print("Booking class...")
                                    
                                    # Click to expand details
                                    basics.click()
                                    time.sleep(2)
                                        
                                    # Find and click book button
                                    cart_button = session.find_element(By.CLASS_NAME, "bw-widget__cart_button")
                                    cart_button.click()
                                    time.sleep(2)
                                        
                                    # Handle the booking modal
                                    if handle_booking_modal(driver):
                                        print(f"Successfully booked class for {class_date.strftime('%Y-%m-%d')}")
                                        # Continue with next session instead of returning
                                        continue
                                    else:
                                        print("Failed to complete booking")
                            
                            except Exception as e:
                                print(f"Error processing session: {e}")
                                continue

                except Exception as e:
                    print(f"Error processing day: {e}")
                    continue

            # After processing current week, move to next week
            next_week_date = move_to_next_week(driver, target_year, target_month) 
            time.sleep(5)
            if not next_week_date:
                print(f"No more weeks found in {MONTHS[target_month]} {target_year}")
                print("Finished processing all weeks in the target month. Exiting program...")
                driver.quit()
                os._exit(0)  # Exit the program immediately
        
        return True
        
    except Exception as e:
        print(f"Error in get_cranford_sessions: {e}")
        return False
    
if __name__ == "__main__":
    driver = None
    try:
        print("\nYoga Class Booking System")
        print("------------------------")
        
        # Get studio choice
        # studio = get_studio_choice()
        # print(f"\nSelected studio: {'Metuchen' if 'metuchen' in studio.lower() else 'Cranford'}")
        
        # Get month choice
        # target_year, target_month = get_target_month()
        # print(f"\nSearching for classes in {calendar.month_name[target_month]} {target_year}")
        target_year = 2025
        target_month = 1
        
        driver = init_driver()

        # if studio.lower() == 'metuchen':
        #     get_metuchen_sessions(driver, target_year, target_month)
        # else:
        get_cranford_sessions(driver, target_year, target_month)
        
        input("\nPress Enter to close the browser...")
        
    except Exception as e:
        print(f"An error occurred: {e}")
    
    finally:
        if driver:
            driver.quit()

