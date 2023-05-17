import librtd
import paho.mqtt.client as mqtt
import time


while True:
    i = 1
    while i < 8:
    rtd[i] = librtd.get(0, i)
    client.publish("test/test2", rtd[i])
    print("Just published " + str(rtd[i]) + " to topic test/test2")
    i += 1
    time.sleep(1)