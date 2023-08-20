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
SUB_TOPIC_3 = "hass/pump"
SUB_TOPIC_4 = "hass/delta_temp_start_tank_1"
SUB_TOPIC_5 = "hass/delta_temp_stop_tank_1"
SUB_TOPIC_6 = "hass/kylning_kollektor"
SUB_TOPIC_7 = "hass/set_temp_tank_1"
SUB_TOPIC_8 = "hass/temp_kok"
SUB_TOPIC_9 = "hass/manuell_styrning"
SUB_TOPIC_10 = "hass/manuell_pump"
SUB_TOPIC_11 = "hass/test_mode"
SUB_TOPIC_12 = "hass/log_level"

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
set_temp_tank_1_hysteres = 2
set_temp_tank_1_gräns = set_temp_tank_1 - set_temp_tank_1_hysteres
dTStart_tank_1 = 8 # Temperaturdifferens mellan kollektor (T1) och Tank1 (T2) vid vilken pumpen startar laddnig mot tanken. (Inställbar 3 °C till 40 °C med fabriksinställning 7 °C)
dTStop_tank_1 = 4 # Temperaturdifferens mellan kollektor (T1) och Tank1 (T2) vid vilken pumpen stannar. (Inställbar 2 till ? (Set tank1 -2 °C) med fabriksinställning 3 °C)
kylning_kollektor = 90
temp_kok = 150
temp_kok_hysteres = 10
temp_kok_hysteres_gräns = temp_kok - temp_kok_hysteres
solfangare_manuell_styrning = False # manuell kontroll av styrningen
solfångare_manuell_pump = False # manuell strning av pumpen
mode = "startup"
state = 1
sub_state = 0
overheated = False
log_level = "info"
test_mode = False


#===== MQTT subscribe =====#
mqtt_rtd = np.zeros(9)
mqtt_sun = np.zeros(3)

#======Test variables =======#
test_pump = True

#==== Application parsing variables ====#
parser = argparse.ArgumentParser()

parser.add_argument("-d", "--debug", dest = "debug_mode", default = "false", help="true|false")
parser.add_argument("-t", "--test", dest = "test_mode", default = "false", help="true|false")

args = parser.parse_args()


def producer(queue, event):
    try:
        while not event.is_set():
            a = 1
            while not FLAG_EXIT:
                collect_sensor_data_mega(3,a,10)
                collect_sensor_data_rtd(0,a,10)
                a += 1
                if a > 8:
                    logging.debug("""input_array content: 
                                    %s""", input_array)
                    a = 1

        logging.info("Producer received event. Exiting")
    except Exception as e:
        logging.error("An error occurred in the producer function: %s" % e)


def execution(queue, event):
    try:
        while not event.is_set() or not queue.empty():
            logging.info("executor started, waiting 7sec")
            time.sleep(5)
            while not FLAG_EXIT:
                time.sleep(2)
                logging.debug("starting main_sun_collector!")
                main_sun_collector(mqtt_client_connected)

        logging.info("Consumer received event. Exiting")
    except Exception as e:
        logging.error("An error occurred in the execution function: %s" % e)

def sender(queue, event):
    try:
        while not event.is_set() or not queue.empty():
            time.sleep(5)
            while not FLAG_EXIT:
                try:
                    time.sleep(5)
                    # main_sun_collector(mqtt_client_connected)  
                    sensor_calculations(mqtt_client_connected)
                    stored_energy(mqtt_client_connected)
                    ftx(mqtt_client_connected)
                except Exception as e:
                    logging.error("An error occurred in the sender function: %s" % e)

        logging.info("Consumer received event. Exiting")
    except Exception as e:
        logging.error("An error occurred in the sender function: %s" % e)

def logging_testmode(queue, event):
    global test_mode
    global log_level
    try:
        while not event.is_set() or not queue.empty():
            while not FLAG_EXIT:
                if args.debug_mode == "true":
                    log_level = "debug"


                if log_level == "debug":       
                    logging.basicConfig(filename="temperature_monitoring.log",
                        filemode='a',
                        format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.DEBUG)
                else:
                    logging.basicConfig(filename="temperature_monitoring.log",
                        filemode='a',
                        format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.INFO)

                if args.test_mode == "true":
                    test_mode = True 
                
                
                #logging.info("debug_mode: %s", debug_mode)
                #logging.info("test_mode: %s", test_mode)


        logging.info("Consumer received event. Exiting")
    except Exception as e:
        logging.error("An error occurred in the execution function: %s" % e)


