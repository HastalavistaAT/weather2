#!/usr/bin/python
import sys
import os
picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

import logging
from waveshare_epd import epd2in7b
from PIL import Image,ImageDraw,ImageFont
import traceback
import random
import json
from datetime import datetime

from paho.mqtt import client as mqtt_client

import sched, time
import threading

# settings
broker = 'localhost'
port = 1883
rtl_433_topic = "home/rtl_433"
currnet_price_topic = "home/awattar/current_price"
topic = [(rtl_433_topic,0),(currnet_price_topic,0)]
# generate client ID with pub prefix randomly
client_id = f'python-mqtt-{random.randint(0, 100)}'
# username = 'emqx'
# password = 'public'

# time in seconds between display refresh
display_refresh = 60

# time in seconds when data is considered exprired
expire_after_seconds = 240

garden = {
  "channel": 1,
  "temperature_C": 0.0,
  "humidity": 0,
  "battery": 0,
  "last_update": None,
}
greenhouse = {
  "channel": 2,
  "temperature_C": 0.0,
  "humidity": 0,
  "battery": 0,
  "last_update": None,
}
attic = {
  "channel": 3,
  "temperature_C": 0.0,
  "humidity": 0,
  "battery": 0,
  "last_update": None,
}
indoor = {
  "channel": 4,
  "temperature_C": 0.0,
  "humidity": 0,
  "battery": 0,
  "last_update": None,
}
bedroom = {
  "channel": 7,
  "temperature_C": 0.0,
  "humidity": 0,
  "battery": 0,
  "last_update": None,
}

current_price = 0.00

# settings for display
fontbold34 = ImageFont.truetype(os.path.join(picdir, 'ARLRDBD.TTF'), 34)
fontbold24 = ImageFont.truetype(os.path.join(picdir, 'ARLRDBD.TTF'), 24)
fontbold16 = ImageFont.truetype(os.path.join(picdir, 'ARLRDBD.TTF'), 16)
font24 = ImageFont.truetype(os.path.join(picdir, 'arial.ttf'), 24)
font18 = ImageFont.truetype(os.path.join(picdir, 'arial.ttf'), 18)
font16 = ImageFont.truetype(os.path.join(picdir, 'arial.ttf'), 16)
font14 = ImageFont.truetype(os.path.join(picdir, 'arial.ttf'), 14)
font12 = ImageFont.truetype(os.path.join(picdir, 'arial.ttf'), 12)

epd = None

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

def convert_F_to_C(fahrenheit):
    return 5/9 * (fahrenheit-32)

def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        #print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
        if msg.topic == currnet_price_topic:
            current_price = msg.payload.decode()
        elif msg.topic == rtl_433_topic:
            message = json.loads(msg.payload.decode())
            if (message['model'] == "Ambientweather-F007TH"):
                channel = message["channel"]
                if (channel == 1): 
                    garden["temperature_C"] =  convert_F_to_C(message['temperature_F'])
                    garden["humidity"] =  message['humidity']
                    garden["battery"] =  message['battery_ok']
                    garden["last_update"] = datetime.now()
                elif (channel == 2): 
                    greenhouse["temperature_C"] =  convert_F_to_C(message['temperature_F'])
                    greenhouse["humidity"] =  message['humidity']
                    greenhouse["battery"] =  message['battery_ok']
                    greenhouse["last_update"] = datetime.now()
                elif (channel == 3): 
                    attic["temperature_C"] =  convert_F_to_C(message['temperature_F'])
                    attic["humidity"] =  message['humidity']
                    attic["battery"] =  message['battery_ok']
                    attic["last_update"] = datetime.now()
                elif (channel == 4): 
                    indoor["temperature_C"] = convert_F_to_C(message['temperature_F'])
                    indoor["humidity"] =  message['humidity']
                    indoor["battery"] =  message['battery_ok']
                    indoor["last_update"] = datetime.now()
                elif (channel == 7):  
                    bedroom["temperature_C"] =  convert_F_to_C(message['temperature_F'])
                    bedroom["humidity"] =  message['humidity']
                    bedroom["battery"] =  message['battery_ok']
                    bedroom["last_update"] = datetime.now()
    client.subscribe(topic)
    client.on_message = on_message

def display_update_checker():
    while True:
        draw_display()
        time.sleep(display_refresh)
        
