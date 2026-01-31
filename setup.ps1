# Create venv (if it does not exist)
if (-not (Test-Path "venv")) {
    python -m venv venv
    Write-Output "Created new venv environment."
} else {
    Write-Output "venv already exists."
}

Write-Output "Installing libraries..."

.\venv\Scripts\python.exe -m pip install --upgrade pip
.\venv\Scripts\pip.exe install Appium-Python-Client selenium pandas matplotlib seaborn

Write-Output "----------------------------------------"
Write-Output "Environment ready!"
Write-Output "Python location:"
(Get-Command .\venv\Scripts\python.exe).Source

Write-Output "Installed libraries:"
.\venv\Scripts\pip.exe list | Select-String -Pattern "Appium|pandas|selenium"

Write-Output "----------------------------------------"
Write-Output "To activate the environment in this terminal, run:"
Write-Output ".\venv\Scripts\Activate.ps1"