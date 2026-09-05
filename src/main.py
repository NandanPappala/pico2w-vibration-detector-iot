import machine
import time
import utime
import maths
import network
from machine import I2C, Pin, PWM
from umqtt.simple import MQTTClient


# define WiFi connect info
WIFI_SSID = "YOUR_WIFI_SSID"
WIFI_PASSWORD = "YOUR_WIFI_PWD"
MQTT_BROKER = "io.adafruit.com"
AIO_USERNAME = "YOUR_AIO_USERNAME"
AIO_KEY = "YOUR_AIO_KEY"

# connect to WiFi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(WIFI_SSID, WIFI_PASSWORD)
# Indicate not connected to WiFi
while wlan.isconnected() != True:
    time.sleep(2)
    print(".")

#notify WiFi connectesf
print("WiFi Connected!", wlan.ifconfig())
time.sleep(2)

# Launch MQTT client
client = MQTTClient(
    client_id = "test_vibration_monitor",
    server = MQTT_BROKER,
    user = AIO_USERNAME,
    password= AIO_KEY,
    port=1883
)

# Connect to Adafruit IO
client.connect()
print("Connected to Adafruit IO")

# sned to adafruit feed (display by username, record feed)
def send_to_aio(feed, value):
    topic = "{}/feeds/{}".format(AIO_USERNAME,feed)
    # Client publish data
    client.publish( topic, str(value))
    
# This is the vibration sensor address to read from
sensor_address = 0x68
#(physical pin 16)
RGB_RED_PIN = 12
#(physical pin 17)
RGB_GREEN_PIN = 13
#(physical pin 19)
RGB_BLUE_PIN = 14

# Buzzer
BUZZER_PIN = 15


sensor_bus = machine.I2C(0, sda=machine.Pin(20), scl=machine.Pin(21), freq=400000)

# pins 12, 13, 14
red_led = machine.Pin(RGB_RED_PIN, machine.Pin.OUT)
green_led = machine.Pin(RGB_GREEN_PIN, machine.Pin.OUT)
blue_led = machine.Pin(RGB_BLUE_PIN , machine.Pin.OUT)


# Passive
buzzer = machine.PWM(machine.Pin(BUZZER_PIN))
# turn off buzzer
buzzer.duty_u16(0)

sensor_bus.writeto_mem(sensor_address, 0x6B, b'\x00')

print("PICO 2w vibration sensor is ready")
    
print("Search the sensors")

pico2w_devices = sensor_bus.scan()

# check if anything is there
if pico2w_devices == []:
    
    print("Check the wiring for any issues.")
else:
    
    print("Proceed to next steps")
    
    for x in pico2w_devices:
        print("Sensor found at Address:")
        print(hex(x))
        print(x)

#code to read the acceleration data x,y,z
def calc_accel():

    try:            
        sample = 50
    
        # read from 0x3B data slot
        data = sensor_bus.readfrom_mem(sensor_address, 0x3B, 6)
        
        # shift 8 slots to fit 2 bytes
        x = data[0] * 256 + data[1]
        y = data[2] * 256 + data[3]
        z = data[4] * 256 + data[5]
        
        # take in consideration neg values
        if x > 32767:
            x -= 65536
        if y > 32767:
            y -= 65536
        if z > 32767:
            z -= 65536
        
        # calc G - force
        x = x/16384
        y = y/16384
        z = z/16384
    
        return x, y, z
    except:
        return 0, 0, 0
#code to read the vibrations using RMS 
def calc_vibr():
    sum_squares = 0
    samples = 50
    for j in range(samples):
        x , y, z = calc_accel()
       
        # calculate magnitude
        magnitude = x*x + y*y + z*z
        magnitude = math.sqrt(magnitude)
        
        # vibration calc
        vibration = magnitude - 1.0
        
        # root mean square formula
        sum_squares += vibration*vibration
        time.sleep_ms(5)

    sum_squares = sum_squares/samples
    rms = math.sqrt(sum_squares)
    
    return rms


# function to turn off buzzer and set led to red
def turn_off():
    # turn off buzzer
    buzzer.duty_u16(0)    
    # Stop PWM to release the pin
    buzzer.deinit()
    red_led.value(0)
    green_led.value(0)
    blue_led.value(0)
   
