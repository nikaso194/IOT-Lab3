import time

# ---------- CONFIGURATION ----------
IR_PIN = 15      # Connect your IR sensor Data pin here
SERVO_PIN = 13   # Connect your Servo PWM pin here
OPEN_DELAY = 3   # How many seconds the gate stays open

# ---------- HARDWARE SETUP ----------
ir_sensor = Pin(IR_PIN, Pin.IN)
servo = PWM(Pin(SERVO_PIN), freq=50)

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
    print("Gate moved to:", angle, "°")

# ---------- INITIALIZATION ----------
# Default position: Closed (180 degrees)
print("Initializing system...")
move_servo(180) 
print("Gate is CLOSED. Waiting for object...")

# Read the initial state of the sensor (1 = clear, 0 = obstacle)
last_state = ir_sensor.value()

# ---------- MAIN LOOP ----------
while True:
    current_state = ir_sensor.value()
    
    # Check if state changed from 'No Obstacle' (1) to 'Obstacle Detected' (0)
    if current_state == 0 and last_state == 1:
        print("\n--- Object Detected! ---")
        
        # 1. Open the gate
        move_servo(90)
        
        # 2. Wait for a short delay
        print(f"Holding open for {OPEN_DELAY} seconds...")
        time.sleep(OPEN_DELAY)
        
        # 3. Return to closed position
        print("Closing gate...")
        move_servo(180)
        print("Gate is CLOSED. Waiting for next object...")

    # Update the last_state tracker
    last_state = current_state
    
    # Tiny delay for debouncing the sensor
    time.sleep(0.1)
