#!/bin/bash

echo "Starting PlantWaterSystem setup..."

# Step 1: Clone the repository (only if not already cloned)
if [ ! -d "PlantWaterSystem" ]; then
    echo "Cloning the PlantWaterSystem repository..."
    git clone git@github.com:SE4CPS/PlantWaterSystem.git
fi

# Navigate to the directory
cd PlantWaterSystem/Embedded || exit

# Step 2: Update Raspberry Pi OS
echo "Updating Raspberry Pi OS..."
sudo apt update && sudo apt upgrade -y

# Step 3: Enable I2C Communication (manual step reminder)
echo "Please ensure I2C is enabled by running: sudo raspi-config (Interfacing Options -> I2C -> Enable)"
echo "Press Enter to continue after enabling I2C or if it is already enabled."
read -p ""

# Step 4: Install Required Packages
echo "Installing required packages..."
sudo apt install -y python3-pip python3-smbus i2c-tools sqlite3

echo "Installing necessary Python libraries..."
sudo pip3 install RPi.GPIO adafruit-circuitpython-ads1x15 --break-system-packages

# Step 5: Verify I2C Devices
echo "Verifying I2C connection..."
i2cdetect -y 1

# Step 6: Set Permissions and Run Python Script
echo "Setting executable permission for the plant_monitor.py script..."
chmod +x plant_monitor.py

# Step 7: Setup Auto-Start with systemd
echo "Setting up auto-start using systemd..."
SERVICE_FILE="/etc/systemd/system/plant_monitor.service"

sudo bash -c "cat > $SERVICE_FILE" <<EOF
[Unit]
Description=Plant Moisture Monitoring Service
After=multi-user.target

[Service]
ExecStart=/usr/bin/python3 /home/pi/PlantWaterSystem/Embedded/plant_monitor.py
WorkingDirectory=/home/pi/PlantWaterSystem/Embedded
StandardOutput=inherit
StandardError=inherit
Restart=always
User=pi

[Install]
WantedBy=multi-user.target
EOF

echo "Reloading systemd daemon..."
sudo systemctl daemon-reload

echo "Enabling and starting the plant_monitor service..."
sudo systemctl enable plant_monitor.service
sudo systemctl start plant_monitor.service

echo "Setup is complete. You can now check the service status with:"
echo "sudo systemctl status plant_monitor.service"
