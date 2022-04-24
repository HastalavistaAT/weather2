# weather2
Weather Station 2.0

**mqtt**
Mosquitto
Channel: home/rtl_433

RTL_433
rtl_433 -R20 -F json -M utc | mosquitto_pub -t home/rtl_433 -l
-R20 is the current sensors

Supervisor
https://www.hagensieker.com/wordpress/2019/03/06/how-to-keep-rtl_433-alive-for-your-home-automation-using-supervisor/

Convert Fahrenheit to Celsius: C = 5/9 x (F-32)