def draw_display():
    try:
        current_time = datetime.now()
        
        logging.info("Initialize Display")
        epd = epd2in7b.EPD()
        epd.init()
        
        logging.info("Draw display")
        
        HBlackimage = Image.open(os.path.join(picdir, 'result_black.bmp'))
        HRedimage = Image.open(os.path.join(picdir, 'result_red.bmp'))

        drawblack = ImageDraw.Draw(HBlackimage)
        drawred = ImageDraw.Draw(HRedimage)
        drawblack.line((200, 0, 200, 176), fill = 0)
        drawblack.line((100, 0, 100, 88), fill = 0)
        drawblack.line((67, 88, 67, 156), fill = 0)
        drawblack.line((133, 88, 133, 156), fill = 0)
        drawblack.line((0, 88, 200, 88), fill = 0)
        drawblack.line((0, 156, 200, 156), fill = 0)
        
        # drawred.rectangle((201, 0, 264, 176), fill = 0)

        # first row first column
        if (garden['temperature_C'] > 0 and garden['temperature_C'] < 30):
            drawblack.text((50, 23), f"{str(round(garden['temperature_C'], 1))}°", font = fontbold34, align='center', fill = 0, anchor="mm")
        else:
            drawred.text((50, 23), f"{str(round(garden['temperature_C'], 1))}°", font = fontbold34, align='center', fill = 0, anchor="mm")
        drawblack.text((75, 55), f"{garden['humidity']}%", font = font24, align='center', fill = 0, anchor="mm")
        
        # check if data is up2date
        if (garden["last_update"] != None):
            if ((current_time - garden['last_update']).total_seconds() > expire_after_seconds):
                drawred.rectangle((0, 0, 99, 87), fill = 0)
        else:
            drawred.rectangle((0, 0, 99, 87), fill = 0)

        # drawblack.text((50, 78), "Garten", font = font18, align='center', fill = 0, anchor="mm")
        
        # first row second column
        drawblack.text((150, 23), f"{str(round(indoor['temperature_C'], 1))}°", font = fontbold34, align='center', fill = 0, anchor="mm")
        drawblack.text((175, 55), f"{indoor['humidity']}%", font = font24, align='center', fill = 0, anchor="mm")   
        # drawblack.text((150, 78), "Wohnraum", font = font18, align='center', fill = 0, anchor="mm")

        # check if data is up2date
        if (indoor["last_update"] != None):
            if ((current_time - indoor['last_update']).total_seconds() > expire_after_seconds):
                drawred.rectangle((101, 0, 199, 87), fill = 0)
        else:
            drawred.rectangle((101, 0, 199, 87), fill = 0)

        # second row first column
        if (greenhouse['temperature_C'] > 10 and greenhouse['temperature_C'] < 30):
            drawblack.text((33, 104), f"{str(round(greenhouse['temperature_C'], 1))}°", font = fontbold24, align='center', fill = 0, anchor="mm")
        else:
            drawred.text((33, 104), f"{str(round(greenhouse['temperature_C'], 1))}°", font = fontbold24, align='center', fill = 0, anchor="mm")
        drawblack.text((52, 130), f"{greenhouse['humidity']}%", font = font14, align='center', fill = 0, anchor="mm")   
        # drawblack.text((33, 148), "Gewächsh.", font = font12, align='center', fill = 0, anchor="mm")

        # check if data is up2date
        if (greenhouse["last_update"] != None):
            if ((current_time - greenhouse['last_update']).total_seconds() > expire_after_seconds):
                drawred.rectangle((0, 89, 66, 155), fill = 0)
        else:
            drawred.rectangle((0, 89, 66, 155), fill = 0)

        # second row second column
        drawblack.text((100, 104), f"{str(round(attic['temperature_C'], 1))}°", font = fontbold24, align='center', fill = 0, anchor="mm")
        drawblack.text((118, 130), f"{attic['humidity']}%", font = font14, align='center', fill = 0, anchor="mm")   
        # drawblack.text((100, 148), "Dachboden", font = font12, align='center', fill = 0, anchor="mm")
        
        # check if data is up2date
        if (attic["last_update"] != None):
            if ((current_time - attic['last_update']).total_seconds() > expire_after_seconds):
                drawred.rectangle((68, 89, 132, 155), fill = 0)
        else:
            drawred.rectangle((68, 89, 132, 155), fill = 0)

        # second row third column
        drawblack.text((166, 104), f"{str(round(bedroom['temperature_C'], 1))}°", font = fontbold24, align='center', fill = 0, anchor="mm")
        drawblack.text((182, 130), f"{bedroom['humidity']}%", font = font14, align='center', fill = 0, anchor="mm")   
        # drawblack.text((166, 148), "Schlafz.", font = font12, align='center', fill = 0, anchor="mm")

        # check if data is up2date
        if (bedroom["last_update"] != None):
            if ((current_time - bedroom['last_update']).total_seconds() > expire_after_seconds):
                drawred.rectangle((134, 89, 199, 155), fill = 0)
        else:
            drawred.rectangle((134, 89, 199, 155), fill = 0)

        # right area
        drawblack.text((232, 16), f"{str(round(current_price, 1))}", font = fontbold24, align='center', fill = 0, anchor="mm")
        drawblack.text((232, 30), f"ct/kWh", font = font18, align='center', fill = 0, anchor="mm")

        # bottom line
        drawblack.text((42, 166), "05:58", font = fontbold16, align='center', fill = 0, anchor="mm")
        drawblack.text((100, 166), time.strftime('%H:%M'), font = fontbold16, align='center', fill = 0, anchor="mm")
        drawblack.text((176, 166), "20:05", font = fontbold16, align='center', fill = 0, anchor="mm")

        epd.display(epd.getbuffer(HBlackimage), epd.getbuffer(HRedimage))
        
        logging.info("Goto Sleep...")
        epd.sleep()
            
    except IOError as e:
        logging.info(e)
        
    except KeyboardInterrupt:    
        logging.info("ctrl + c:")
        epd2in7b.epdconfig.module_exit()
        exit()

def run():
    client = connect_mqtt()
    subscribe(client)
    x = threading.Thread(target=display_update_checker, daemon=True)
    x.start()
    client.loop_forever()


if __name__ == '__main__':
    run()