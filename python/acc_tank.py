import threading
import librtd
import paho.mqtt.client as mqtt
import time
import statistics

#MQTT variables
mqttBroker ="192.168.0.110" 
client = mqtt.Client("RTD")
client.connect(mqttBroker)

# Threding variables
exitFlag = 0


# Application variables
rtd_1 = [0,0,0,0,0,0,0,0,0,0]
rtd_2 = [0,0,0,0,0,0,0,0,0,0]
rtd_3 = [0,0,0,0,0,0,0,0,0,0]
rtd_avg = [0,0,0,0,0,0,0,0]
loops = 10

def read_rtd(board_id,rtd_id,loops):
    i = 0
    while i < loops:
        rtd_1[i] = librtd.get(board_id, rtd_id)
        avg_rtd_1 = round(statistics.mean(rtd_1),1)
        client.publish("test/test2", avg_rtd_1)
        rtd_avg[rtd_id-1] = avg_rtd_1
        #print("Just published " + str(mean_rtd1) + " to topic test/test2")
        #print(rtd1)
        print("rtd_" + str(rtd_id) + " " + str(avg_rtd_1))
        #print(mean_rtd_1)
        i += 1
        time.sleep(0.2)

while True:
#    a = 0
#    while a < 8
    read_rtd(0,1,10)
    print(rtd_avg[1])
    read_rtd(0,2,10)