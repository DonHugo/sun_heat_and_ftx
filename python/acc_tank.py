import librtd
import paho.mqtt.client as mqtt
import time
import statistics

mqttBroker ="192.168.0.110" 

client = mqtt.Client("RTD")
client.connect(mqttBroker)
rtd1 = [0,0,0,0,0,0,0,0,0,0]
loops = 10


def read_rtd(board_id,rtd_id,loops):
    i = 0
    while i < loops:
        rtd1[i] = librtd.get(board_id, rtd_id)
        mean_rtd1 = round(statistics.mean(rtd1),1)
        client.publish("test/test2", mean_rtd1)
        #print("Just published " + str(mean_rtd1) + " to topic test/test2")
        #print(rtd1)
        print("rtd" + srt(rtd_id) + " " + str(mean_rtd1))
        #print(mean_rtd1)
        i += 1
        time.sleep(1)

while True:
#    a = 0
#    while a < 8
    read_rtd(0,1,10)
    read_rtd(0,2,10)