import network
import time

SSID = "Failure"
PASSWORD = "1234567891"

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    if not wlan.isconnected():
        print("Connecting to Wi-Fi...")
        wlan.active(True)
        wlan.connect(SSID, PASSWORD)
        attempts = 0
        while not wlan.isconnected() and attempts < 10:
            time.sleep(1)
            attempts += 1
    if wlan.isconnected():
        print("Connected to Wi-Fi:", wlan.ifconfig())
    else:
        print("Failed to connect. Will try again in main.py")

connect_wifi()


