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
    # We use Config.CSV_FILE to ensure it goes to the /data folder
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
    
    try:
        driver = webdriver.Remote(url, options=options)
        bolt = BoltPage(driver)

        # --- SECTION: CLEAN START ---
        print("Preparing fresh session...")
        driver.terminate_app("ee.mtakso.client")
        time.sleep(3)
        driver.activate_app("ee.mtakso.client")
        print("Waiting 15s for map to load...")
        time.sleep(15)

        while True:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"\n--- New measurement: {now} ---")
            
            try:
                # Execute measurement
                all_prices = bolt.get_price()
                
                if isinstance(all_prices, dict) and len(all_prices) > 0:
                    route_label = f"{Config.ADDRESS_START} -> {Config.ADDRESS_END}"
                    save_to_csv(now, route_label, all_prices)
                    print(f"Success: Saved {len(all_prices)} categories.")
                else:
                    print(f"Failed to fetch prices: {all_prices}")
                
            except Exception as e:
                print(f"Error during measurement: {e}")
            
            # --- APP RESET AFTER MEASUREMENT ---
            print("Resetting Bolt application...")
            driver.terminate_app("ee.mtakso.client")
            time.sleep(3)
            driver.activate_app("ee.mtakso.client")
            
            # --- JITTER LOGIC (Random wait time) ---
            # base_wait: how often to check
            # jitter: random noise
            base_wait = 1800 
            jitter = random.randint(180, 360) 
            total_wait = base_wait + jitter
            
            next_run = datetime.fromtimestamp(time.time() + total_wait).strftime("%H:%M:%S")
            print(f"Jitter: {jitter}s. Resting... Next measurement at: {next_run}")
            
            time.sleep(total_wait)

    except KeyboardInterrupt:
        print("\nStopped by user (Ctrl+C).")
    except Exception as e:
        print(f"Critical error: {e}")
    finally:
        print("Closing driver session.")
        try: driver.quit()
        except: pass

if __name__ == "__main__":
    main()