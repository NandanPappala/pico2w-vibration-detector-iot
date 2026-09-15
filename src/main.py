"""
Smart Vibration Monitoring System

Uses a Raspberry Pi Pico 2 W and MPU6050 sensor to:
- Monitor vibration levels
- Detect unusual vibration activity
- Display system health status
- Generate maintenance alerts
"""
import math
import time
import utime
import machine
import network
from machine import I2C, Pin
from umqtt.simple import MQTTClient

# ==================================================
# Configuration
# ==================================================
WIFI_SSID = "YOUR_WIFI_SSID"
WIFI_PASSWORD = "YOUR_WIFI_PWD"
MQTT_BROKER = "io.adafruit.com"
AIO_USERNAME = "YOUR_AIO_USERNAME"
AIO_KEY = "YOUR_AIO_KEY"

MPU6050_ADDR = 0x68

RGB_RED_PIN = 12
RGB_GREEN_PIN = 13
RGB_BLUE_PIN = 14
BUZZER_PIN = 15

# Maintenance is recommended when 3 or more
# critical vibration events occur within 30 seconds
CRITICAL_LIMIT = 3
CRITICAL_WINDOW = 30

# Demo settings
MIN_UPLOAD_INTERVAL = 60
RUNTIME_UPLOAD_INTERVAL = 1
MAINTENANCE_RESET_TIME = 10

# ==================================================
# Runtime Variables
# ==================================================
peak_vibration = 0
start_time = time.time()

critical_events = []
maintenance_required = False
maintenance_alarm_sent = False
maintenance_start_time = None

# Variables used to reduce cloud traffic
last_sent = None
last_upload_time = 0
last_runtime_upload = 0
last_status = None
last_peak = 0
last_critical_count = -1
last_maintenance_status = "UNKNOWN"

# ==================================================
# WiFi Setup
# ==================================================
print("Connecting to Wi-Fi...")

wlan = network.WLAN(network.STA_IF)
wlan.active(True)

# Uncomment when connecting to WiFi
wlan.connect(WIFI_SSID, WIFI_PASSWORD)
while not wlan.isconnected():
    time.sleep(1)

print("Wi-Fi Connected!", wlan.ifconfig())
time.sleep(2)

# ==================================================
# MQTT / Adafruit IO
# ==================================================
client = MQTTClient(
    client_id="predictive_maintenance",
    server=MQTT_BROKER,
    user=AIO_USERNAME,
    password=AIO_KEY,
    port=1883
)

client.connect()
print("Connected to Adafruit IO")


def send_to_aio(feed, value):
    """Publish data to Adafruit IO feed."""
    topic = "{}/feeds/{}".format(AIO_USERNAME, feed)
    client.publish(topic, str(value))


# ==================================================
# Hardware Setup
# ==================================================
i2c = I2C(
    0,
    sda=machine.Pin(20),
    scl=machine.Pin(21),
    freq=400000
)

red_led = Pin(RGB_RED_PIN, Pin.OUT)
green_led = Pin(RGB_GREEN_PIN, Pin.OUT)
blue_led = Pin(RGB_BLUE_PIN, Pin.OUT)

buzzer = machine.PWM(machine.Pin(BUZZER_PIN))
buzzer.duty_u16(0)

# ==================================================
# MPU6050 Initialization
# ==================================================
try:
    i2c.writeto_mem(MPU6050_ADDR, 0x6B, b" ")
    print("MPU6050 initialized")
except Exception:
    print("MPU6050 connection failed")

# Display detected I2C devices
for device in i2c.scan():
    print(hex(device))

# ==================================================
# Sensor Functions
# ==================================================
def read_vibration():
    """Read raw accelerometer values from MPU6050."""

    try:
        data = i2c.readfrom_mem(MPU6050_ADDR, 0x3B, 6)

        x = (data[0] << 8) | data[1]
        y = (data[2] << 8) | data[3]
        z = (data[4] << 8) | data[5]

        if x > 32767:
            x -= 65536
        if y > 32767:
            y -= 65536
        if z > 32767:
            z -= 65536

        return x / 16384.0, y / 16384.0, z / 16384.0

    except Exception:
        return 0, 0, 0


def calculate_vibration_rms(samples=40):
    """Calculate RMS vibration level from multiple samples."""

    sum_squares = 0

    for _ in range(samples):
        x, y, z = read_vibration()

        magnitude = math.sqrt(x**2 + y**2 + z**2)
        vibration = magnitude - 1.0

        sum_squares += vibration**2
        time.sleep_ms(5)

    return math.sqrt(sum_squares / samples)


# ==================================================
# LED Functions
# ==================================================
def set_color(r, g, b):
    red_led.value(r)
    green_led.value(g)
    blue_led.value(b)


def turn_off_all():
    buzzer.duty_u16(0)
    set_color(0, 0, 0)


def light_protocol(status):
    """LED indication of machine state."""

    turn_off_all()

    if status == "Normal":
        set_color(0, 1, 0)
    elif status == "Warning":
        set_color(0, 1, 1)
    else:
        set_color(1, 0, 0)


