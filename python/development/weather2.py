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
topic = "home/rtl_433"
# generate client ID with pub prefix randomly
client_id = f'python-mqtt-{random.randint(0, 100)}'
# username = 'emqx'
# password = 'public'

# time in seconds between display refresh
display_refresh = 60

garden = {
  "channel": 1,
  "temperature_C": 0.0,
  "humidity": 0,
  "battery": 0,
  "last_update": datetime.now,
}
greenhouse = {
  "channel": 2,
  "temperature_C": 0.0,
  "humidity": 0,
  "battery": 0,
  "last_update": datetime.now,
}
attic = {
  "channel": 3,
  "temperature_C": 0.0,
  "humidity": 0,
  "battery": 0,
  "last_update": datetime.now,
}
indoor = {
  "channel": 4,
  "temperature_C": 0.0,
  "humidity": 0,
  "battery": 0,
  "last_update": datetime.now,
}
bedroom = {
  "channel": 7,
  "temperature_C": 0.0,
  "humidity": 0,
  "battery": 0,
  "last_update": datetime.now,
}

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


def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        #print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
        message = json.loads(msg.payload.decode())
        channel = message["channel"]
        if (channel == 1): 
            garden["temperature_C"] =  5/9 * (message['temperature_F']-32)
            garden["humidity"] =  message['humidity']
            garden["battery"] =  message['battery_ok']
            garden["last_update"] = time.localtime
        elif (channel == 2): 
            greenhouse["temperature_C"] =  5/9 * (message['temperature_F']-32)
            greenhouse["humidity"] =  message['humidity']
            greenhouse["battery"] =  message['battery_ok']
            greenhouse["last_update"] = time.localtime
        elif (channel == 3): 
            attic["temperature_C"] =  5/9 * (message['temperature_F']-32)
            attic["humidity"] =  message['humidity']
            attic["battery"] =  message['battery_ok']
            attic["last_update"] = time.localtime
        elif (channel == 4): 
            indoor["temperature_C"] =  5/9 * (message['temperature_F']-32)
            indoor["humidity"] =  message['humidity']
            indoor["battery"] =  message['battery_ok']
            indoor["last_update"] = time.localtime
        elif (channel == 7):  
            bedroom["temperature_C"] =  5/9 * (message['temperature_F']-32)
            bedroom["humidity"] =  message['humidity']
            bedroom["battery"] =  message['battery_ok']
            bedroom["last_update"] = time.localtime


    client.subscribe(topic)
    client.on_message = on_message

def display_update_checker(name):
    while True:
        draw_display()
        time.sleep(display_refresh)
        
def draw_display():
    try:
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
        time_delta = datetime.now - garden['last_update']
        total_seconds = time_delta.total_seconds()
        if (total_seconds > 120):
            drawred.rectangle((0, 0, 99, 87), fill = 0)
        # drawblack.text((50, 78), "Garten", font = font18, align='center', fill = 0, anchor="mm")
        
        # first row second column
        drawblack.text((150, 23), f"{str(round(indoor['temperature_C'], 1))}°", font = fontbold34, align='center', fill = 0, anchor="mm")
        drawblack.text((175, 55), f"{indoor['humidity']}%", font = font24, align='center', fill = 0, anchor="mm")   
        # drawblack.text((150, 78), "Wohnraum", font = font18, align='center', fill = 0, anchor="mm")

        # second row first column
        if (greenhouse['temperature_C'] > 10 and greenhouse['temperature_C'] < 30):
            drawblack.text((33, 104), f"{str(round(greenhouse['temperature_C'], 1))}°", font = fontbold24, align='center', fill = 0, anchor="mm")
        else:
            drawred.text((33, 104), f"{str(round(greenhouse['temperature_C'], 1))}°", font = fontbold24, align='center', fill = 0, anchor="mm")
        drawblack.text((52, 130), f"{greenhouse['humidity']}%", font = font14, align='center', fill = 0, anchor="mm")   
        # drawblack.text((33, 148), "Gewächsh.", font = font12, align='center', fill = 0, anchor="mm")

        # second row second column
        drawblack.text((100, 104), f"{str(round(attic['temperature_C'], 1))}°", font = fontbold24, align='center', fill = 0, anchor="mm")
        drawblack.text((118, 130), f"{attic['humidity']}%", font = font14, align='center', fill = 0, anchor="mm")   
        # drawblack.text((100, 148), "Dachboden", font = font12, align='center', fill = 0, anchor="mm")
        
        # second row third column
        drawblack.text((166, 104), f"{str(round(bedroom['temperature_C'], 1))}°", font = fontbold24, align='center', fill = 0, anchor="mm")
        drawblack.text((182, 130), f"{bedroom['humidity']}%", font = font14, align='center', fill = 0, anchor="mm")   
        # drawblack.text((166, 148), "Schlafz.", font = font12, align='center', fill = 0, anchor="mm")

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
    x = threading.Thread(target=display_update_checker, args=(1,), daemon=True)
    x.start()
    client.loop_forever()


if __name__ == '__main__':
    run()