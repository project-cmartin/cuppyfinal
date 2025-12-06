## Cuppy Has A Voice

# This code is used with an ESP32 and an sdd1306 OLED screen
# It communicates over an MQTT Broker
# Whatever is typed and published to the broker is printed on the screen

# The communication over the Broker allows the publish from anywhere in the world over the internet, the ESP32 and MQTT Client does NOT have to be on the same network

# Connect the ESP32 and screen wiring, ensure you are using either the same pins for the screen or change the pins you use in the code
# Change the "YOUR_SSID" in the WIFI_SSID option and "YOUR_PASSWORD" in the WIFI_PASSWORD option to the Wi-Fi connection you are using.
# Change the "UNIQUE_NAME" for the YOUR_NAME option to your choosing, this will appear in the topic you publish and subscribe to
# When changeing the variables, keep the parenthesis around the info
# After changes are made, run the code on the ESP32 from a program such as Thonny
# Use an MQTT client (example MQTT Explorer)
# Connect to broker.hivemq.com and make sure to use the advanced option to subscribe to the topics "wyohack/YOUR_NAME/display/command", and wyohack/YOUR_NAME/display/status

# Use the wyohack/YOUR_NAME/display/command topic for the publish option
# Type what you want printed and press the publish button

# There is trouble shooting information that prints to the Thonny terminal as long as the ESP32 is connected while you run the code. I suggest this for the first inital run.
