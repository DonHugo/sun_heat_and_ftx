import random
import json
import time
import megabas as m
import librtd
from paho.mqtt import client as mqttClient
import statistics
import numpy as np

# Application variables
collection = [0,0,0,0,0,0,0,0,0,0]
input_array = np.zeros((4, 8, 10))
#stack_array = np.zeros((4, 8))
loops = 10

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



def calc_megabas_temp(calc, delta, deci):
    calculated_temp=(calc/delta)+deci
    round_calculated_temp = (round(calculated_temp, 1))
    #p_calculated_temp = "calculated_temp: {}"
    #print(p_calculated_temp.format(calculated_temp))
    #p_round_calculated_temp = "round_calculated_temp: {}"
    #print(p_round_calculated_temp.format(round_calculated_temp))
    return round_calculated_temp

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

        #input_array_mean = input_array.mean(2)[stack_position,input_position]    
        #p_input_array_mean = "Input_array.mean(2){},{} = {}"     
        #print(p_input_array_mean.format(stack_position,input_position,input_array_mean))      
        i += 1
        time.sleep(0.02)
        #if input == 7 or input == 8:
        #    time.sleep(5)
        #else:
        #    time.sleep(0.02)
    
def board_megabas_values():
    board_type = "megabas"
    stack_level = 3
    hw_version = "4.1"
    sw_version = m.getVer(stack_level)
    board_name_prep = "{} stack {}"
    board_name = board_name_prep.format(board_type, stack_level)
    x = {
            "name": board_name,
            "HW version": hw_version,
            "SW version": sw_version,
            "power supply voltage": m.getInVolt(stack_level),
            "raspberry power supply voltage": m.getRaspVolt(stack_level),
            "board cpu temperature": m.getCpuTemp(stack_level)

        }
    y = json.dumps(x, ensure_ascii=False).encode('utf8')
    #print(x)
    print(y)
    #msg = y
    #topic_path = "sequentmicrosystems/{}"
    #topic = topic_path.format(board_name)
    #client.publish(topic,msg)
    
    return

def read_rtd(stack,input):
    temp = librtd.get(stack, input)
    if temp > 200 or temp < -50:
        #print("no sensor connected!")
        #template = "no sensor connected in stack {}, input {}"
        #temp = template.format(stack,input)
        temp = 9999
    #print(temp)
    #round_temp = round(temp,1)
    return temp

def collect_sensor_data_rtd(stack,input,iterations):
    i = 0
    while i < iterations:
        collect_rtd = read_rtd(stack, input)
        if collect_rtd != 9999:
            stack_position = stack-1
            #print(stack_position)
            input_position = input-1
            #print(rtd_position)
            input_array[stack_position,input_position,i] = collect_rtd
        else:
            stack_position = stack-1
            #print(stack_position)
            input_position = input-1
            #print(rtd_position)

        #input_array_mean = input_array.mean(2)[stack_position,input_position]    
        #p_input_array_mean = "Input_array.mean(2){},{} = {}"     
        #print(p_input_array_mean.format(stack_position,input_position,input_array_mean))   
        i += 1
        time.sleep(0.02)
    return


def read_onewire():
    print("========== OneWire ==========")
    #print(m.owbScan(3))
    print(m.owbGetSensorNo(3))
    print(m.owbGetTemp(3, 1))
    print(m.owbGetRomCode(3, 1))
    print("========== OneWire ==========")

    return

def collect_sensor_data_onewire():
    
    return
    
#get_temp()
#print(read_megabas_1k(3,6))
#print(read_megabas_1k(3,7))
#print(read_megabas_1k(3,8))
#print(read_rtd(4,1))
#board_megabas_values()
#read_onewire()

a=1
while True:
    p_a = "a (input) = {} "
    print(p_a.format(a))
    collect_sensor_data_mega(3,a,10)
    collect_sensor_data_rtd(4,a,10)
    print(input_array)
    a += 1
    if a > 8:
        a = 1
        if a == 7 or a == 8:
            time.sleep(10)
        else:
            time.sleep(1)
client.disconnect()
client.loop_stop()



