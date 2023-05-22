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
rtd1 = [0,0,0,0,0,0,0,0,0,0]
loops = 10

class myThread (threading.Thread):
   def __init__(self, threadID, name, counter):
      threading.Thread.__init__(self)
      self.threadID = threadID
      self.name = name
      self.counter = counter
   def run(self):
      print "Starting " + self.name
      print_time(self.name, 5, self.counter)
      print "Exiting " + self.name

def read_rtd(board_id,rtd_id,loops):
    i = 0
    while i < loops:
        rtd1[i] = librtd.get(board_id, rtd_id)
        mean_rtd1 = round(statistics.mean(rtd1),1)
        client.publish("test/test2", mean_rtd1)
        #print("Just published " + str(mean_rtd1) + " to topic test/test2")
        #print(rtd1)
        print("rtd_" + str(rtd_id) + " " + str(mean_rtd1))
        #print(mean_rtd1)
        i += 1
        time.sleep(1)

# Create new threads
thread1 = myThread(1, "Thread-1", 1)
thread2 = myThread(2, "Thread-2", 2)

# Start new Threads
thread1.start()
thread2.start()

while True:
#    a = 0
#    while a < 8
    read_rtd(0,1,10)
    read_rtd(0,2,10)