#========================== MQTT setup ==========================
def on_connect(client, userdata, flags, rc):
    try:
        if rc == 0 and client.is_connected():
            print("Connected to MQTT Broker!")
            #client.subscribe(SUB_TOPIC_1)
            client.subscribe([(SUB_TOPIC_1, 0), (SUB_TOPIC_2, 0), (SUB_TOPIC_3, 0),(SUB_TOPIC_4, 0), (SUB_TOPIC_5, 0), (SUB_TOPIC_6, 0), (SUB_TOPIC_7, 0), (SUB_TOPIC_8, 0), (SUB_TOPIC_9, 0),(SUB_TOPIC_10, 0),(SUB_TOPIC_11, 0),(SUB_TOPIC_12, 0)])
        else:
            print(f'Failed to connect, return code {rc}')
    except Exception as e:
        print("An error occurred in the on_connect function:", e)


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
    global set_temp_tank_1
    global set_temp_tank_1_hysteres
    global dTStart_tank_1 #
    global dTStop_tank_1
    global kylning_kollektor
    global temp_kok
    global temp_kok_hysteres
    global solfangare_manuell_styrning
    global solfångare_manuell_pump
    global test_pump
    global test_mode
    global log_level

    if log_level == "true": print(f'Received `{msg.payload.decode()}` from `{msg.topic}` SUB_TOPIC')
    
    if msg.topic == "rtd/acctank":
        try:
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
            logging.debug("mqtt_rtd %s", mqtt_rtd)
            logging.debug("mqtt_sun %s", mqtt_sun)
        except Exception as err:
            logging.error("%s. message from topic == %s", err, msg.topic)
    elif msg.topic == "hass/pump":
        try:
            x = json.loads(msg.payload.decode())
            test_pump = x["pump"]
            logging.debug("test_pump: %s", test_pump)
        except Exception as err:
            logging.debug("%s. message from topic == %s", err, msg.topic)
    elif msg.topic == "hass/delta_temp_start_tank_1":
        try:
            x = json.loads(msg.payload.decode())
            dTStart_tank_1 = x["state"]
            logging.debug("dTStart_tank_1: %s", dTStart_tank_1)
        except Exception as err:
            logging.error("%s. message from topic == %s", err, msg.topic)
    elif msg.topic == "hass/delta_temp_stop_tank_1":
        try:
            x = json.loads(msg.payload.decode())
            dTStop_tank_1 = x["state"]
            logging.debug("dTStop_tank_1: %s", dTStop_tank_1)
        except Exception as err:
            logging.error("%s. message from topic == %s", err, msg.topic)
    elif msg.topic == "hass/kylning_kollektor":
        try:
            x = json.loads(msg.payload.decode())
            kylning_kollektor = x["state"]
            logging.debug("kylning_kollektor: %s", kylning_kollektor)
        except Exception as err:
            logging.error("%s. message from topic == %s", err, msg.topic)
    elif msg.topic == "hass/set_temp_tank_1":
        try:
         x = json.loads(msg.payload.decode())
         set_temp_tank_1 = x["state"]
         logging.debug("set_temp_tank_1: %s", set_temp_tank_1)
        except Exception as err:
            logging.error("%s. message from topic == %s", err, msg.topic)
    elif msg.topic == "hass/temp_kok":
        try:
            x = json.loads(msg.payload.decode())
            temp_kok = x["state"]
            logging.debug("temp_kok: %s", temp_kok)
        except Exception as err:
            logging.error("%s. message from topic == %s", err, msg.topic)
    elif msg.topic == "hass/manuell_styrning":
        try:
            x = json.loads(msg.payload.decode())
            if x["state"] == 0:
                solfangare_manuell_styrning = False
            elif x["state"] == 1:
                solfangare_manuell_styrning = True
            logging.debug("solfangare_manuell_styrning: %s", solfangare_manuell_styrning)
        except Exception as err:
            logging.error("%s. message from topic == %s", err, msg.topic)
    elif msg.topic == "hass/manuell_pump":
        try:
            x = json.loads(msg.payload.decode())
            if x["state"] == 0:
                solfångare_manuell_pump = False
            elif x["state"] == 1:
                solfångare_manuell_pump = True
            logging.debug("solfångare_manuell_pump: %s", solfångare_manuell_pump)
        except Exception as err:
            logging.error("%s. message from topic == %s", err, msg.topic)
    elif msg.topic == "hass/test_mode":
        try:
            x = json.loads(msg.payload.decode())
            if x["state"] == 0:
                test_mode = False
            elif x["state"] == 1:
                test_mode = True
            logging.debug("test_mode: %s", test_mode)
        except Exception as err:
            logging.error("%s. message from topic == %s", err, msg.topic)
    elif msg.topic == "hass/log_level":
        try:
            x = json.loads(msg.payload.decode())
            if x["state"] == 0:
                log_level = "info"
            elif x["state"] == 1:
                log_level = "debug"
            logging.debug("log_level: %s", log_level)
        except Exception as err:
            logging.error("%s. message from topic == %s", err, msg.topic)



    
