import time
from appium.webdriver.common.appiumby import AppiumBy
from pages.base_page import BasePage
from config import Config

class BoltPage(BasePage):
    def __init__(self, driver):
        super().__init__(driver)
        size = self.driver.get_window_size()
        self.w = size['width']
        self.h = size['height']

    def get_price(self):
        print(f"Measurement: {Config.ADDRESS_START} -> {Config.ADDRESS_END}")
        time.sleep(10)
        print("Tapping map to dismiss overlays/dimming...")
        self._wake_up_screen()
        time.sleep(3) 
        
        self._handle_popups_aggressively()
        
        print("Searching for search bar...")
        search_success = False
        
        for attempt in range(3):
            try:
                search_bar = self.driver.find_element(AppiumBy.XPATH, "//*[contains(@text, 'Dokąd jedziemy') or contains(@text, 'Gdzie jedziemy')]")
                search_bar.click()
                search_success = True
                break 
            except:
                print(f"Search bar missing (Attempt {attempt+1}/3). Tapping safe zone...")
                self._wake_up_screen()
                time.sleep(2)
            
        if not search_success:
            # Fallback tap if element not found
            print("Fallback: Blind tap on search area...")
            self.driver.tap([(self.w * 0.5, self.h * 0.40)]) 
        
        time.sleep(5)

        self._input_and_click_first_result(Config.ADDRESS_START, is_start=True)
        time.sleep(4)
        self._confirm_on_map()
        self._input_and_click_first_result(Config.ADDRESS_END, is_start=False)

        print("Waiting for prices to load (15s)...")
        time.sleep(15) 
        
        return self._extract_promo_prices()

    def _extract_promo_prices(self):
        """
        Extracts 'Payable Price' AND 'Old Price' (if it exists).
        Returns format: "14.00 zl | 28.00 zl"
        """
        all_options = {}
        try:
            # Container ID from your dump
            containers = self.driver.find_elements(AppiumBy.ID, "ee.mtakso.client:id/categoryItemContainer")
            
            print(f"Analyzing {len(containers)} offers...")

            for card in containers:
                try:
                    # 1. Name
                    name = card.find_element(AppiumBy.ID, "ee.mtakso.client:id/title").text.strip()

                    # 2. Primary Price (Payable)
                    price_now = card.find_element(AppiumBy.ID, "ee.mtakso.client:id/primaryPrice").text.strip()

                    # 3. Check for 'Old Price' (Secondary)
                    price_old = ""
                    try:
                        # Search inside the same card
                        old_el = card.find_element(AppiumBy.ID, "ee.mtakso.client:id/secondaryPrice")
                        if old_el.is_displayed():
                            price_old = old_el.text.strip()
                    except:
                        pass # No promo for this category

                    # 4. Format the entry
                    if price_old:
                        # Save as: "PriceNow | PriceOld"
                        all_options[name] = f"{price_now} | {price_old}"
                    else:
                        all_options[name] = price_now
                        
                except Exception as e:
                    continue

            if all_options:
                print(f"Collected {len(all_options)} categories (with promo info).")
                return all_options
            return "No data"

        except Exception as e:
            print(f"Error: {e}")
            return "Error"

    # --- Helper methods ---
    def _input_and_click_first_result(self, text, is_start):
        inputs = self.driver.find_elements(AppiumBy.CLASS_NAME, "android.widget.EditText")
        if not inputs: return
        idx = 0 if is_start or len(inputs) == 1 else 1
        inputs[idx].click()
        inputs[idx].clear()
        inputs[idx].send_keys(text)
        time.sleep(5)
        try:
            results = self.driver.find_elements(AppiumBy.ID, "ee.mtakso.client:id/title")
            if results: results[0].click()
            else: self.driver.tap([(self.w * 0.5, 640)])
        except: self.driver.tap([(self.w * 0.5, 640)])

    def _confirm_on_map(self):
        try:
            confirm_btn = self.driver.find_elements(AppiumBy.XPATH, "//*[contains(@text, 'Potwierdź')]")
            if confirm_btn: confirm_btn[0].click(); time.sleep(4)
        except: pass

    def _handle_popups_aggressively(self):
        """
        Checks for various popup texts and closes them.
        """
        print("Checking for popups/modals...")
        target_texts = [
            "Może później", "Pomiń", "Nie teraz", 
            "Anuluj", "Odrzuć", "Nie zezwalaj", "Zamknij"
        ]

        for text in target_texts:
            try:
                xpath = f"//*[contains(@text, '{text}')]"
                elems = self.driver.find_elements(AppiumBy.XPATH, xpath)
                if elems:
                    print(f"Closing popup: '{text}'")
                    elems[0].click()
                    time.sleep(1)
                    return
            except: pass
        
        # Check for X icon by content-desc
        try:
            close_x = self.driver.find_elements(AppiumBy.XPATH, "//*[@content-desc='Zamknij' or @content-desc='Close']")
            if close_x:
                close_x[0].click()
                time.sleep(1)
        except: pass

    def _wake_up_screen(self):
        """
        Taps a safe area on the map (35% from top) to dismiss dimming.
        """
        x = self.w * 0.5
        y = self.h * 0.35
        try:
            self.driver.tap([(x, y)])
        except: pass

    def go_back_to_main(self):
        self.driver.terminate_app("ee.mtakso.client")
        time.sleep(2)
        self.driver.activate_app("ee.mtakso.client")
        time.sleep(8)