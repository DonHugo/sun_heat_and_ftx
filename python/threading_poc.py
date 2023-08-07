import concurrent.futures
import logging
import queue
import random
import threading
import time
import megabas as m
from paho.mqtt import client as mqtt_client
import json
import numpy as np

collection = [0,0,0,0,0,0,0,0,0,0]
input_array = np.zeros((4, 8, 10))
loops = 10

BROKER = '192.168.0.110'
PORT = 1883
#TOPIC = "python-mqtt/tcp"
SUB_TOPIC = "sequentmicrosystems"
# generate client ID with pub prefix randomly
CLIENT_ID = f'python-mqtt-tcp-pub-sub-{random.randint(0, 1000)}'
USERNAME = 'mqtt_beaches'
PASSWORD = 'uQX6NiZ.7R'

FIRST_RECONNECT_DELAY = 1
RECONNECT_RATE = 2
MAX_RECONNECT_COUNT = 12
MAX_RECONNECT_DELAY = 60
FLAG_EXIT = False

def producer(queue, event):
    """Pretend we're getting a number from the network."""
    while not event.is_set():
        a = 1
        while a > 8:
            collect_sensor_data_mega(3,a,10)
            a += 1
            if a > 8:
                a = 1
        logging.info("Producer got message: %s", input_array)
        #queue.put(input_array)

    logging.info("Producer received event. Exiting")

def sender(queue, event):
    while not event.is_set(): #or not queue.empty():
        publish(mqtt_client_connected)
        #message = queue.get()
        #logging.info(
        #    "Consumer storing message: %s (size=%d)", message, queue.qsize()
        #)

    logging.info("Consumer received event. Exiting")

#============= MQTT setup ==========================
def on_connect(client, userdata, flags, rc):
    if rc == 0 and client.is_connected():
        print("Connected to MQTT Broker!")
        client.subscribe(SUB_TOPIC)
    else:
        print(f'Failed to connect, return code {rc}')

def on_disconnect(client, userdata, rc):
    logging.info("Disconnected with result code: %s", rc)
    reconnect_count, reconnect_delay = 0, FIRST_RECONNECT_DELAY
    while reconnect_count < MAX_RECONNECT_COUNT:
        logging.info("Reconnecting in %d seconds...", reconnect_delay)
        time.sleep(reconnect_delay)

        try:
            client.reconnect()
            logging.info("Reconnected successfully!")
            return
        except Exception as err:
            logging.error("%s. Reconnect failed. Retrying...", err)

        reconnect_delay *= RECONNECT_RATE
        reconnect_delay = min(reconnect_delay, MAX_RECONNECT_DELAY)
        reconnect_count += 1
    logging.info("Reconnect failed after %s attempts. Exiting...", reconnect_count)
    global FLAG_EXIT
    FLAG_EXIT = True

def on_message(client, userdata, msg):
    print(f'Received `{msg.payload.decode()}` from `{msg.topic}` sub_topic')

def connect_mqtt():
    client = mqtt_client.Client(CLIENT_ID)
    client.username_pw_set(USERNAME, PASSWORD)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER, PORT, keepalive=3)
    client.on_disconnect = on_disconnect
    return client


#============= megabas ==========================
def collect_sensor_data_mega(stack,input,iterations):
    i = 0
    
    #print("===== def collect_sensor_data_mega =====")
    while i < iterations:
        #p_i = "i = {}"
        #print(p_i.format(i))
        collect = read_megabas_1k(stack, input)

        if collect != 9999:
            #print("===== if =====")
            #p_collect = "collect = {}"
            #print(p_collect.format(collect))
            input_position = input-1
            #print(rtd_position)
            stack_position = stack-1
            #print(stack_position)
            input_array[stack_position,input_position,i] = collect 
        else:
            #print("===== else =====") 
            stack_position = stack-1
            #print(stack_position)
            input_position = input-1
            #print(rtd_position)
            logging.info("megabas stack: %i input: %i Value: %i ", stack_position, input_position, collect)

        #input_array_mean = input_array.mean(2)[stack_position,input_position]    
        #p_input_array_mean = "Input_array.mean(2){},{} = {}"     
        #print(p_input_array_mean.format(stack_position,input_position,input_array_mean))      
        i += 1
        time.sleep(0.02)
        #if input == 7 or input == 8:
        #    time.sleep(5)
        #else:
        #    time.sleep(0.02)
    
