import os

class Config:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(BASE_DIR, 'data')
    OUTPUT_DIR = os.path.join(BASE_DIR, 'output')
    DEBUG_DIR = os.path.join(BASE_DIR, 'debug')
    
    CSV_FILE = os.path.join(DATA_DIR, 'prices_bolt.csv')
    CHART_FILE = os.path.join(OUTPUT_DIR, 'chart.png')
    
    ADDRESS_START = "Dworzec Główny Wschód w Krakowie"
    ADDRESS_END = "Bronowicka 57 Kraków"
    
    CAPS = {
        "platformName": "Android",
        "automationName": "UiAutomator2",
        "deviceName": "Xiaomi Redmi Note 12",
        "appPackage": "ee.mtakso.client",
        "appActivity": ".activity.SplashHomeActivity",
        "appWaitActivity": "*",
        "language": "pl",
        "locale": "PL",
        "noReset": True,
        "fullReset": False,
        "ensureWebviewsHavePages": True,
        "nativeWebScreenshot": True,
        "newCommandTimeout": 3600,
        "connectHardwareKeyboard": True,
        "autoGrantPermissions": True
    }