def connect_mqtt():
    try:
        client = mqtt_client.Client(CLIENT_ID)
        client.username_pw_set(USERNAME, PASSWORD)
        client.on_connect = on_connect
        client.on_message = on_message
        client.connect(BROKER, PORT, keepalive=3)
        client.on_disconnect = on_disconnect
        return client
    except Exception as e:
        print("An error occurred in the connect_mqtt function:", e)


#========================== megabas ==========================
def collect_sensor_data_mega(stack,input,iterations):
    i = 0
    try:
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
    except Exception as err:
        logging.error("%s. from collect_sensor_data_mega: stack(%s), input(%s), iteration(%s), collect(%s)", err,stack,input,iterations,collect)
    
def read_megabas_1k(stack, input):
    limit = [1000,1039,1077.9,1116.7,1155.4,1194,1232.4,1270.8,1309,1347.1,1385.1,1422.9,1460.7,1498.3,1535.8,1573.3,1610.5,1647.7,1684.8]
    delta = [3.9,3.89,3.88,3.87,3.86,3.84,3.84,3.82,3.81,3.8,3.78,3.78,3.76,3.75,3.75,3.72,3.72,3.71]

    sensor = m.getRIn1K(stack, input)
    mod_sensor = sensor*1000
    megabas_temp = "No value"
    try:    
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
    except Exception as err:
        logging.error("%s. from read_megabas_1k: stack(%s), input(%s), sensor(%s), mod_sensor(%s), megabas_temp(%s)", err,stack,input,sensor,mod_sensor,megabas_temp)
    
def calc_megabas_temp(calc, delta, deci):
    try:
        calculated_temp=(calc/delta)+deci
        round_calculated_temp = (round(calculated_temp, 1))
        return round_calculated_temp
    except Exception as err:
        logging.error("%s. from calc_megabas_temp: calc(%s), delta(%s), deci(%s), calculated_temp(%s), round_calculated_temp(%s)", err,calc,delta,deci,calculated_temp,round_calculated_temp)
    

#========================== rtd ==========================
def collect_sensor_data_rtd(stack, input, iterations):
    i = 0
    while i < iterations:
        try:
            collect_rtd = read_rtd(stack, input)
            if collect_rtd != 9999:
                stack_position = stack
                input_position = input-1
                input_array[stack_position,input_position,i] = collect_rtd
            else:
                stack_position = stack
                input_position = input-1
        except Exception as e:
            print("An error occurred:", str(e))
        
        i += 1
        time.sleep(0.02)
    return

def read_rtd(stack,input):
    try:
        temp = librtd.get(stack, input)
        if temp > 200 or temp < -50:
            temp = 9999
        return temp
    except ValueError:
        print("Error: Invalid input parameters")
        return None


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
def publish(client, topic, msg):
    try:
        if not client.is_connected():
            logging.error("publish: MQTT client is not connected!")
            time.sleep(1)
            return
        result = client.publish(topic, msg)
        status = result[0]
        if status == 0:
            if log_level == "true":
                print(f'Send `{msg}` to topic `{topic}`')
        else:
            print(f'Failed to send message to topic {topic}')
        time.sleep(0.1)
    except Exception as e:
        print(f'An error occurred: {str(e)}')

def run():
    try:
        client = connect_mqtt()
        client.loop_start()
        time.sleep(1)
        
        # Check if the client is connected before publishing the message
        if client.is_connected():
            # publish(client)
            return client
        else:
            client.loop_stop()
    
    # Catch any exceptions that may occur during execution
    except Exception as e:
        logging.error(f"An error occurred in run: {str(e)}")
        


