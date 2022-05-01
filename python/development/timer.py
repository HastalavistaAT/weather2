#!/usr/bin/python
import random
import time, datetime

# Formel von Dr. Roland Brodbeck, Calsky
# http://lexikon.astronomie.info/zeitgleichung/neu.html
# Uebertragung auf Python 3 von Alexander Klupp 2014-01-14

import math
from paho.mqtt import client as mqtt_client

pi2 = 2*math.pi
pi = math.pi
RAD = math.pi/180

def JulianischesDatum (Jahr, Monat, Tag, Stunde, Minuten, Sekunden):
    if (Monat <= 2):
        Monat = Monat + 12
        Jahr = Jahr - 1
    Gregor = (Jahr/400) - (Jahr/100) + (Jahr/4)  # Gregorianischer Kalender
    return 2400000.5 + 365 * Jahr - 679004 + Gregor \
           + math.floor(30.6001*(Monat + 1)) + Tag + Stunde/24 \
           + Minuten/1440 + Sekunden/86400

def InPi(x):
    n = int(x/pi2)
    x = x - n*pi2
    if (x < 0):
        x += pi2
    return x

def eps(T): # Neigung der Erdachse
    return RAD*(23.43929111 + (-46.8150*T - 0.00059*T**2 + 0.001813*T**3)/3600)

def BerechneZeitgleichung(T):
    RA_Mittel = 18.71506921 + 2400.0513369*T +(2.5862e-5 - 1.72e-9*T)*T**2
    M  = InPi(pi2*(0.993133 + 99.997361*T))
    L  = InPi(pi2*(0.7859453 + M/pi2 \
                   + (6893*math.sin(M) + 72*math.sin(2*M) + 6191.2*T) / 1296e3))
    e = eps(T)
    RA = math.atan(math.tan(L)*math.cos(e))
    if (RA < 0):
        RA += pi
    if (L > pi):
        RA += pi
    RA = 24*RA/pi2
    DK = math.asin(math.sin(e)*math.sin(L))
    #Damit 0 <= RA_Mittel < 24
    RA_Mittel = 24.0*InPi(pi2*RA_Mittel/24.0)/pi2
    dRA = RA_Mittel - RA
    if (dRA < -12.0):
        dRA += 24.0
    if (dRA > 12.0):
        dRA -= 24.0
    dRA = dRA* 1.0027379
    return dRA, DK

JD2000 = 2451545
h = -50.0/60.0*RAD
B = math.radians(48.275857)       # geographische Breite
GeographischeLaenge = 14.207694   # geographische Laenge

def Sonnenauf_untergang (JD, Zeitzone):
    # Zeitzone = 0 #Weltzeit
    # Zeitzone = 1 #Winterzeit
    # Zeitzone = 2 #Sommerzeit
    # JD = JulianischesDatum
        
    T = (JD - JD2000)/36525

    Zeitgleichung, DK = BerechneZeitgleichung(T)

    Minuten = Zeitgleichung*60

    Zeitdifferenz = 12*math.acos((math.sin(h) - math.sin(B)*math.sin(DK)) \
                             / (math.cos(B)*math.cos(DK)))/pi

    AufgangOrtszeit = 12 - Zeitdifferenz - Zeitgleichung
    UntergangOrtszeit = 12 + Zeitdifferenz - Zeitgleichung
    AufgangWeltzeit = AufgangOrtszeit - GeographischeLaenge/15
    UntergangWeltzeit = UntergangOrtszeit - GeographischeLaenge/15

    Aufgang = AufgangWeltzeit + Zeitzone
    if (Aufgang < 0):
        Aufgang += 24
    elif (Aufgang >= 24):
        Aufgang -= 24

    AM = round(Aufgang*60)/60 # minutengenau runden

    Untergang = UntergangWeltzeit + Zeitzone	
    if (Untergang < 0):
        Untergang += 24
    elif (Untergang >= 24):
        Untergang -= 24

    UM = round(Untergang*60)/60 # minutengenau runden
    
    return AM, UM

import RPi.GPIO as GPIO

def switchrelay(gpio):
    GPIO.setmode(GPIO.BCM)

    GPIO.setup(gpio, GPIO.OUT, initial=GPIO.HIGH)

    GPIO.output(gpio, GPIO.LOW)
    time.sleep(0.5)
    GPIO.output(gpio, GPIO.HIGH)

    GPIO.cleanup()
    print(datetime.datetime.now())

def time_in_range(start, end, x):
    # """Return true if x is in the range [start, end]"""
    if start <= end:
        return start <= x <= end
    else:
        return start <= x or x <= end

# settings
broker = 'localhost'
port = 1883
topic = "home/blinds"
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


UNKNOWN = 0
DOWN = -1
UP = 1

def calculate_open_time():
    lt = time.localtime() # Aktuelle, lokale Zeit als Tupel
    # Entpacken des Tupels
    lt_jahr, lt_monat, lt_tag = lt[0:3]        # Datum
    lt_dst = lt[8]                             # Sommerzeit

    AM, UM = Sonnenauf_untergang (JulianischesDatum(lt_jahr, lt_monat, lt_tag, 12, 0, 0), lt_dst + 1)

    AMh = int(math.floor(AM))
    AMm = int((AM - AMh)*60)

    # add some minutes so that closure is not happening too early and opening before sunrise
    sunrise = datetime.time(AMh, AMm, 0)
    sunrise_offset = datetime.datetime.combine(datetime.date.today(), sunrise) - datetime.timedelta(minutes = 30)
    return sunrise_offset

def calculate_close_time():
    lt = time.localtime() # Aktuelle, lokale Zeit als Tupel
    # Entpacken des Tupels
    lt_jahr, lt_monat, lt_tag = lt[0:3]        # Datum
    lt_dst = lt[8]                             # Sommerzeit

    AM, UM = Sonnenauf_untergang (JulianischesDatum(lt_jahr, lt_monat, lt_tag, 12, 0, 0), lt_dst + 1)

    UMh = int(math.floor(UM))
    UMm = int((UM - UMh)*60)

    # add some minutes so that closure is not happening too early and opening before sunrise
    sunset = datetime.time(UMh, UMm, 0)
    sunset_offset = datetime.datetime.combine(datetime.date.today(), sunset) + datetime.timedelta(minutes = 30)
    return sunset_offset

    
def loop():
    state = UNKNOWN
    time.sleep(1)
    while True:
           
        current_time = datetime.datetime.now().time()

        if (time_in_range(calculate_open_time(), calculate_close_time(), current_time)):
            if not state == UP:
                state = UP
                switchrelay(20)
                publish("up")
        else:
            if not state == DOWN:
                state = DOWN
                switchrelay(21)
                publish("down")
        time.sleep(60)


def run():
    global client
    client = connect_mqtt()
    loop()
    

if __name__ == '__main__':
    run()