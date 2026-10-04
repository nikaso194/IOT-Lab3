import time
from machine import Pin, PWM
import urequests as requests

# ---------- CONFIG ----------
WIFI_SSID = "Robotic WIFI"
WIFI_PASS = "rbtWIFI@2025"

BLYNK_TOKEN = "frVys2D1fryJ_JKhKPLUnWHSN-eSHKkk"
BLYNK_API   = "http://blynk.cloud/external/api"

VIRTUAL_PIN = "V6"

# ---------- SERVO SETUP ----------
servo = PWM(Pin(13), freq=50)

def move_servo(angle):
    if angle < 0:
        angle = 0
    if angle > 180:
        angle = 180

    # standard ESP32 10-bit duty: ~26 for 0.5ms (0°), ~128 for 2.5ms (180°)
    duty_min = 26
    duty_max = 128
    duty = int(duty_min + (angle / 180) * (duty_max - duty_min))
    
    servo.duty(duty)
    print("Servo angle:", angle, "° | PWM duty:", duty)

# ---------- WIFI ----------
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(WIFI_SSID, WIFI_PASS)

print("Connecting to WiFi...")
while not wifi.isconnected():
    time.sleep(1)
    print(".", end="")
print("\nWiFi connected!")

# ---------- BLYNK API ----------
def read_slider_v6():
    try:
        # Format: http://blynk.cloud/external/api/get?token=YOUR_TOKEN&V6
        url = f"{BLYNK_API}/get?token={BLYNK_TOKEN}&{VIRTUAL_PIN}"
        r = requests.get(url)
        
        # Blynk returns JSON array format like ["90"]
        text_value = str(r.text).strip('[]"{}')
        r.close()
        
        return int(text_value)
    except Exception as e:
        print("API Read Error:", e)
        return None

# ---------- MAIN ----------
# Set initial position
move_servo(90)
last_angle = 90

print("Running Blynk API control for Servo...")

while True:
    current_angle = read_slider_v6()
    
    # Only update the servo if we got a valid reading and the angle changed
    if current_angle is not None and current_angle != last_angle:
        move_servo(current_angle)
        last_angle = current_angle
        
    # Crucial: 0.5s delay prevents you from exceeding Blynk's HTTP API rate limits
    time.sleep(0.5)