#========================== data calculations ==========================
def sensor_calculations(client):
    try:
        # Iterate through the input array
        for x in range(4):
            for y in range(8):
                # Calculate the rounded value of the mean of the input array
                round_value = round(input_array.mean(2)[x,y],1)
                
                # Calculate the stack and sensor values
                stack = x+1
                sensor = y+1
                
                # Create the name of the sensor
                name = "sequentmicrosystems_{}_{}"
                
                # Create a dictionary with the sensor name and temperature
                msg_dict = {
                    "name": name.format(stack,sensor),
                    "temperature": round_value
                }
                
                # Create the topic path
                topic_path = "sequentmicrosystems/{}"
                topic = topic_path.format(name.format(stack,sensor))
                
                # Convert the message dictionary to JSON
                msg = json.dumps(msg_dict)
                
                # Publish the message to the MQTT broker
                publish(client, topic, msg)
    
    # Catch any exceptions that may occur during execution
    except Exception as e:
        logging.error(f"An error occurred in sensor_calculations: {str(e)}")


def stored_energy(client):
    try:
        stored_energy = np.zeros(10)
        logging.debug("stored_energy: %s", stored_energy)
        stored_energy_kwh = np.zeros(4)
        logging.debug("stored_energy_kwh: %s", stored_energy_kwh)
        if test_mode == False:
            zero_valu = 0 #temperature of the water that is comming to to the system from the well
            stack_1 = 0
            stack_2 = 2
            stored_energy[0] = ((input_array.mean(2)[stack_1,0]-zero_valu)*35)
            stored_energy[1] = ((input_array.mean(2)[stack_1,1]-zero_valu)*35)
            stored_energy[2] = ((input_array.mean(2)[stack_1,2]-zero_valu)*35)
            stored_energy[3] = ((input_array.mean(2)[stack_1,3]-zero_valu)*35)
            stored_energy[4] = ((input_array.mean(2)[stack_1,4]-zero_valu)*35)
            stored_energy[5] = ((input_array.mean(2)[stack_1,5]-zero_valu)*35)
            stored_energy[6] = ((input_array.mean(2)[stack_1,6]-zero_valu)*35)
            stored_energy[7] = ((input_array.mean(2)[stack_1,7]-zero_valu)*35)
#            stored_energy[8] = ((input_array.mean(2)[stack_2,6]-zero_valu)*35) # T2
            stored_energy[9] = ((input_array.mean(2)[stack_2,7]-zero_valu)*35) # T3
            #logging.debug("stored_energy[0]: %s", stored_energy[0])
            #logging.debug("stored_energy: %s", stored_energy)
            stored_energy_kwh[0] = round(np.sum(stored_energy)*4200/1000/3600,2)
            stored_energy_kwh[1] = round(np.sum(stored_energy[:5])*4200/1000/3600,2)
            stored_energy_kwh[2] = round(np.sum(stored_energy[5:])*4200/1000/3600,2)
            #logging.debug("stored_energy_kwh: %s", stored_energy_kwh)

        elif test_mode == True:
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
            #logging.debug("stored_energy[0]: %s", stored_energy[0])
            #logging.debug("stored_energy: %s", stored_energy)
            stored_energy_kwh[0] = round((np.sum(stored_energy)*4200/1000/3600),2)
            stored_energy_kwh[1] = round((np.sum(stored_energy[:5])*4200/1000/3600),2)
            stored_energy_kwh[2] = round((np.sum(stored_energy[4:])*4200/1000/3600),2)
            stored_energy_kwh[3] = round(np.mean(mqtt_rtd[:8]),2)
            #logging.debug("stored_energy_kwh: %s", stored_energy_kwh)

        msg_dict = {
                "name": "stored_energy",
                "stored_energy_kwh": stored_energy_kwh[0],
                "stored_energy_top_kwh": stored_energy_kwh[2],
                "stored_energy_bottom_kwh": stored_energy_kwh[1],
                "average_temperature": stored_energy_kwh[3]
            }
        topic = "sequentmicrosystems/stored_energy"
        logging.debug("topic: %s", topic)

        msg = json.dumps(msg_dict)
        publish(client,topic,msg)
        return
    except Exception as e:
        logging.error(f"An error occurred in stored_energy: {str(e)}")

