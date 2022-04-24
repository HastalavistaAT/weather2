import random
import json
from datetime import datetime

from paho.mqtt import client as mqtt_client

import sched, time
import threading

broker = 'localhost'
port = 1883
topic = "home/rtl_433"
# generate client ID with pub prefix randomly
client_id = f'python-mqtt-{random.randint(0, 100)}'
# username = 'emqx'
# password = 'public'
last_update = datetime.now()

garden = {
  "channel": 1,
  "temperature_C": 0.0,
  "humidity": 0,
  "battery": 0,
}
greenhouse = {
  "channel": 2,
  "temperature_C": 0.0,
  "humidity": 0,
  "battery": 0,
}
attic = {
  "channel": 3,
  "temperature_C": 0.0,
  "humidity": 0,
  "battery": 0,
}
bedroom = {
  "channel": 7,
  "temperature_C": 0.0,
  "humidity": 0,
  "battery": 0,
}


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


def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        #print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
        message = json.loads(msg.payload.decode())
        channel = message["channel"]
        if (channel == 1): 
            garden["temperature_C"] =  5/9 * (message['temperature_F']-32)
            garden["humidity"] =  message['humidity']
            garden["battery"] =  message['battery_ok']
        elif (channel == 2): 
            greenhouse["temperature_C"] =  5/9 * (message['temperature_F']-32)
            greenhouse["humidity"] =  message['humidity']
            greenhouse["battery"] =  message['battery_ok']
        elif (channel == 3): 
            attic["temperature_C"] =  5/9 * (message['temperature_F']-32)
            attic["humidity"] =  message['humidity']
            attic["battery"] =  message['battery_ok']
        elif (channel == 7):  
            bedroom["temperature_C"] =  5/9 * (message['temperature_F']-32)
            bedroom["humidity"] =  message['humidity']
            bedroom["battery"] =  message['battery_ok']


    client.subscribe(topic)
    client.on_message = on_message

def display_update_checker(name):
    while True:
        time.sleep(10) # delay for 1 minute (60 seconds)
        last_update = datetime.now()
        print(garden)
        print(greenhouse)
        print(attic)
        print(bedroom)


def run():
    client = connect_mqtt()
    subscribe(client)
    x = threading.Thread(target=display_update_checker, args=(1,), daemon=True)
    x.start()
    client.loop_forever()


if __name__ == '__main__':
    run()