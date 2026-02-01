import csv
import os
import time
import json
import random
from datetime import datetime
from appium import webdriver
from appium.options.android import UiAutomator2Options
from config import Config
from pages.bolt_page import BoltPage

def save_to_csv(timestamp, route, options_dict, filename='prices_bolt.csv'):
    """Saves collected prices to a CSV file."""
    file_exists = os.path.isfile(Config.CSV_FILE)
    with open(Config.CSV_FILE, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["date_hour", "route", "options"])
        
        options_json = json.dumps(options_dict, ensure_ascii=False)
        writer.writerow([timestamp, route, options_json])

def main():
    # 1. Connection configuration
    options = UiAutomator2Options().load_capabilities(Config.CAPS)
    url = "http://localhost:4723"
    
    print("Appium-Surge-Monitor")
    print(f"Route: {Config.ADDRESS_START} -> {Config.ADDRESS_END}")
    
    driver = None
    try:
        driver = webdriver.Remote(url, options=options)
        bolt = BoltPage(driver)
        app_package = "ee.mtakso.client"

        # Ensure app is closed before starting the loop
        driver.terminate_app(app_package)

        while True:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"\n--- New cycle: {now} ---")

            # --- STEP 1: LAUNCH APP ---
            print("Launching Bolt application...")
            driver.activate_app(app_package)
            
            # Wait for map/GUI to load
            print("Waiting 15s for map to load...")
            time.sleep(15)

            # --- STEP 2: MEASURE ---
            try:
                all_prices = bolt.get_price()
                
                if isinstance(all_prices, dict) and len(all_prices) > 0:
                    route_label = f"{Config.ADDRESS_START} -> {Config.ADDRESS_END}"
                    save_to_csv(now, route_label, all_prices)
                    print(f"Success: Saved {len(all_prices)} categories.")
                else:
                    print(f"Failed to fetch prices: {all_prices}")
                
            except Exception as e:
                print(f"Error during measurement: {e}")
            
            # --- STEP 3: TERMINATE APP ---
            print("Terminating application...")
            driver.terminate_app(app_package)
            
            # --- STEP 4: WAIT (JITTER) ---
            # base_wait: 30 minutes (1800s)
            # jitter: 3 to 6 minutes (180s - 360s)
            base_wait = 900 
            jitter = random.randint(180, 360) 
            total_wait = base_wait + jitter
        
            next_run = datetime.fromtimestamp(time.time() + total_wait).strftime("%H:%M:%S")
            print(f"Jitter: {jitter}s. Sleeping with app closed... Next run: {next_run}")
            
            time.sleep(total_wait)

    except KeyboardInterrupt:
        print("\nStopped by user (Ctrl+C).")
    except Exception as e:
        print(f"Critical error: {e}")
    finally:
        print("Closing driver session.")
        if driver:
            try: driver.quit()
            except: pass

if __name__ == "__main__":
    main()