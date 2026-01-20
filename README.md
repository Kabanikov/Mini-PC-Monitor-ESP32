# 🖥️ Mini PC Monitor ESP32

![Project Status](https://img.shields.io/badge/status-active-brightgreen)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Platform](https://img.shields.io/badge/Platform-ESP32-orange)

[🇷🇺 Читать на русском](README_RU.md)

**A compact external PC resource monitor.**
Created purely for fun and aesthetics. It displays real-time CPU, RAM, and GPU usage along with GPU temperature. Powered by an ESP32-C6 SuperMini microcontroller (or similar).

![Device Demo](img/device_photo.jpg)

## ✨ Features
* **Real-time Monitoring:** Data updates every second.
* **Plug & Play:** Automatic COM port detection and connection.
* **System Tray:** The app minimizes to the tray and runs in the background.
* **RGB Status:** The tray icon changes color (Green — Connected, Red — No connection).
* **Compact Design:** Minimalist case that takes up very little desk space.

## 📦 Installation & Usage (For Users)

No need to install Python or write any code. Just download the ready-to-use version.

1.  **Drivers:**
    Make sure you have the drivers installed for the ESP32-C6 (usually CH343 or built-in USB CDC).
    * [Download CH343 Driver](http://www.wch-ic.com/downloads/CH343SER_EXE.html) (if the device is not detected).

2.  **Download:**
    Go to the [Releases](https://github.com/Kabanikov/Mini-PC-Monitor-ESP32/releases) section and download the `PC_Monitor_v1.0.zip` archive.

3.  **Run:**
    * Unzip the archive.
    * Connect the device via USB.
    * Run exe.
    * A tray icon will appear (near the clock). Right-click -> Select Port.

## 🛠️ DIY Build (For Developers)

Follow these steps if you want to build this monitor yourself or modify the code.

### Hardware
* ESP32-C6 SuperMini (or ESP32-C3)
* OLED Display 0.96" (SSD1306) I2C
* **Wiring:**
    * **SDA** -> GPIO 6
    * **SCL** -> GPIO 7
    * **VCC** -> 3.3V
    * **GND** -> GND

### Firmware
The code is located in the `firmware/` folder.
Use **Arduino IDE**:
1.  Install libraries: `Adafruit GFX`, `Adafruit SSD1306`.
2.  Board Settings: `ESP32C6 Dev Module`, USB CDC On Boot: **Enabled**.

### Software
The code is located in the `software/` folder.

```bash
# Install dependencies
pip install pyserial psutil pystray pillow pynvml

# Run script
python monitor.py

# Compile to EXE
pyinstaller --noconsole --onefile --name="PCDashMonitor" monitor.py
