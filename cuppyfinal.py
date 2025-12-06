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
YOUR_NAME = "UNIQUE_NAME"   # <--- CHANGE THIS (Use your actual name or a unique ID)

MQTT_BROKER = "broker.hivemq.com"

# --- SSD1306 I2C Setup ---
# Adjust these pins and dimensions based on your specific board and display wiring.
# Standard 0.96" OLED is typically 128x64 or 128x32. 
DISPLAY_WIDTH = 128 
DISPLAY_HEIGHT = 64
I2C_SCL_PIN = 22 # Example for ESP32
I2C_SDA_PIN = 21 # Example for ESP32

COMMAND_TOPIC = b"wyohack/" + YOUR_NAME.encode('utf-8') + b"/display/command"
STATUS_TOPIC = b"wyohack/" + YOUR_NAME.encode('utf-8') + b"/display/status"

# Initialize I2C and OLED Display
try:
    i2c = I2C(0, scl=Pin(I2C_SCL_PIN), sda=Pin(I2C_SDA_PIN))
    oled = SSD1306_I2C(DISPLAY_WIDTH, DISPLAY_HEIGHT, i2c)
    print("OLED Display Initialized successfully.")
except Exception as e:
    print(f"Error initializing OLED: {e}")
    # You may want to halt execution or run in a limited mode if the display is critical
    oled = None 

# Initial Display State
current_display_text = "Waking Up ..."                      #can change for initializing setup display text
# Display the initial message (if oled object exists)
if oled:
    oled.fill(0)  # Clear the screen
    oled.text(current_display_text, 0, 0)
    oled.show()

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

def get_unique_client_id():
    """Generates a unique MQTT client ID based on the ESP32's MAC address."""
    mac = ubinascii.hexlify(network.WLAN().config('mac'), ':').decode()
    client_id = b"esp32_oled_controller_" + mac.encode('utf-8')
    return client_id

LINE_HEIGHT = 10 # 8 pixels for the font + 2 pixels for spacing

def display_message_and_publish_status(client, new_message):
    """Displays the message on the OLED and publishes the status."""
    global current_display_text

    current_display_text = new_message

# --- Display Logic ---
    if oled:
        # 1. Clear the screen
        oled.fill(0) 
        
        # 2. Wrap the incoming message (max 16 chars per line)
        display_lines = wrap_text(new_message, width=16)
        
        # 3. Draw each line
        y_position = 0
        for line in display_lines:
            # Check if we are running out of screen space (DISPLAY_HEIGHT=64, so max 8 lines)
            if y_position >= DISPLAY_HEIGHT:
                # Stop if we run out of screen
                break 
                
            # Draw the line at (x=0, y=y_position)
            oled.text(line, 0, y_position) 
            
            # Move down 8 pixels for the next line
            y_position += LINE_HEIGHT 
        
        oled.show()
        print(f"OLED set to: '{new_message}' (wrapped)")
    else:
        print("OLED not initialized, skipping display update.")

# --- Publish Status ---
    status_message = b"Displayed: " + new_message.encode('utf-8')
    print(f"Publishing status to {STATUS_TOPIC.decode()}")
    client.publish(STATUS_TOPIC, status_message, retain=False) # Retain=False is more suitable for dynamic messages


# --- MQTT CALLBACK ---

def sub_callback(topic, msg):
    """Handles incoming MQTT messages on the command topic."""

    global mqtt_client

    print(f"Received command: Topic='{topic.decode()}', Message='{msg.decode()}'")

    incoming_text = msg.decode().strip()

    if incoming_text:
        display_message_and_publish_status(mqtt_client, incoming_text)
    else:
         # Clear the screen if an empty message is sent
         display_message_and_publish_status(mqtt_client, "Screen Cleared")



# --- MAIN EXECUTION ---

# Connect Wi-Fi
wifi_connect(WIFI_SSID, WIFI_PASSWORD)


# Prepare MQTT Client
client_id = get_unique_client_id()
print(f"MQTT Client ID: {client_id.decode()}")

try:
    # Initialize and connect MQTT
    mqtt_client = MQTTClient(
        client_id=client_id,
        server=MQTT_BROKER,
        port=1883,
        user=None,
        password=None,
        keepalive=60
    )
    mqtt_client.set_callback(sub_callback)

    print(f"Connecting to MQTT broker {MQTT_BROKER}...")
    mqtt_client.connect()
    print("MQTT connected.")

# Subscribe to the command topic
    mqtt_client.subscribe(COMMAND_TOPIC)
    print(f"Subscribed to command topic: {COMMAND_TOPIC.decode()}")

# Initial status publication after subscription
    if oled:
        display_message_and_publish_status(mqtt_client, "Ready for Text!")         #can change for original display after setup
    else:
        print("Display not active. Waiting for messages.")

#Main Loop
    while True:
# Check for new messages on the subscribed topic
        mqtt_client.check_msg() 
        time.sleep(1) # Keep the loop responsive but not overly demanding

except Exception as e:
    print(f"An error occurred: {e}")
    print("Attempting to reconnect in 10 seconds...")
    time.sleep(10)