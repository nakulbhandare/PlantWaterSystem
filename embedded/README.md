# Setting Up PlantWaterSystem on a New Raspberry Pi

This guide will walk you through setting up a new Raspberry Pi for your Soil Moisture Monitoring System using:
- Raspberry Pi
- Capacitive Soil Moisture Sensor
- ADS1115 Analog-to-Digital Converter (ADC)
- SQLite Database
- Python (for data processing and logging)

---
## 1. Hardware Requirements
### Components Needed
1. Raspberry Pi (any model with GPIO support)
2. Capacitive Soil Moisture Sensor
3. ADS1115 ADC Module
4. Jumper Wires
5. Power Supply for Raspberry Pi

---
## 2. Wiring Connections
Follow the wiring diagram you provided to correctly connect the components.

### ADS1115 (ADC) to Raspberry Pi
| ADS1115 Pin | Raspberry Pi GPIO Pin |
|-------------|-----------------|
| VDD    | 3.3V (Pin 1) 	|
| GND    | GND (Pin 9)		|
| SCL    | GPIO3 (SCL, Pin 5)	|
| SDA    | GPIO2 (SDA, Pin 3) 	|
| ADDR	 | GPIO7 (Pin 7)	|
| ALRT	 | GPIO0 (Pin 11)	|


### Capacitive Soil Moisture Sensor to ADS1115
| Sensor Pin | ADS1115 Pin |
|------------|-------------|
| VCC		| 5V (Pin 2)	|
| GND		| GND (Pin 14)	|
| Sensor 1 AO	| A0		|
| Sensor 2 AO	| A1		|
| Sensor 3 AO	| A2		|
| Sensor 4 AO	| A3		|


### Capacitive Soil Moisture Sensor Digital Output to Raspberry Pi
| Sensor DO Pin | Raspberry Pi GPIO |
|---------------|-------------------|
| Sensor 1 AO	| GPIO8 (Pin 8).    |
| Sensor 2 AO	| GPI15 (Pin 10).    |
| Sensor 3 AO	| GPI18 (Pin 12).    |
| Sensor 4 AO	| GPI23 (Pin 16).    |

---

## 3. Setting Up the Raspberry Pi
### Step 1: Update Raspberry Pi OS
Run the following commands to update your system:
sudo apt update && sudo apt upgrade -y

### Step 2: Enable I2C Communication
Check if I2C is enabled:

ls /dev/i2c-*

If you don’t see a response, enable it using:

sudo raspi-config

- Go to **Interfacing Options** → I2C → Enable.

### **Step 3: Install Required Packages**

Install Python

sudo apt install pip

Install necessary Python libraries:

sudo pip install RPi.GPIO adafruit-circuitpython-ads1x15 --break-system-packages
sudo apt install sqlite3

Ensure I2C tools are installed:

sudo apt install -y python3-smbus i2c-tools


### Step 4: Verify I2C Devices
Check if the ADS1115 is detected:

i2cdetect -y 1

You should see an address like **0x48**, confirming that ADS1115 is correctly connected.

---
## 4. Deploying the Python Script
### Step 1: Create a Working Directory

mkdir -p ~/PlantWaterSystem && cd ~/PlantWaterSystem


### **Step 2: Create the Python Script**
Create a file:

nano plant_monitor.py
nano send_data_api.py

Paste the updated Python script that reads analog and digital data from the sensor.

---

## 5. Running the Python Script
Make the script executable:

chmod +x plant_monitor.py

Run it:

python3 plant_monitor.py

It should display:
plaintext
Starting Plant Sensor Monitoring...
Raw ADC Value: 18345, Moisture Level: 54.23%, Digital Status: Dry

To check stored data in SQLite:

sqlite3 plant_sensor_data.db "SELECT * FROM moisture_data;"

---

## 6. Auto-Start on Boot
To ensure the script runs at startup:

### Option 1: Using systemd (Recommended)
1. Create a new service file:

   sudo nano /etc/systemd/system/plant_monitor.service

2. Paste the following:

   [Unit]
   Description=Plant Moisture Monitoring Service
   After=multi-user.target

   [Service]
   ExecStart=/usr/bin/python3 /home/pi/PlantWaterSystem/plant_monitor.py
   WorkingDirectory=/home/pi/plant_monitor
   StandardOutput=inherit
   StandardError=inherit
   Restart=always
   User=pi

   [Install]
   WantedBy=multi-user.target

3. Enable and start the service:

   sudo systemctl daemon-reload
   sudo systemctl enable plant_monitor.service
   sudo systemctl start plant_monitor.service

4. Check if it's running:

   sudo systemctl status plant_monitor.service


### Option 2: Using Cron
1. Open crontab:

   crontab -e

2. Add this line at the end:

   @reboot /usr/bin/python3 /home/pi/PlantWaterSystem/plant_monitor.py &

3. Save and exit.

---

## 7. Testing & Debugging
### To View Logs

journalctl -u plant_monitor.service --follow


### To Restart Service

sudo systemctl restart plant_monitor.service

### **To Manually View Data**

sqlite3 plant_sensor_data.db "SELECT * FROM moisture_data;"
