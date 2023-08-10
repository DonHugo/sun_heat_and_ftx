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
import librtd
import argparse
import lib4relind

#==== MQTT Variables ====#
BROKER = '192.168.0.110'
PORT = 1883
#TOPIC = "python-mqtt/tcp"
SUB_TOPIC_1 = "rtd/acctank"
SUB_TOPIC_2 = "rtd/solfangare_2"
# generate client ID with pub prefix randomly
CLIENT_ID = f'python-mqtt-tcp-pub-sub-{random.randint(0, 1000)}'
USERNAME = 'mqtt_beaches'
PASSWORD = 'uQX6NiZ.7R'

FIRST_RECONNECT_DELAY = 1
RECONNECT_RATE = 2
MAX_RECONNECT_COUNT = 12
MAX_RECONNECT_DELAY = 60

#==== Application Variables ====#
FLAG_EXIT = False
collection = [0,0,0,0,0,0,0,0,0,0]
input_array = np.zeros((4, 8, 10))
loops = 10

set_temp_tank_1 = 70 # Maximal temperatur i tanken under normal drift. (Inställbar 15 °C till 90 °C med fabriksinställning 65 °C)
dTStart_tank_1 = 8 # Temperaturdifferens mellan kollektor (T1) och Tank1 (T2) vid vilken pumpen startar laddnig mot tanken. (Inställbar 3 °C till 40 °C med fabriksinställning 7 °C)
dTStop_tank_1 = 4 # Temperaturdifferens mellan kollektor (T1) och Tank1 (T2) vid vilken pumpen stannar. (Inställbar 2 till (Set tank1 -2 °C) med fabriksinställning 3 °C)
kylning_kollektor = 90
temp_kok = 150
temp_kok_hysteres = (temp_kok - 10)
solfangare_manuell_styrning = False
solfångare_manuell_pump = False # pump_solfangare


#===== MQTT subscribe =====#
mqtt_rtd = np.zeros(9)
mqtt_sun = np.zeros(3)

#==== Application parsing variables ====#
parser = argparse.ArgumentParser()

#-db DATABSE -u USERNAME -p PASSWORD -size 20
parser.add_argument("-d", "--debug", dest = "debug_mode", default = "false", help="true|false")
parser.add_argument("-t", "--test", dest = "test_mode", default = "false", help="true|false")

args = parser.parse_args()




def producer(queue, event):
    """Pretend we're getting a number from the network."""
    while not event.is_set():
        a = 1
        while not FLAG_EXIT:
            collect_sensor_data_mega(3,a,10)
            a += 1
            if a > 8:
                if args.debug_mode == "true":
                    logging.info("""input_array content: 
                                %s""", input_array)
                a = 1
        #logging.info("""Producer got message: %s""", input_array)
        #queue.put(input_array)

    logging.info("Producer received event. Exiting")

def execution(queue, event):
    while not event.is_set() or not queue.empty():
        logging.info("executor started, waiting 7sec")
        time.sleep(5)
        while not FLAG_EXIT:
            time.sleep(2)
            logging.info("starting main_sun_collector!")
            main_sun_collector()


    logging.info("Consumer received event. Exiting")

def sender(queue, event):
    while not event.is_set() or not queue.empty():
        time.sleep(5)
        while not FLAG_EXIT:
            time.sleep(2)
            sensor_calculations(mqtt_client_connected)
            stored_energy(mqtt_client_connected)
            ftx(mqtt_client_connected)

    logging.info("Consumer received event. Exiting")

#========================== MQTT setup ==========================
def on_connect(client, userdata, flags, rc):
    if rc == 0 and client.is_connected():
        print("Connected to MQTT Broker!")
        #client.subscribe(SUB_TOPIC_1)
        client.subscribe([(SUB_TOPIC_1, 0), (SUB_TOPIC_2, 0)])
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
    if args.debug_mode == "true":
        print(f'Received `{msg.payload.decode()}` from `{msg.topic}` SUB_TOPIC')
    
    if msg.topic == "rtd/acctank":
        x = json.loads(msg.payload.decode())
        mqtt_rtd[0] = x["RTD_1"]
        mqtt_rtd[1] = x["RTD_2"]
        mqtt_rtd[2] = x["RTD_3"]
        mqtt_rtd[3] = x["RTD_4"]
        mqtt_rtd[4] = x["RTD_5"]
        mqtt_rtd[5] = x["RTD_6"]
        mqtt_rtd[6] = x["RTD_7"]
        mqtt_rtd[7] = x["RTD_8"]
        mqtt_rtd[8] = x["T3"]
        mqtt_sun[0] = x["T1"]
        mqtt_sun[1] = x["T2"]
        mqtt_sun[2] = x["T3"]
        if args.debug_mode == "true":
            logging.info("mqtt_rtd %s", mqtt_rtd)
            logging.info("mqtt_sun %s", mqtt_sun)

