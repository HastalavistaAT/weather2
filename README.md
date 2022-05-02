# weather2
Weather Station 2.0

**Hardware**

Raspberry Pi 2/3/4
Waveshare e-paper HAT 2.7inch (3-color: white, black, red)
DVB-T Receiver to listen to 433 MHz sensors

**mqtt**
Mosquitto
Channel: home/rtl_433
Used to listen to sensors and update the status of the blinds

**DVB-T Receiver**
RTL_433 for DVB-T receiver

Start with:
rtl_433 -R20 -F json -M utc | mosquitto_pub -t home/rtl_433 -l
-R20 is the current sensors from Dostmann
-> See rtl433.sh to start automatically with supervisor

Supervisor
https://www.hagensieker.com/wordpress/2019/03/06/how-to-keep-rtl_433-alive-for-your-home-automation-using-supervisor/

**wather2.py**
main application to run
This will render the display and listen to MQTT
it uses awattar.py and timer.py

**awattar.py**
ready the current and future prices for electricity

**timer.py**
calculate sunrise and sunset to open or close the blinds.
Calculation for Leonding/Austria
Adapt Lon/Lat accordingly
-> note: messy code!