def ftx(client):
    try:
        effekt_varmevaxlare = 0
        if test_mode == False:
            uteluft = round(input_array.mean(2)[2,0],2)  # sensor marked 4
            avluft = round(input_array.mean(2)[2,1],2)   # sensor marked 5
            tilluft = round(input_array.mean(2)[2,2],2)  # sensor marked 6
            franluft = round(input_array.mean(2)[2,3],2) # sensor marked 7
            effekt_varmevaxlare = round(100 - (avluft/franluft*100),2)

        elif test_mode == True:
            uteluft = round(input_array.mean(2)[2,0],2)  # sensor marked 4
            avluft = round(input_array.mean(2)[2,1],2)   # sensor marked 5
            tilluft = round(input_array.mean(2)[2,2],2)  # sensor marked 6
            franluft = round(input_array.mean(2)[2,3],2) # sensor marked 7
            effekt_varmevaxlare = round(100 - (avluft/franluft*100),2)

        msg_dict = {
            "name": "ftx",
            "effekt_varmevaxlare": effekt_varmevaxlare,
            "uteluft": uteluft,
            "avluft": avluft,
            "tilluft": tilluft,
            "franluft": franluft
        }

        topic = "sequentmicrosystems/ftx"

        msg = json.dumps(msg_dict)
        publish(client,topic,msg)
    except Exception as e:
        print(f"An error occurred in ftx: {str(e)}")
    return None


