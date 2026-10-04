import time
import urequests as requests
from machine import Pin
import tm1637

# ---------- CONFIGURATION ----------
WIFI_SSID = "Robotic WIFI"
WIFI_PASS = "rbtWIFI@2025"

BLYNK_TOKEN = "frVys2D1fryJ_JKhKPLUnWHSN-eSHKkk"
BLYNK_API   = "http://blynk.cloud/external/api"
BLYNK_VPIN  = "V9"  # Virtual Pin for the counter in Blynk

IR_PIN = 15
TM_CLK_PIN = 17
TM_DIO_PIN = 16

# ---------- HARDWARE SETUP ----------
ir_sensor = Pin(IR_PIN, Pin.IN)
tm = tm1637.TM1637(Pin(TM_CLK_PIN), Pin(TM_DIO_PIN))

def update_blynk(count):
    try:
        url = f"{BLYNK_API}/update?token={BLYNK_TOKEN}&{BLYNK_VPIN}={count}"
        r = requests.get(url)
        r.close()
        print(f"Blynk updated with count: {count}")
    except Exception as e:
        print("Blynk update failed:", e)

# ---------- WIFI INITIALIZATION ----------
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(WIFI_SSID, WIFI_PASS)

print("Connecting to WiFi...")
while not wifi.isconnected():
    time.sleep(1)
    print(".", end="")
print("\nWiFi connected!")

# ---------- SYSTEM INITIALIZATION ----------
detection_count = 0
tm.show_number(detection_count)  # Display 0 on startup

print("Initializing system...")
print("Waiting for object detection...")

last_state = ir_sensor.value()

# ---------- MAIN LOOP ----------
while True:
    current_state = ir_sensor.value()
    
    # Trigger only on the moment of detection (state changes from 1 to 0)
    if current_state == 0 and last_state == 1:
        print("\n--- Object Detected! ---")
    
        # Update Count
        detection_count += 1
        tm.show_number(detection_count)
        update_blynk(detection_count)

    # Update state tracker
    last_state = current_state
    
    # Debounce delay
    time.sleep(0.1)
