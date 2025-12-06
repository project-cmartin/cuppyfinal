# --- Import libraries ---
import network
import socket
import time
import machine
import ubinascii

from umqtt.robust import MQTTClient
from machine import Pin, I2C
from ssd1306 import SSD1306_I2C

# --- Define Variables ---
WIFI_SSID = "YOUR_SSID" # <--- CHANGE THIS
WIFI_PASSWORD = "YOUR_PASSWORD" # <--- CHANGE THIS


# --- UTILITY FUNCTIONS ---

def wifi_connect(WIFI_SSID, WIFI_PASSWORD):
    """Connects to the Wi-Fi network."""
# Create a WLAN interface object for Station mode (connecting to a router)
    wlan = network.WLAN(network.STA_IF)
# Activate the Wi-Fi interface
    print("Activating WiFi interface...")
    wlan.active(True)
    time.sleep(1) # Allow some time for activation
# Check if already connected (useful if script restarts)
    if not wlan.isconnected():
        print("Connecting to network:", WIFI_SSID)
# Start the connection attempt
        wlan.connect (WIFI_SSID, WIFI_PASSWORD)
# Wait for connection with a timeout (e.g., 20 seconds)
        max_wait_seconds = 20
        start_time = time.ticks_ms() # Get start time in milliseconds
        print("Waiting for connection", end="")
        while not wlan.isconnected() and time.ticks_diff(time.ticks_ms(), start_time) < max_wait_seconds * 1000:
            print(".", end="")
            time.sleep(1) # Wait 1 second between checks
        print() # Print a newline after the dots/timeout
    else:
        print("Already connected to:", WIFI_SSID)
# Verify Connection and Print IP Address
    if wlan.isconnected():
        print("-" * 40) # Print a separator line
        print("WiFi Connection Successful!")
        network_config = wlan.ifconfig() # Get network configuration tuple
# network_config contains: (IP Address, Subnet Mask, Gateway, DNS Server)
        print("Device IP Address:", network_config[0])
        print("Subnet Mask:", network_config[1])
        print("Gateway:", network_config[2])
        print("DNS Server:", network_config[3])
        print("-" * 40)
    else:
        print("-" * 40)
        print("!!! WiFi Connection Failed !!!")
        print("Please check:")
        print("- Correct SSID and Password?")
        print("- Correct Wi-Fi band (2.4 GHz)?")
        print("- Wi-Fi signal strength?")
        print("-" * 40)




# --- MAIN EXECUTION ---

# Connect Wi-Fi
wifi_connect(WIFI_SSID, WIFI_PASSWORD)


