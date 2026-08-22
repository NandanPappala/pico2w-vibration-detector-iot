import machine
import time
import utime
import maths
from machine import I2C, Pin

# This is the vibration sensor address to read from
sensor_address = 0x68

sensor_bus = machine.I2C(0, sda=machine.Pin(20), scl=machine.Pin(21), freq=400000)

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

#display RMS
def display_rms():
    while True:
        vibration_rms = calc_vibr()
        print(f"vibration_rms: {vibration_rms:.4f}")
        time.sleep(5)

display_rms()
