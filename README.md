# Bolt Surge Price Monitor

An automated system for monitoring and analyzing dynamic pricing (Surge Pricing) and discounts in the Bolt application. The project uses mobile process automation (Appium) to collect price data for all ride categories on a selected route in real-time.

---

## Project Architecture

The project follows the **Page Object Model (POM)** pattern, ensuring separation of test logic from the application structure.

### Key Components:
* **`monitor.py`** – The main process overseeing measurements. It handles the "Jitter" logic (random delays) and performs hard application restarts to ensure stability during long-term (night) runs.
* **`config.py`** – Central configuration file containing addresses, Appium Capabilities, and file paths.
* **`pages/bolt_page.py`** – Page Object containing interaction logic with the Bolt UI. It includes advanced logic for extracting both the payable price and the original "strike-through" price (promotion detection).
* **`visualizer.py`** – Analytical tool that generates professional charts from collected CSV data, visualizing price trends and active promotions.
* **`setup.ps1`** – PowerShell script for automatic environment setup.

### Directory Structure:
* `/data` – Stores the raw database (CSV files).
* `/output` – Stores generated visualization charts (PNG).
* `/debug` – Stores XML dumps for troubleshooting UI changes.
* `/utils` – Helper scripts (e.g., inspector).

---

## Features

1.  **Surge Monitoring:** Tracks price fluctuations in real-time.
2.  **Promotion Detection:** Distinguishes between the payable price and the original price (e.g., "12.00 zl | 24.00 zl"), allowing for analysis of discount strategies.
3.  **Anti-Ban & Stability:** Uses random wait times (Jitter) and application termination commands to simulate human behavior and prevent app crashes/caching issues.
4.  **Dynamic Activity Detection:** Configured to handle various Android Activity entry points.

---

## Configuration and Installation

### 1. System Requirements
* **Python:** 3.10+
* **Appium Server:** 2.x
* **Device:** Android Smartphone (USB Debugging enabled) or Emulator.
* **Application:** Bolt installed and logged in.

### 2. Installation

You can use the provided PowerShell script to set up the virtual environment and install dependencies automatically:

```powershell
.\setup.ps1
```

### 3. Configuration (`config.py`)

Before running, ensure `config.py` matches your environment:
* **ADDRESS_START / END:** Set your monitoring route.
* **appActivity:** The entry point for the app. If the bot fails to start with an "Activity not found" error:
    1. Open the Bolt app manually on your phone.
    2. Run the following command in your terminal:
       ```powershell
       adb shell dumpsys window | Select-String "mCurrentFocus"
       ```
    3. Look for the output like: `.../ee.mtakso.client.activity.SplashHomeActivity}`.
    4. Copy the part **after the slash** (e.g., `.activity.SplashHomeActivity`) and update the `appActivity` value in `config.py`.

## Usage

* **Start Monitoring:**
    ```bash
    python monitor.py
    ```
    *Saves data to `data/prices_bolt.csv`.*

* **Generate Chart:**
    ```bash
    python visualizer.py
    ```
    *Saves chart to `output/chart.png`.*

