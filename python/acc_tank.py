import librtd
import paho.mqtt.client as mqtt
import time


while True:
    i = 1
    while i < 8:
        rtd = librtd.get(0, i)
        client.publish("test/test2", rtd)
        print("Just published " + str(rtd) + " to topic test/test2")
        i += 1
        time.sleep(1)