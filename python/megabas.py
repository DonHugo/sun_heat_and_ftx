import requests
import random
import json
import time
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




def get_water_temp():

    response = requests.post("https://gotlandsenergi.se/badapp//Home/buoyGraf", headers={'User-Agent': 'Mozilla/5.0'})
    water = 'N/A'
    air = 'N/A'
    beaches = ["Ekeviken", "Sudersand", "Slite", "Åminne", "Sandviken", "Ljugarn", "Herta", "Holmhällar", "Burgsvik", "Nisseviken", "Tofta", "Kallis", "Ihreviken"]
    beach_search = "<td>{}</td>"   
    for beach in beaches:
        for i, line in enumerate(response.text.splitlines()):

            if beach_search.format(beach) in line.strip():

                water = response.text.splitlines()[i+1].strip()[4:-6]
                #print(water)
                air = response.text.splitlines()[i+2].strip()[4:-6]
                #print(air)
                break

        x = {
            "name": beach,
            "water": water,
            "air": air,
            "unit_of_measurement" : "°C",
            "state_class" : "measurement",
            "device_class" : "temperature"
            }
        y = json.dumps(x, ensure_ascii=False).encode('utf8')
        print(y.decode())

        msg = y
        topic_path = "beach/{}"
        topic = topic_path.format(beach)
        client.publish(topic,msg)

        #time.sleep(1)



    return water, air

get_water_temp()
#print(get_water_temp("Herta"))
#get_water_temp("Tofta")
#get_water_temp("Herta")
#get_water_temp("Slite")
#get_water_temp("Ihreviken")
#get_water_temp("Sandviken")

client.disconnect()
client.loop_stop()



