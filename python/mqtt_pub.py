import paho.mqtt.client as mqtt 
from random import randrange, uniform
import time

mqttBroker ="mqtt.eclipseprojects.io" 

client = mqtt.Client("Temperature_Inside")
client.connect(mqttBroker) 

while True:
    randNumber = uniform(20.0, 21.0)
    client.publish("test/test2", randNumber)
    print("Just published " + str(randNumber) + " to topic test/test2")
    time.sleep(1)