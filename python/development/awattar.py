#!/usr/bin/python

import datetime
from paho.mqtt import client as mqtt_client
import time
import json
from types import SimpleNamespace
import requests
import random

# settings
broker = 'localhost'
port = 1883
topic = "home/awattar"
# generate client ID with pub prefix randomly
client_id = f'python-mqtt-{random.randint(0, 100)}'
# username = 'emqx'
# password = 'public'

def connect_mqtt() -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    #client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

def publish(message):
    global client
    def on_publish(client,userdata,result):             #create function for callback
        print("data published \n")
        pass
    client.on_publish = on_publish                          #assign function to callback
    client.publish(topic,message)                   #publish

def load_prices():
    response = requests.get("https://api.awattar.at/v1/marketdata")
    message = response.text
    # print (message)
    data = json.loads(message, object_hook=lambda d: SimpleNamespace(**d))
    print (data.data[0])
    testtimestamp = data.data[0].start_timestamp
    print (testtimestamp)
    print(datetime.datetime.utcfromtimestamp(testtimestamp).strftime('%Y-%m-%d %H:%M:%S'))
    
def loop():
    while True:
        load_prices()
        publish("test")
        time.sleep(3600)

def run():
    global client
    client = connect_mqtt()
    loop()

if __name__ == '__main__':
    run()