import paho.mqtt.client as mqtt
import time

def on_message(client, userdata, message):
    print("received message: " ,str(message.payload.decode("utf-8")))

mqttBroker ="192.168.0.110"

client = mqtt.Client("sun_heat_collector")
client.connect(mqttBroker) 

client.loop_start()

client.subscribe("test/test1")
client.on_message=on_message 

time.sleep(30)
client.loop_stop()