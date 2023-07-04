import random
import json
import time
import megabas as m
from paho.mqtt import client as mqttClient

def on_connect(client, userdata, flags, rc):
 
    if rc == 0:
 
        print("Connected to broker")
 
        global Connected                #Use global variable
        Connected = True                #Signal connection 
 
    else:
 
        print("Connection failed")
 
Connected = False   #global variable for the state of the connection
 
broker_address= "192.168.0.110"
port = 1883
user = "mqtt_beaches"
password = "uQX6NiZ.7R"
 
client = mqttClient.Client("Python_beaches")               #create new instance
client.username_pw_set(user, password=password)    #set username and password
client.on_connect= on_connect                      #attach function to callback
client.connect(broker_address, port=port)          #connect to broker
 
client.loop_start()        #start the loop
 
while Connected != True:    #Wait for connection
    time.sleep(0.1)




def get_temp():
    for x in range(8):
        sensor = m.getRIn1K(3, x)
        if sensor == 60:
            break
        else:
            print(sensor)
#        x = {
#            "name": beach,
#            "water": water,
#            "air": air,
#            "unit_of_measurement" : "C",
#            "state_class" : "measurement",
#            "device_class" : "temperature"
#            }
#        y = json.dumps(x, ensure_ascii=False).encode('utf8')
#        print(y.decode())

        # msg = y
        # topic_path = "beach/{}"
        # topic = topic_path.format(beach)
        # client.publish(topic,msg)

        #time.sleep(1)



    return

def read_sensors():
    #s7 = m.getRIn1K(3, 7)
    #s8 = m.getRIn1K(3, 8)
    print(m.getRIn1K(3, 5))
    time.sleep(0.3)
    print(m.getRIn1K(3, 6))
    time.sleep(0.3)
    print(m.getRIn1K(3, 7))
    time.sleep(0.3)
    print(m.getRIn1K(3, 8))
    print(m.getInVolt(3))
    print(m.getRaspVolt(3))
    print(m.getCpuTemp(3))

    return

#get_water_temp()
#read_sensors()
get_temp()

client.disconnect()
client.loop_stop()



