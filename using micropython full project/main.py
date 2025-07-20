from machine import Pin, reset, ADC, I2C
from time import sleep, ticks_ms, ticks_diff
from bmp180 import BMP180
from dht import DHT11
from i2c_lcd import I2cLcd
import network
import time
import urequests as requests

# Wi-Fi Credentials
SSID = "Failure"
PASSWORD = "1234567891"

# API Info
API_KEY = '59ae5c0a66d15dbcd1af005b2d622b05'
LAT = 22.9747
LON = 88.4337

# Model Parameters
FEATURE_NAMES = ['temperature', 'dew', 'humidity', 'windspeed', 'winddir', 'pressure', 'cloudcover', 'visibility']
MEAN = [26.767101740294514, 21.47822958500669, 75.04173360107096, 17.491131191432395, 188.5200301204819, 1007.245983935743, 39.443373493975905, 3.2808400267737614]
SCALE = [4.4864203142335555, 5.3908870262590165, 10.144244248446377, 9.386844503049042, 105.08216116184296, 5.924671653847149, 27.60642197755209, 0.674752195956455]
COEF = [0.5085855379196891, -0.8065530494045989, 1.5891960979482895, 0.2172819799620712, -0.2610900705521323, -0.5429413480021518, 1.2528130646571016, -0.10385137219276974]
INTERCEPT = -2.2822012270682155

# LED Pins
RED_LED = Pin(25, Pin.OUT)  # D25
BLUE_LED = Pin(26, Pin.OUT)  # D26


def connect_wifi(): 
    RED_LED.value(1)   # Turn ON red LED (no blink)
    BLUE_LED.value(0)  # Make sure blue LED is OFF

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)

    # Wait until connected
    while not wlan.isconnected():
        time.sleep(1)

    # Once connected
    RED_LED.value(0)   # Turn OFF red LED
    BLUE_LED.value(1)  # Turn ON blue LED
    

def get_api_data():
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={LAT}&lon={LON}&appid={API_KEY}&units=metric"
    try:
        response = requests.get(url).json()
        wind_speed = response['wind']['speed']
        wind_dir = response['wind'].get('deg', 0)
        dew_point = response['main']['temp'] - ((100 - response['main']['humidity']) / 5)
        cloud_cover = response['clouds']['all']
        visibility_km = response.get('visibility', 5000) / 1000.0
        return wind_speed, wind_dir, dew_point, cloud_cover, visibility_km
    except:
        return 2.5, 180, 23.4, 60, 2.8  # fallback

def scale_features(features):
    return [(f - m) / s for f, m, s in zip(features, MEAN, SCALE)]

def predict_rainfall(scaled_features):
    z = sum(c * f for c, f in zip(COEF, scaled_features)) + INTERCEPT
    prob = 1 / (1 + pow(2.718281828, -z))
    return prob

# Pin Setup
LDR = Pin(4, Pin.IN)
TH = Pin(5)
Rain = ADC(Pin(36))
Soil = ADC(Pin(34))
MOTOR = Pin(14, Pin.OUT)
D27 = Pin(27, Pin.OUT)

Rain.atten(ADC.ATTN_11DB)
Soil.atten(ADC.ATTN_11DB)

# I2C Devices
i2c = I2C(0, scl=Pin(22), sda=Pin(21))
bmp = BMP180(i2c)
dht = DHT11(TH)
lcd = I2cLcd(i2c, 0x27, 2, 16)

# Initial State
prev_ldr_state = LDR.value()
motor_active = False
motor_start_time = 0
display_state = 0
last_display_change = ticks_ms()

# Startup Delay for GPIO stability
RED_LED.value(1)
BLUE_LED.value(0)
sleep(1)

lcd.putstr("System Starting...")
sleep(2)
lcd.clear()

# Connect to Wi-Fi
connect_wifi()

# Get weather
wind_speed, wind_dir, dew, cloud, visibility = get_api_data()

# Main Loop
while True:
    now = ticks_ms()
    current_ldr_state = LDR.value()

    try:
        dht.measure()
        temp = dht.temperature()
        humidity = dht.humidity()
    except:
        temp = 25
        humidity = 50

    try:
        pressure = bmp.pressure
    except:
        pressure = 101325

    rain_raw = Rain.read()
    rainPct = int(rain_raw * 100 / 4095)
    rainMM = (100 - rainPct) * 0.5

    soil_raw = Soil.read()
    soilPct = int(soil_raw * 100 / 4095)
    soilMM = (100 - soilPct) * 0.5

    features = [temp, dew, humidity, wind_speed, wind_dir, pressure / 100, cloud, visibility]
    scaled = scale_features(features)
    prob = predict_rainfall(scaled)
    rain_predicted = 1 if prob >= 0.5 else 0

    if current_ldr_state != prev_ldr_state:
        prev_ldr_state = current_ldr_state

        lcd.clear()
        lcd.move_to(0, 0)
        lcd.putstr(f"Rainfall: {'YES' if rain_predicted else 'NO'}")
        lcd.move_to(0, 1)
        lcd.putstr(f"Prob: {prob:.2f}")

        if rain_predicted == 0 and soilMM < 10:
            MOTOR.value(1)
            D27.value(1)
            motor_active = True
            motor_start_time = ticks_ms()

        sleep(3)
        lcd.clear()

    if motor_active and ticks_diff(ticks_ms(), motor_start_time) > 4000:
        MOTOR.value(0)
        D27.value(0)
        motor_active = False

    if now - last_display_change > 3000:
        last_display_change = now
        lcd.clear()
        lcd.move_to(0, 0)
        lcd.putstr("Device: ON")
        lcd.move_to(0, 1)
        if display_state == 0:
            lcd.putstr(f"T:{temp:.1f} H:{humidity:.1f}%")
        elif display_state == 1:
            lcd.putstr(f"Rain:{rainMM:.1f}mm")
        elif display_state == 2:
            lcd.putstr(f"Press:{pressure / 100:.1f}hPa")
        elif display_state == 3:
            lcd.putstr(f"Soil:{soilMM:.1f}mm")
        display_state = (display_state + 1) % 4

    sleep(0.1)