def connect_mqtt():
    client = mqtt_client.Client(CLIENT_ID)
    client.username_pw_set(USERNAME, PASSWORD)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER, PORT, keepalive=3)
    client.on_disconnect = on_disconnect
    return client

#========================== megabas ==========================
def collect_sensor_data_mega(stack,input,iterations):
    i = 0
    
    while i < iterations:
        collect = read_megabas_1k(stack, input)

        if collect != 9999:
            input_position = input-1
            stack_position = stack-1
            input_array[stack_position,input_position,i] = collect 
        else:
            stack_position = stack-1
            input_position = input-1
 
        i += 1
    
def read_megabas_1k(stack, input):
    limit = [1000,1039,1077.9,1116.7,1155.4,1194,1232.4,1270.8,1309,1347.1,1385.1,1422.9,1460.7,1498.3,1535.8,1573.3,1610.5,1647.7,1684.8]
    delta = [3.9,3.89,3.88,3.87,3.86,3.84,3.84,3.82,3.81,3.8,3.78,3.78,3.76,3.75,3.75,3.72,3.72,3.71]

    sensor = m.getRIn1K(stack, input)
    mod_sensor = sensor*1000
    megabas_temp = "No value"
        
    if sensor == 60:
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
    return megabas_temp

def calc_megabas_temp(calc, delta, deci):
    calculated_temp=(calc/delta)+deci
    round_calculated_temp = (round(calculated_temp, 1))
    return round_calculated_temp

#========================== rtd ==========================
def collect_sensor_data_rtd(stack,input,iterations):
    i = 0
    while i < iterations:
        collect_rtd = read_rtd(stack, input)
        if collect_rtd != 9999:
            stack_position = stack-1
            input_position = input-1
            input_array[stack_position,input_position,i] = collect_rtd
        else:
            stack_position = stack-1
            input_position = input-1

        i += 1
        time.sleep(0.02)
    return

def read_rtd(stack,input):
    temp = librtd.get(stack, input)
    if temp > 200 or temp < -50:
        temp = 9999
    return temp

#========================== onewire ==========================
def collect_sensor_data_onewire(stack):
    return

def read_onewire():
    print("========== OneWire ==========")
    print(m.owbGetSensorNo(3)) #number of sensors present, starting at 1
    print(m.owbGetTemp(3, 1))  # reading first sensor and getting temperature
    print(m.owbGetRomCode(3, 1)) # reading sensor id on first sensor
    print("========== OneWire ==========")

    return

#========================== MQTT publish ==========================
def publish(client,topic,msg):
    if not client.is_connected():
        logging.error("publish: MQTT client is not connected!")
        time.sleep(1)
        return
    result = client.publish(topic, msg)
    status = result[0]
    if status == 0:
        if args.debug_mode == "true":
            print(f'Send `{msg}` to topic `{topic}`')
    else:
        print(f'Failed to send message to topic {topic}')
    time.sleep(0.1)

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


#========================== data calculations ==========================
def sensor_calculations(client):
    for x in range(4):
        for y in range(8):
            #remove below row?! (input_array.mean(2)[x,y]), dont think its used!
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
            publish(client,topic,msg)