def read_megabas_1k(stack, input):
    limit = [1000,1039,1077.9,1116.7,1155.4,1194,1232.4,1270.8,1309,1347.1,1385.1,1422.9,1460.7,1498.3,1535.8,1573.3,1610.5,1647.7,1684.8]
    delta = [3.9,3.89,3.88,3.87,3.86,3.84,3.84,3.82,3.81,3.8,3.78,3.78,3.76,3.75,3.75,3.72,3.72,3.71]

    sensor = m.getRIn1K(stack, input)
    mod_sensor = sensor*1000
    megabas_temp = "No value"
        
    if sensor == 60:
        #print("no sensor connected!")
        #template = "no sensor connected in stack {}, input {}"
        #megabas_temp = template.format(stack,input)
        megabas_temp = 9999
    else:
        if mod_sensor >= limit[0] and mod_sensor < limit[1]:        megabas_temp = calc_megabas_temp(mod_sensor-limit[0],delta[0],0)
        elif mod_sensor >= limit[1] and mod_sensor < limit[2]:      megabas_temp = calc_megabas_temp(mod_sensor-limit[1],delta[1],10)
        elif mod_sensor >= limit[2] and mod_sensor < limit[3]:      megabas_temp = calc_megabas_temp(mod_sensor-limit[2],delta[2],20)
        elif mod_sensor >= limit[3] and mod_sensor < limit[4]:      megabas_temp = calc_megabas_temp(mod_sensor-limit[3],delta[3],30)
        elif mod_sensor >= limit[4] and mod_sensor < limit[5]:      megabas_temp = calc_megabas_temp(mod_sensor-limit[4],delta[4],40)
        elif mod_sensor >= limit[5] and mod_sensor < limit[6]:      megabas_temp = calc_megabas_temp(mod_sensor-limit[5],delta[5],50)
        elif mod_sensor >= limit[6] and mod_sensor < limit[7]:      megabas_temp = calc_megabas_temp(mod_sensor-limit[6],delta[6],60)
        elif mod_sensor >= limit[7] and mod_sensor < limit[8]:      megabas_temp = calc_megabas_temp(mod_sensor-limit[7],delta[7],70)
        elif mod_sensor >= limit[8] and mod_sensor < limit[9]:      megabas_temp = calc_megabas_temp(mod_sensor-limit[8],delta[8],80)
        elif mod_sensor >= limit[9] and mod_sensor < limit[10]:      megabas_temp = calc_megabas_temp(mod_sensor-limit[9],delta[9],90)
        elif mod_sensor >= limit[10] and mod_sensor < limit[11]:      megabas_temp = calc_megabas_temp(mod_sensor-limit[10],delta[10],100)
        elif mod_sensor >= limit[11] and mod_sensor < limit[12]:      megabas_temp = calc_megabas_temp(mod_sensor-limit[11],delta[11],110)
        elif mod_sensor >= limit[12] and mod_sensor < limit[13]:      megabas_temp = calc_megabas_temp(mod_sensor-limit[12],delta[12],120)
        elif mod_sensor >= limit[13] and mod_sensor < limit[14]:      megabas_temp = calc_megabas_temp(mod_sensor-limit[13],delta[13],130)
        elif mod_sensor >= limit[14] and mod_sensor < limit[15]:      megabas_temp = calc_megabas_temp(mod_sensor-limit[14],delta[14],140)
        elif mod_sensor >= limit[15] and mod_sensor < limit[16]:      megabas_temp = calc_megabas_temp(mod_sensor-limit[15],delta[15],150)
        elif mod_sensor >= limit[16] and mod_sensor < limit[17]:      megabas_temp = calc_megabas_temp(mod_sensor-limit[16],delta[16],160)
        elif mod_sensor >= limit[17] and mod_sensor < limit[18]:      megabas_temp = calc_megabas_temp(mod_sensor-limit[17],delta[17],170)   
    #print("===== def read_megabas_1k =====")
    #print(sensor)
    #print(mod_sensor)
    #print(megabas_temp)
    return megabas_temp

def calc_megabas_temp(calc, delta, deci):
    calculated_temp=(calc/delta)+deci
    round_calculated_temp = (round(calculated_temp, 1))
    #p_calculated_temp = "calculated_temp: {}"
    #print(p_calculated_temp.format(calculated_temp))
    #p_round_calculated_temp = "round_calculated_temp: {}"
    #print(p_round_calculated_temp.format(round_calculated_temp))
    return round_calculated_temp

#============= MQTT publish ==========================
def publish(client):
    # a = 1
    # while not FLAG_EXIT:
    #     collect_sensor_data_mega(3,a,10)
    #     collect_sensor_data_rtd(4,a,10)
    #     a += 1
    #     if a > 8:
    #         a = 1
            for x in range(4):
                for y in range(8):
                    input_array.mean(2)[x,y]
                    round_value = round(input_array.mean(2)[x,y],1)
                    stack = x+1
                    sensor = y+1
                    name = "sequentmicrosystems_{}_{}"

                    msg_dict = {
                            "name": name.format(stack,sensor),
                            "temperature": round_value
                        }
                    
                    topic_path = "sequentmicrosystems/{}"
                    topic = topic_path.format(name.format(stack,sensor))

                    msg = json.dumps(msg_dict)
                    if not client.is_connected():
                        logging.error("publish: MQTT client is not connected!")
                        time.sleep(0.01)
                        continue
                    result = client.publish(topic, msg)
                    # result: [0, 1]
                    status = result[0]
                    if status == 0:
                        print(f'Send `{msg}` to topic `{topic}`')
                    else:
                        print(f'Failed to send message to topic {topic}')
                    time.sleep(1)

def run():
    logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s',
                        level=logging.DEBUG)
    client = connect_mqtt()
    client.loop_start()
    time.sleep(1)
    if client.is_connected():
        #publish(client)
        return client
    else:
        client.loop_stop()


#============= Main execution ==========================
if __name__ == "__main__":
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")
    mqtt_client_connected = run()
    pipeline = queue.Queue(maxsize=10)
    event = threading.Event()
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        executor.submit(producer, pipeline, event)
    #    executor.submit(consumer, pipeline, event)
        executor.submit(sender, pipeline, event)
        time.sleep(0.1)
        logging.info("Main: about to set event")
        event.set()
