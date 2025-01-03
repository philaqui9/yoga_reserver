from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
from resources.html_selectors import *
from config.config import (
    MINDBODY_USERNAME, 
    MINDBODY_PASSWORD
)

class ModalUtils:
    def __init__(self):
        pass

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