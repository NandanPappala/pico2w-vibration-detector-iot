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
