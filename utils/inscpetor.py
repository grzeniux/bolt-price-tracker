from appium import webdriver
from appium.options.android import UiAutomator2Options
from config import Config
import time

options = UiAutomator2Options().load_capabilities(Config.CAPS)
driver = webdriver.Remote("http://localhost:4723", options=options)

def inspect():
    print("Launch Bolt manually on your phone and navigate to the screen where you entered 'Dworzec' and see the list of results.")
    input("Press Enter in this terminal when you are ready...")
    
    # Get screen structure
    xml_source = driver.page_source
    
    with open("screen_structure.xml", "w", encoding="utf-8") as f:
        f.write(xml_source)
    
    print("Done! File 'screen_structure.xml' has been generated.")
    print("Open it in a text editor and paste the fragments containing 'Wschód' or 'results' here.")
    driver.quit()

if __name__ == "__main__":
    inspect()