from machine import Pin, ADC, I2C
from time import sleep, ticks_ms
from bmp180 import BMP180
from dht import DHT11
from i2c_lcd import I2cLcd
import sys

# Pin assignments
LDR = Pin(4, Pin.IN)
TH = Pin(5)
Rain = ADC(Pin(36))
Soil = ADC(Pin(34))
MOTOR = Pin(14, Pin.OUT)
D27 = Pin(27, Pin.OUT)

Rain.atten(ADC.ATTN_11DB)
Soil.atten(ADC.ATTN_11DB)

# I2C and sensor initialization
i2c = I2C(0, scl=Pin(22), sda=Pin(21))  # adjust if needed
bmp = BMP180(i2c)
dht = DHT11(TH)
lcd = I2cLcd(i2c, 0x27, 2, 16)

# Initial states
prev_ldr_state = LDR.value()
awaiting_response = False
motor_active = False
motor_start_time = 0
display_state = 0
last_display_change = ticks_ms()
last_sensor_read = ticks_ms()

temp = 0
humidity = 0
pressureVal = 0
rainMM = 0
soilMM = 0

lcd.putstr("System Starting...")
sleep(2)
lcd.clear()

while True:
    now = ticks_ms()

    # LDR change detection
    current_ldr_state = LDR.value()
    if current_ldr_state != prev_ldr_state:
        prev_ldr_state = current_ldr_state

        print(f'{{"temp":{temp},"humidity":{humidity},"pressure":{pressureVal},"soil":{soilMM}}}')
        awaiting_response = True

    # Sensor update every second
    if now - last_sensor_read > 1000:
        last_sensor_read = now

        try:
            dht.measure()
            temp = dht.temperature()
            humidity = dht.humidity()
        except Exception:
            lcd.move_to(0, 1)
            lcd.putstr("DHT Fail     ")

        rain_raw = Rain.read()
        rainPct = int(rain_raw * 100 / 4095)
        rainMM = (100 - rainPct) * 0.5

        soil_raw = Soil.read()
        soilPct = int(soil_raw * 100 / 4095)
        soilMM = (100 - soilPct) * 0.5

        try:
            pressureVal = bmp.pressure
        except:
            pass

    # LCD display rotation
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
            lcd.putstr(f"Press:{int(pressureVal)}hPa")
        elif display_state == 3:
            lcd.putstr(f"Soil:{soilMM:.1f}mm")
        display_state = (display_state + 1) % 4

    # Handle Python response
    if awaiting_response and sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
        try:
            received = int(sys.stdin.readline())
            if received == 1:
                MOTOR.value(1)
                D27.value(1)
                motor_start_time = ticks_ms()
                motor_active = True
            else:
                MOTOR.value(0)
                D27.value(0)
                motor_active = False
            awaiting_response = False
        except:
            pass

    # Turn off motor after 4 seconds
    if motor_active and ticks_ms() - motor_start_time > 4000:
        MOTOR.value(0)
        D27.value(0)
        motor_active = False

    # Keep D27 in sync if motor is still on
    if motor_active:
        D27.value(MOTOR.value())

    sleep(0.1)