# ==================================================
# Buzzer Functions
# ==================================================
def play_tone(freq, duration):
    buzzer.freq(freq)
    buzzer.duty_u16(32768)
    utime.sleep_ms(duration)
    buzzer.duty_u16(0)


def simple_tone():
    play_tone(800, 500)
    utime.sleep_ms(200)
    play_tone(1000, 500)
    utime.sleep_ms(200)
    play_tone(1200, 500)


def buzzer_protocol(status):
    if status == "Warning":
        simple_tone()
    elif status == "Critical":
        for _ in range(2):
            simple_tone()
            time.sleep(0.1)
    

def maintenance_alarm():
    """One-time alarm when maintenance is triggered."""

    print("MAINTENANCE REQUIRED")

    for _ in range(3):
        simple_tone()
        time.sleep(0.1)


# ==================================================
# System Health Classification
# ==================================================
def get_machine_status(vibration):

    if vibration <= baseline * 1.15:
        return "Normal"
    elif vibration <= baseline * 1.30:
        return "Warning"

    return "Critical"


# ==================================================
# Track Critical Vibration Events
# ==================================================
def update_critical_alert(status):
"""
Count critical vibration events over 30 seconds.
Recommend maintenance when the event limit is reached.
"""

    global critical_events
    global maintenance_required
    global maintenance_start_time

    current_time = time.time()

    if status == "Critical":
        critical_events.append(current_time)
        print(">>> Critical Event Recorded")

    critical_events = [
        event_time
        for event_time in critical_events
        if current_time - event_time <= CRITICAL_WINDOW
    ]

    if (
        len(critical_events) >= CRITICAL_LIMIT
        and not maintenance_required
    ):
        maintenance_required = True
        maintenance_start_time = current_time

        print(">>> MAINTENANCE REQUIRED <<<")

    return len(critical_events)



baseline = 0.0  # Global variable
"""
At startup, the system records vibration data for 30 seconds
to determine a normal vibration level.

Future readings are compared against this value.

Normal   : ≤ baseline × 1.15
Warning  : ≤ baseline × 1.30
Critical : > baseline × 1.30
"""
def calibrate():
    global baseline

    samples = []
    start_time = time.time()

    while time.time() - start_time < 30:
        vibration = calculate_vibration_rms()
        samples.append(vibration)
        time.sleep(0.1)

    baseline = sum(samples) / len(samples)

    print("Baseline =", baseline)
    
    
# ==================================================
# Main Monitoring Loop
# ==================================================
turn_off_all()


try:
    print("Calibrating... Please keep the system in normal condition.")

    calibrate()
    
    while True:

        vibration_rms = calculate_vibration_rms()
        status = get_machine_status(vibration_rms)

        # Keep critical count frozen during maintenance
        if not maintenance_required:
            critical_count = update_critical_alert(status)
        else:
            critical_count = len(critical_events)

        # Reset maintenance mode automatically for testing
        if (
            maintenance_required
            and maintenance_start_time is not None
            and (time.time() - maintenance_start_time) >= MAINTENANCE_RESET_TIME
        ):

            maintenance_required = False
            maintenance_alarm_sent = False
            maintenance_start_time = None
            critical_events.clear()

        # Maintenance Mode
        if maintenance_required:

            set_color(0, 0, 1)

            if not maintenance_alarm_sent:
                maintenance_alarm()
                maintenance_alarm_sent = True

            buzzer.duty_u16(0)

        else:
            light_protocol(status)
            buzzer_protocol(status)

        peak_vibration = max(peak_vibration, vibration_rms)
        runtime_hours = round((time.time() - start_time) / 3600, 2)

        maintenance_status = (
            "MAINTENANCE REQUIRED"
            if maintenance_required
            else "OK"
        )
        print("----------------------------------")
        print(f"Vibration: {vibration_rms:.3f} g")
        print(f"Machine Status: {status}")
        print(f"Peak: {peak_vibration:.3f} g")
        print(f"Critical Event Count: {critical_count}")
        print(f"Runtime: {runtime_hours} hrs")
        print(f"Maintenance Status: {maintenance_status}")
        print("----------------------------------")

        #  Send updates to Adafruit IO only when values change
        if last_sent is None or abs(vibration_rms - last_sent) > 0.02:
            send_to_aio("vibration", round(vibration_rms, 3))
            last_sent = vibration_rms

        if status != last_status:
            send_to_aio("machine_status", status)
            last_status = status

        if critical_count != last_critical_count:
            send_to_aio("critical_event_count_30s", critical_count)
            last_critical_count = critical_count

        if maintenance_status != last_maintenance_status:
            send_to_aio("maintenance_status", maintenance_status)
            last_maintenance_status = maintenance_status

        if peak_vibration > last_peak:
            send_to_aio("peak_vibration", round(peak_vibration, 3))
            last_peak = peak_vibration

        if (time.time() - last_runtime_upload) >= MIN_UPLOAD_INTERVAL:
            send_to_aio("runtime_hours", runtime_hours)
            last_runtime_upload = time.time()

        time.sleep(4)

finally:
    turn_off_all()
    buzzer.deinit()
    print("System safely shut down.")