# function to provide functionality for buzzer
def play_tone(frequency, duration):
    # Check if it's a rest
    if frequency == 0:
        utime.sleep_ms(duration)
    else:
        # Play the tone at 50% volume
        buzzer.freq(frequency)
        buzzer.duty_u16(32768)
        utime.sleep_ms(duration)
       
        # Turn off the sound
        buzzer.duty_u16(0)
       
# Function to play a simple tone using buzzer
def simple_tone():
    # A4 note for 500 ms
    play_tone(800, 500)  
    utime.sleep_ms(200)
    # B4 note for 500 ms
    play_tone(1000, 500)  
    utime.sleep_ms(200)
    # C5 note for 500ms
    play_tone(1000, 500)
    
# function to return status based on vibrations
def status(vibration):
    if vibration < 0.07 or vibration == 0.07:
        return "Normal"
    elif vibration < 0.1 and vibration > 0.07:
        return "Warning"
    elif vibration > 0.1 and vibration < 0.25:
        return "Anomaly"
    else:
        return "Critical"
        
# function to easily set color values for LED
def set_color(red_color, green_color, blue_color):
    red_led.value(red_color)
    green_led.value(green_color)
    blue_led.value(blue_color)

# function which controls led color based on status
def light_protocol(status):
    turn_off()
    # green
    if status == "Normal":
        set_color( 0, 1, 0)
    # yellow
    elif status == "Warning":
        set_color(0, 1, 1)
    # purple
    elif status == "Anomaly":
        set_color( 1, 0, 1)
    # red
    else:
        set_color(1, 0, 0)


# function for buzzer sound for status warning
def warning_buzzer():
    simple_tone()
   
# function for buzzer sound for status Anomaly
def anomaly_buzzer():
    for i in range(1):
        simple_tone()
        time.sleep(0.1)
# function for buzzer sound for status critical
def critical_buzzer():
    for i in range(2):
        simple_tone()
        time.sleep(0.1)

def buzzer_protocol(current_status):
   
    if current_status == "Normal":
       pass    
    elif current_status == "Warning":
       warning_buzzer()
    elif current_status == "Anomaly":
       anomaly_buzzer()
    else:
       critical_buzzer()
       


# recommend actions based on vibration
def recommendation(rms):
    if rms < 0.07:
        return "No Action Required"

    if rms < 0.12:
        return "Warning: Avoid shaking the fan or table."

    if rms < 0.25:
        return "High vibration detected. Inspect equipment and reduce movement."

    return (
        "Critical Fault: Immediate action required. "
    )



start_time = time.time()
last_upload_time = 0
RUNTIME_UPLOAD_INTERVAL = 30  # 1 minutes
MIN_UPLOAD_INTERVAL = 15  # seconds
last_sent = None
peak_vibration = 0
start_time = time.time()
def main():
    # 💡 ADD THIS LINE TO FIX THE ERROR
    global last_sent, last_upload_time, peak_vibration
   
    while True:
       
        # Calculate rms and indicate user based on status
        rms = calc_vibr()                
        current_status = status(rms)
        light_protocol(current_status)
        buzzer_protocol(current_status)
       
         # Upload only when needed
       
        if (last_sent is None or
           
             (abs(rms - last_sent) > 0.02 and time.time() - last_upload_time >= MIN_UPLOAD_INTERVAL) or
           
             time.time() - last_upload_time >= RUNTIME_UPLOAD_INTERVAL):
           
            # Display info on console
                   # Track peak vibration since last upload
            peak_vibration = max(peak_vibration, rms)
           
            # Calculate system health score and recommendation based on RMS
           
              #  score = health_score(rms)
            rec = recommendation(rms)
           
            # Calculate runtime in hours
            runtime_hours = round((time.time() - start_time) / 3600, 2)
           

            print(f"Vibration: {rms:.3f} g")
           # print(f"Health score: {score:.3f}")
            print(f"Recommendation: {rec}")
            print(f"Peak Vibration: {peak_vibration:.3f} g")
            print(f"Runtime: {runtime_hours} hrs")
           
            # Send to AdafruitIO
           
            send_to_aio("Vibration", rms)
            send_to_aio("Peak Vibration", peak_vibration)
            send_to_aio("Recommendation", rec)
            send_to_aio("Runtime", runtime_hours)
           
           
            # Now properly modifying global variables
            last_sent = rms
            last_upload_time = time.time()
           
        time.sleep(1)
   
main()
