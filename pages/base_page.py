from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from appium.webdriver.common.appiumby import AppiumBy

class BasePage:
    def __init__(self, driver):
        self.driver = driver

    def wait_for(self, locator, timeout=45):
        """Bardzo cierpliwe czekanie na element - ważne dla wolnych Xiaomi."""
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located(locator)
        )

    def click(self, locator):
        element = self.wait_for(locator)
        element.click()

    def type_text(self, locator, text):
        element = self.wait_for(locator)
        element.send_keys(text)