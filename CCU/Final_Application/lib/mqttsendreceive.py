import sys
import json
import paho.mqtt.client as mqtt
import csv
import time
import numpy as np 
import math
import lib.globals as globals


def on_connect(mqttc, obj, flags, rc):
    globals.VISION_connected = True
    print("rc: "+str(rc))

def on_message(mqttc, obj, msg):
    globals.mqtt_payload = str(msg.payload.decode("utf-8")) #messages received are printed from here
    temp = globals.mqtt_payload.split(",") # message received as "angle,strength" tuple
    globals.mqtt_angle = int(temp[0])
    globals.mqtt_strength = int(temp[0])
    globals.mqtt_turn = 1 # 1 means it is SCRATCH's turn to send
    print(f"Received angle {globals.mqtt_angle}, strength {globals.mqtt_strength}")
               
def on_publish(mqttc, obj, mid):
    print("mid: "+str(mid))

def on_subscribe(mqttc, obj, mid, granted_qos):
    print("Subscribed: "+str(mid)+" "+str(granted_qos))

def on_log(mqttc, obj, level, string):
    print(string)
    

globals.VISION_mqtt = mqtt.Client(transport='websockets')   
globals.VISION_mqtt.on_message = on_message
globals.VISION_mqtt.on_connect = on_connect
globals.VISION_mqtt.on_publish = on_publish
globals.VISION_mqtt.on_subscribe = on_subscribe
globals.VISION_mqtt.connect('broker.emqx.io', 8083, 60)
globals.VISION_mqtt.subscribe("t/sd/scratch", 0)

#ret = globals.VISION_mqtt.publish("t/sd/scratch","start") #use this line to send
globals.VISION_mqtt.loop_forever()
