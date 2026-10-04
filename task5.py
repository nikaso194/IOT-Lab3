```import network
import time
import urequests as requests
from machine import Pin, PWM
import tm1637

# ==========================================
# 1. CONFIGURATION
# ==========================================
WIFI_SSID = "Robotic WIFI"
WIFI_PASS = "rbtWIFI@2025"

BLYNK_TOKEN = "frVys2D1fryJ_JKhKPLUnWHSN-eSHKkk"
BLYNK_API   = "http://blynk.cloud/external/api"

# Blynk Virtual Pins
VPIN_STATUS = "V5"  # IR Status Display (String)
VPIN_SLIDER = "V6"  # Manual Servo Slider (0-180)
VPIN_COUNT  = "V9"  # Detection Counter Display
VPIN_MODE   = "V0"  # Mode Switch: 1 for Auto, 0 for Manual

# Hardware Pins
IR_PIN = 15
SERVO_PIN = 13
TM_CLK_PIN = 17
TM_DIO_PIN = 16
OPEN_DELAY = 3      # Seconds gate stays open in Auto Mode

# ==========================================
# 2. HARDWARE SETUP
# ==========================================
ir_sensor = Pin(IR_PIN, Pin.IN)
servo = PWM(Pin(SERVO_PIN), freq=50)
tm = tm1637.TM1637(Pin(TM_CLK_PIN), Pin(TM_DIO_PIN))

def move_servo(angle):
    if angle < 0: angle = 0
    if angle > 180: angle = 180
    duty_min = 26
    duty_max = 128
    duty = int(duty_min + (angle / 180) * (duty_max - duty_min))
    servo.duty(duty)
    print(f"Gate moved to: {angle}°")

# ==========================================
# 3. BLYNK API FUNCTIONS
# ==========================================
def update_blynk(vpin, value):
    try:
        url = f"{BLYNK_API}/update?token={BLYNK_TOKEN}&{vpin}={value}"
        r = requests.get(url)
        r.close()
    except Exception as e:
        print(f"Blynk update failed on {vpin}:", e)

def read_blynk(vpin):
    try:
        url = f"{BLYNK_API}/get?token={BLYNK_TOKEN}&{vpin}"
        r = requests.get(url)
        text_value = str(r.text).strip('[]"{}')
        r.close()
        if text_value.isdigit():
            return int(text_value)
    except Exception as e:
        print(f"Blynk read failed on {vpin}:", e)
    return None

# ==========================================
# 4. INITIALIZATION
# ==========================================
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(WIFI_SSID, WIFI_PASS)

print("Connecting to WiFi...")
while not wifi.isconnected():
    time.sleep(1)
    print(".", end="")
print("\nWiFi connected!")

detection_count = 0
tm.show_number(detection_count)
move_servo(180)

# Tracking variables
last_ir_state = ir_sensor.value()
last_slider_val = 180
current_mode = 1  # Default to Auto Mode
last_blynk_poll = time.ticks_ms()

print("System Ready. Mode: AUTO")

# ==========================================
# 5. MAIN LOOP
# ==========================================
while True:
    # -----------------------------------
    # TASK 1: IR Sensor & Auto Logic
    # -----------------------------------
    current_ir_state = ir_sensor.value()
    
    if current_ir_state != last_ir_state:
        if current_ir_state == 0:  # Object Detected
            print("\n--- Object Detected! ---")
            
            # Always update counters and status
            detection_count += 1
            tm.show_number(detection_count)
            update_blynk(VPIN_COUNT, detection_count)
            update_blynk(VPIN_STATUS, "Detected")
            
            # Auto Mode Gate Logic
            if current_mode == 1:
                move_servo(90)
                print(f"Holding open for {OPEN_DELAY} seconds...")
                time.sleep(OPEN_DELAY)
                print("Closing gate...")
                move_servo(180)
                
        else:  # No Object
            update_blynk(VPIN_STATUS, "Not%20Detected")  # %20 encodes the space
# -----------------------------------
    # TASK 2: Poll Blynk (Once every 1 second)
    # -----------------------------------
    # We check time elapsed so we don't spam the Blynk API and crash the script
    if time.ticks_diff(time.ticks_ms(), last_blynk_poll) > 1000:
        last_blynk_poll = time.ticks_ms()
        
        # 1. Read Mode Switch (1 = Auto, 0 = Manual)
        fetched_mode = read_blynk(VPIN_MODE)
        if fetched_mode is not None and fetched_mode != current_mode:
            current_mode = fetched_mode
            print(f"Mode switched to: {'AUTO' if current_mode == 1 else 'MANUAL'}")
        
        # 2. Read Slider if in Manual Mode
        if current_mode == 0:
            fetched_slider = read_blynk(VPIN_SLIDER)
            if fetched_slider is not None and fetched_slider != last_slider_val:
                move_servo(fetched_slider)
                last_slider_val = fetched_slider
    
    time.sleep(0.05)
`

        last_ir_state = current_ir_state
