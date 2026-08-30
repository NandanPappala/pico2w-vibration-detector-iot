import machine
import time
import utime
import maths
from machine import I2C, Pin

# This is the vibration sensor address to read from
sensor_address = 0x68
#(physical pin 16)
RGB_RED_PIN = 12
#(physical pin 17)
RGB_GREEN_PIN = 13
#(physical pin 19)
RGB_BLUE_PIN = 14


sensor_bus = machine.I2C(0, sda=machine.Pin(20), scl=machine.Pin(21), freq=400000)

# pins 12, 13, 14
red_led = machine.Pin(RGB_RED_PIN, machine.Pin.OUT)
green_led = machine.Pin(RGB_GREEN_PIN, machine.Pin.OUT)
blue_led = machine.Pin(RGB_BLUE_PIN , machine.Pin.OUT)


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

# function to turn off buzzer and set led to red
def turn_off():
    red_led.value(0)
    green_led.value(0)
    blue_led.value(0)


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
       
def main():
   
    while True:
        rms = calc_vibr()                
        current_status = status(rms)
        light_protocol(current_status)
                       
        time.sleep(1)
   
main()