#========================== sun heat collector ==========================
def main_sun_collector(client):
    try:
        global test_pump
        global overheated
        global mode
        global state
        global sub_state
        dT_running = 0
        dT = 0
        topic = "test/sequentmicrosystems/problem"
        current_pump_status = True
        start_pump = None 
        stop_pump = None
        
        if test_mode == False:
            logging.info("test_mode: %s", test_mode)
            logging.info("sun collector in production mode")
            T1 = round(input_array.mean(2)[2,5],2)  # sensor marked I
            T2 = round(input_array.mean(2)[2,6],2) # sensor marked II
            #T3 = round(input_array.mean(2)[2,7],2)  # sensor marked III
            dT = round(T1-T2,1);
            #start_pump = set_relay(4, 1, 0)
            #stop_pump = set_relay(4, 1, 1)
            logging.debug("T1: %s, T2: %s, dT: %s, current_pump_status: %s", T1, T2, dT, current_pump_status)
            
            #Pumpen är kopplad som NC(Normaly Closed) så värdena måste inverteras i koden
            if lib4relind.get_relay(2, 1) == 0:
                current_pump_status = True
            elif lib4relind.get_relay(2, 1) == 1:
                current_pump_status = False

            #skapar en entitet för att mäta energimängd när pumpen är på
            if current_pump_status == True:
                dT_running = dT
                logging.debug("dT_running: %s", dT_running)
                logging.debug("solfangare_manuell_styrning: %s, T1:%s, temp_kok:%s, overheated:%s, state:%s , mode:%s", solfangare_manuell_styrning, T1, temp_kok,overheated, state, mode)
            else:
                dT_running = 0
                logging.debug("dT_running: %s", dT_running)
                logging.debug("solfangare_manuell_styrning: %s, T1:%s, temp_kok:%s, overheated:%s, state:%s , mode:%s", solfangare_manuell_styrning, T1, temp_kok,overheated, state, mode)
            #######################
            # kollar om manuell styrning är påslagen, mode "10-11"
            if solfangare_manuell_styrning == True:
                logging.debug("solfångare_manuell_pump: %s", solfångare_manuell_pump)
                if solfångare_manuell_pump == True:
                    start_pump
                    mode = "10"
                    state = 1
                    sub_state = 0
                elif solfångare_manuell_pump == False:
                    stop_pump
                    mode = "11"
                    state = 1
                    sub_state = 1
            # Kollar om temperaturen är över eller ha varit över temp_kok, mode "20-21" 
            elif T1 >= temp_kok or overheated == True:
                logging.debug("T1(%s) >= temp_kok(%s), overheated(%s) == True and T1(%s) < temp_kok_hysteres_gräns(%s)", T1, temp_kok,overheated,T1,temp_kok_hysteres_gräns)
                if T1 >= temp_kok:
                    overheated = True
                    stop_pump
                    mode = "20"
                    state = 2
                    sub_state = 0
                    #När temperaturen i kollktorn har varit över temp_kok-gränsen men har gått under hysteresgränsen
                elif overheated == True and T1 < temp_kok_hysteres_gräns:
                    overheated = False
                    start_pump
                    mode = "21"
                    state = 2
                    sub_state = 1
            # Om pumpen är avslagen eller startup läge, mode "30-32"
            elif current_pump_status == False or mode == "startup":
                logging.debug("dT(%s) >= dTStart_tank_1(%s) and T2(%s) <= set_temp_tank_1(%s), T1(%s) >= kylning_kollektor(%s), mode(%s)", dT, dTStart_tank_1, T2, set_temp_tank_1, T1, kylning_kollektor, mode)
                # starta pumpen om dT är lika med eller större än satt nivå och T2 är under satt nivå
                if dT >= dTStart_tank_1 and T2 <= set_temp_tank_1_gräns:
                    start_pump
                    mode = "30"
                    state = 3
                    sub_state = 0
                # starta pump om kollektor blir för varm men inte om den överstiger "temp_kok" grader
                elif T1 >= kylning_kollektor:
                    start_pump
                    mode = "31"
                    state = 3
                    sub_state = 1
                elif mode == "startup":
                    start_pump
                    mode = "32"
                    state = 3
                    sub_state = 2
                else:    
                    logging.debug("T2:%s, T1:%s, , dT:%s, current_pump_status:%s, mode;%s, state:%s, sub_state:%s", T2, T1, dT, current_pump_status, mode, state, sub_state)
            # Pumpmen är påslagen, mode "40-41
            elif current_pump_status == True:
                logging.debug("dT(%s) <= dTStop_tank_1(%s), T2(%s) >= set_temp_tank_1_gräns(%s) and T1(%s) <= kylning_kollektor(%s)", dT, dTStop_tank_1, T2, set_temp_tank_1_gräns, T1, kylning_kollektor)
                #stoppa pumpen när dT går under satt nivå
                if dT <= dTStop_tank_1:
                    stop_pump
                    mode = "40"
                    state = 4
                    sub_state = 0
                #stäng av pumpen när den nåt rätt nivå och kollektor inte är för varm
                elif T2 >= set_temp_tank_1 and T1 <= kylning_kollektor:
                    stop_pump
                    mode = "41"
                    state = 4
                    sub_state = 1
                else:    
                    logging.debug("T2:%s, T1:%s, , dT:%s, current_pump_status:%s, mode;%s, state:%s, sub_state:%s", T2, T1, dT, current_pump_status, mode, state, sub_state)
                    #mode = "42"
                    #state = 4
                    #sub_state = 2

            #######################
            topic = "sequentmicrosystems/suncollector"
            logging.debug("topic: %s", topic)

        elif test_mode == True:
            logging.info("test_mode: %s", test_mode)
            logging.info("sun collector in test mode")
            T1 = mqtt_sun[0]
            T2 = mqtt_sun[1]
            dT = round(T1-T2,1);
            logging.debug("T1: %s, T2: %s, dT: %s, test_pump: %s", T1, T2, dT, test_pump)
            
            #skapar en entitet för att mäta energimängd när pumpen är på
            if test_pump == True:
                dT_running = dT
                logging.debug("dT_running: %s", dT_running)
                logging.debug("solfangare_manuell_styrning: %s, T1:%s, temp_kok:%s, overheated:%s, state:%s , mode:%s", solfangare_manuell_styrning, T1, temp_kok,overheated, state, mode)
            else:
                dT_running = 0
                logging.debug("dT_running: %s", dT_running)
                logging.debug("solfangare_manuell_styrning: %s, T1:%s, temp_kok:%s, overheated:%s, state:%s , mode:%s", solfangare_manuell_styrning, T1, temp_kok,overheated, state, mode)
            
            # kollar om manuell styrning är påslagen
            if solfangare_manuell_styrning == True:
                logging.debug("solfångare_manuell_pump: %s", solfångare_manuell_pump)
                if solfångare_manuell_pump == True:
                    test_pump = True
                    #lib4relind.set_relay(2, 1, 0)
                    mode = "10"
                    state = 1
                    sub_state = 0
                elif solfångare_manuell_pump == False:
                    test_pump = False
                    #lib4relind.set_relay(2, 1, 1)
                    mode = "11"
                    state = 1
                    sub_state = 1
            # Kollar om temperaturen är över eller ha varit över temp_kok 
            elif T1 >= temp_kok or overheated == True:
                logging.debug("T1(%s) >= temp_kok(%s), overheated(%s) == True and T1(%s) < temp_kok_hysteres_gräns(%s)", T1, temp_kok,overheated,T1,temp_kok_hysteres_gräns)
                if T1 >= temp_kok:
                    overheated = True
                    test_pump = False
                    mode = "20"
                    state = 2
                    sub_state = 0
                    #När temperaturen i kollktorn har varit över temp_kok-gränsen men har gått under hysteresgränsen
                elif overheated == True and T1 < temp_kok_hysteres_gräns:
                    overheated = False
                    test_pump = True
                    mode = "21"
                    state = 2
                    sub_state = 1
            # Om pumpen är avslagen eller startup läge
            elif test_pump == False or mode == "startup":
                logging.debug("dT(%s) >= dTStart_tank_1(%s) and T2(%s) <= set_temp_tank_1(%s), T1(%s) >= kylning_kollektor(%s), mode(%s)", dT, dTStart_tank_1, T2, set_temp_tank_1, T1, kylning_kollektor, mode)
                # starta pumpen om dT är lika med eller större än satt nivå och T2 är under satt nivå
                if dT >= dTStart_tank_1 and T2 <= set_temp_tank_1_gräns:
                    test_pump = True
                    mode = "30"
                    state = 3
                    sub_state = 0
                # starta pump om kollektor blir för varm men inte om den överstiger "temp_kok" grader
                elif T1 >= kylning_kollektor:
                    test_pump = True
                    mode = "31"
                    state = 3
                    sub_state = 1
                elif mode == "startup":
                    test_pump = True
                    mode = "32"
                    state = 3
                    sub_state = 2
                else:    
                    logging.debug("T2:%s, T1:%s, , dT:%s, test_pump:%s, mode;%s, state:%s, sub_state:%s", T2, T1, dT, test_pump, mode, state, sub_state)
            # Pumpmen är påslagen
            elif test_pump == True:
                logging.debug("dT(%s) <= dTStop_tank_1(%s), T2(%s) >= set_temp_tank_1_gräns(%s) and T1(%s) <= kylning_kollektor(%s)", dT, dTStop_tank_1, T2, set_temp_tank_1_gräns, T1, kylning_kollektor)
                #stoppa pumpen när dT går under satt nivå
                if dT <= dTStop_tank_1:
                    test_pump = False
                    mode = "40"
                    state = 4
                    sub_state = 0
                #stäng av pumpen när den nåt rätt nivå och kollektor inte är för varm
                elif T2 >= set_temp_tank_1 and T1 <= kylning_kollektor:
                    test_pump = False
                    mode = "41"
                    state = 4
                    sub_state = 1
                else:    
                    logging.debug("T2:%s, T1:%s, , dT:%s, test_pump:%s, mode;%s, state:%s, sub_state:%s", T2, T1, dT, test_pump, mode, state, sub_state)
                    #mode = "42"
                    #state = 4
                    #sub_state = 2
            topic = "test/sequentmicrosystems/suncollector"
            logging.debug("topic: %s", topic)

        msg_dict = {
                "name": "solfångare",
                "pump": test_pump,
                "mode": mode,
                "state": state,
                "sub_state": sub_state,
                "overheated": overheated,
                "dT_running": dT_running,
                "dT": dT,
                "test_mode": test_mode,
                "log_level": log_level
            }
        print(msg_dict)
        msg = json.dumps(msg_dict)
        publish(client,topic,msg)       
        return
    except Exception as e:
        print(f"An error occurred in main_sun_collector: {str(e)}")
        return None

#========================== Main execution ==========================

if __name__ == "__main__":
    try:
        mqtt_client_connected = run()
        pipeline = queue.Queue(maxsize=10)
        event = threading.Event()
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            executor.submit(logging_testmode, pipeline, event)
            executor.submit(producer, pipeline, event)
            executor.submit(execution, pipeline, event)
            executor.submit(sender, pipeline, event)
            time.sleep(0.1)
            logging.info("Main: about to set event")
            event.set()
    except Exception as e:
        logging.error("An error occurred in __main__: %s" % e)