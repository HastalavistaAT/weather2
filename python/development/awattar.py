#!/usr/bin/python

import datetime
#from paho.mqtt import client as mqtt_client
import time
import json
from types import SimpleNamespace
import requests
import random

# settings
update_frequency = 900 # seconds

broker = 'localhost'
port = 1883
# generate client ID with pub prefix randomly
client_id = f'python-mqtt-{random.randint(0, 100)}'
# username = 'emqx'
# password = 'public'

#def connect_mqtt() -> mqtt_client:
#    def on_connect(client, userdata, flags, rc):
#        if rc == 0:
#            print("Connected to MQTT Broker!")
#        else:
#            print("Failed to connect, return code %d\n", rc)
#
#    client = mqtt_client.Client(client_id)
#    #client.username_pw_set(username, password)
#    client.on_connect = on_connect
#    client.connect(broker, port)
#    return client

#def publish(message, topic):
#    global client
#    def on_publish(client,userdata,result):             #create function for callback
#        print("data published \n")
#        pass
#    client.on_publish = on_publish                          #assign function to callback
#    client.publish(topic,message)                   #publish

def load_prices():
    global prices
    global last_update
    presentDate = datetime.datetime.now()
    if last_update:
        #print (last_update.strftime('%Y-%m-%d %H:%M:%S'))
        timediff = presentDate-last_update
        # print (timediff)
        if timediff.total_seconds() >= update_frequency:
            enddate = presentDate + datetime.timedelta(days=2)
            unix_timestamp = datetime.datetime.timestamp(enddate)*1000
            try:
                response = requests.get("https://api.awattar.at/v1/marketdata?end="+str(unix_timestamp))
                message = response.text
                # print (message)
                data = json.loads(message, object_hook=lambda d: SimpleNamespace(**d))
                
                prices.clear()
                for val in data.data:
                    start = datetime.datetime.fromtimestamp(val.start_timestamp/1000)
                    end = datetime.datetime.fromtimestamp(val.end_timestamp/1000)
                    price = val.marketprice/10
                    prices.update({start:price})
                last_update = datetime.datetime.now()
                print(last_update.strftime('%Y-%m-%d %H:%M:%S'), " loaded new data from awattar")
            except:
                print(last_update.strftime('%Y-%m-%d %H:%M:%S'), " unable to load data from awattar")
            
    #print(get_current_price())

def get_current_price(): #in cent/kwh
    global prices
    presentDate = datetime.datetime.now()
    for key in prices:
        timediff = presentDate - key
        #print(key, timediff.total_seconds())
        if timediff.total_seconds() < 3600:
            return prices[key]

def get_lowest_price():
    lowest_prices = sorted(prices.items(), key=lambda x: x[1])
    if lowest_prices is not None and len(lowest_prices) >= 1:
        return next(iter(lowest_prices))
    else:
        return None


def loop():
    while True:
        load_prices()
        #publish(get_current_price(), "home/awattar/current_price")
        #publish(json.dumps(get_lowest_price()), "home/awattar/lowest_price")
        time.sleep(10)

def run():
    global client
    global prices
    global last_update
    # client = connect_mqtt()
    prices = {}
    last_update = datetime.datetime(1980,1,1,0,0,0,0)
    loop()

if __name__ == '__main__':
    run()
