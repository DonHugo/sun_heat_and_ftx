import librtd
import paho.mqtt.client as mqtt
import time
import statistics

mqttBroker ="192.168.0.110" 

client = mqtt.Client("RTD")
client.connect(mqttBroker)
rtd1 = [0,0,0,0,0,0,0,0,0,0]

while True:
    i = 0
    while i < 10:
        rtd1[i] = librtd.get(0, 1)
        mean_rtd1 = round(statistics.mean(rtd1),2)
        client.publish("test/test2", mean_rtd1)
        print("Just published " + str(mean_rtd1) + " to topic test/test2")
        print(rtd1)
        print(mean_rtd1)
        i += 1
        time.sleep(1)