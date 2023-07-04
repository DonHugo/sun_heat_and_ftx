import megabas as m
import time

def read_sensors():
    #s7 = m.getRIn1K(3, 7)
    #s8 = m.getRIn1K(3, 8)
    print(m.getRIn1K(3, 7))
    time.sleep(0.3)
    print(m.getRIn1K(3, 8))
    return

read_sensors()