def stored_energy(client):
    stored_energy = np.zeros(10)
    #logging.info("stored_energy: %s", stored_energy)
    stored_energy_kwh = np.zeros(4)
    #logging.info("stored_energy_kwh: %s", stored_energy_kwh)
    if args.test_mode == "false":
        zero_valu = 0 #temperature of the water that is comming to to the system from the well
        stack_1 = 2
        stack_2 = 2
        stored_energy[0] = ((input_array.mean(2)[stack_1,0]-zero_valu)*35)
        stored_energy[1] = ((input_array.mean(2)[stack_1,1]-zero_valu)*35)
        stored_energy[2] = ((input_array.mean(2)[stack_1,2]-zero_valu)*35)
        stored_energy[3] = ((input_array.mean(2)[stack_1,3]-zero_valu)*35)
        stored_energy[4] = ((input_array.mean(2)[stack_1,4]-zero_valu)*35)
        stored_energy[5] = ((input_array.mean(2)[stack_1,5]-zero_valu)*35)
        stored_energy[6] = ((input_array.mean(2)[stack_1,6]-zero_valu)*35)
        stored_energy[7] = ((input_array.mean(2)[stack_1,7]-zero_valu)*35)
        stored_energy[8] = ((input_array.mean(2)[stack_2,0]-zero_valu)*35)
        stored_energy[9] = ((input_array.mean(2)[stack_2,1]-zero_valu)*35)
        stored_energy[0] = (input_array.mean(2)[2,0])
        #logging.info("stored_energy[0]: %s", stored_energy[0])
        #logging.info("stored_energy: %s", stored_energy)
        stored_energy_kwh[0] = round(np.sum(stored_energy)*4200/1000/3600,2)
        stored_energy_kwh[1] = round(np.sum(stored_energy[:5])*4200/1000/3600,2)
        stored_energy_kwh[2] = round(np.sum(stored_energy[5:])*4200/1000/3600,2)
        #logging.info("stored_energy_kwh: %s", stored_energy_kwh)

    elif args.test_mode == "true":
        zero_valu = 4 #temperature of the water that is comming to to the system from the well
        stored_energy[0] = ((mqtt_rtd[0]-zero_valu)*35)
        stored_energy[1] = ((mqtt_rtd[1]-zero_valu)*35)
        stored_energy[2] = ((mqtt_rtd[2]-zero_valu)*35)
        stored_energy[3] = ((mqtt_rtd[3]-zero_valu)*35)
        stored_energy[4] = ((mqtt_rtd[4]-zero_valu)*35)
        stored_energy[5] = ((mqtt_rtd[5]-zero_valu)*35)
        stored_energy[6] = ((mqtt_rtd[6]-zero_valu)*35)
        stored_energy[7] = ((mqtt_rtd[7]-zero_valu)*35)
        stored_energy[8] = ((mqtt_rtd[8]-zero_valu)*35)
        #logging.info("stored_energy[0]: %s", stored_energy[0])
        #logging.info("stored_energy: %s", stored_energy)
        stored_energy_kwh[0] = round((np.sum(stored_energy)*4200/1000/3600),2)
        stored_energy_kwh[1] = round((np.sum(stored_energy[:5])*4200/1000/3600),2)
        stored_energy_kwh[2] = round((np.sum(stored_energy[4:])*4200/1000/3600),2)
        stored_energy_kwh[3] = round(np.mean(mqtt_rtd[:8]),2)
        #logging.info("stored_energy_kwh: %s", stored_energy_kwh)

    msg_dict = {
            "name": "stored_energy",
            "stored_energy_kwh": stored_energy_kwh[0],
            "stored_energy_top_kwh": stored_energy_kwh[2],
            "stored_energy_bottom_kwh": stored_energy_kwh[1],
            "average_temperature": stored_energy_kwh[3]
        }
    topic = "sequentmicrosystems/stored_energy"
    #logging.info("topic: %s", topic)

    msg = json.dumps(msg_dict)
    publish(client,topic,msg)
    return

def ftx(client):
    
    if args.test_mode == "false":
        uteluft = input_array.mean(2)[2,0]  # sensor marked 4
        avluft = input_array.mean(2)[2,1]   # sensor marked 5
        tilluft = input_array.mean(2)[2,2]  # sensor marked 6
        franluft = input_array.mean(2)[2,3] # sensor marked 7
        effekt_varmevaxlare = round(100 - (avluft/franluft*100),2)
        #logging.info("stored_energy_kwh: %s", stored_energy_kwh)

    elif args.test_mode == "true":
        uteluft = input_array.mean(2)[2,0]  # sensor marked 4
        avluft = input_array.mean(2)[2,1]   # sensor marked 5
        tilluft = input_array.mean(2)[2,2]  # sensor marked 6
        franluft = input_array.mean(2)[2,3] # sensor marked 7
        effekt_varmevaxlare = round(100 - (avluft/franluft*100),2)
        #logging.info("stored_energy_kwh: %s", stored_energy_kwh)

    msg_dict = {
            "name": "ftx",
            "effekt_varmevaxlare": effekt_varmevaxlare,
            "uteluft": uteluft,
            "avluft": avluft,
            "tilluft": tilluft,
            "franluft": franluft
        }

    topic = "sequentmicrosystems/ftx"
    #logging.info("topic: %s", topic)

    msg = json.dumps(msg_dict)
    publish(client,topic,msg)
    return

#========================== sun heat collector ==========================
def main_sun_collector():


    if args.test_mode == "false":
        logging.info("test_mode: %s", args.test_mode)

    elif args.test_mode == "true":
        logging.info("sun collector in testmode")
        T1 = mqtt_sun[0]
        T2 = mqtt_sun[1]
        dT = round(T1-T2,1);
        logging.info("T1: %s, T2: %s, dT: %s", T1, T2, dT)
        

    return
#========================== Main execution ==========================
if __name__ == "__main__":
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")
    logging.info("debug_mode: %s", args.debug_mode)
    logging.info("test_mode: %s", args.test_mode)
    mqtt_client_connected = run()
    pipeline = queue.Queue(maxsize=10)
    event = threading.Event()
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        executor.submit(producer, pipeline, event)
        executor.submit(execution, pipeline, event)
        executor.submit(sender, pipeline, event)
        time.sleep(0.1)
        logging.info("Main: about to set event")
        event.set()
