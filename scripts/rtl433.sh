#!/bin/bash
# start the program 10 times for 3 seconds in ortder to get a stable version up and running
# solution found here: https://github.com/merbanan/rtl_433/issues/1669
rtl_433 -T 3
rtl_433 -T 3
rtl_433 -T 3
rtl_433 -T 3
rtl_433 -T 3
rtl_433 -T 3
rtl_433 -T 3
rtl_433 -T 3
rtl_433 -T 3
rtl_433 -T 3
# listen to protocol 20 (TFA weather sensors) and publish on mosquitto
rtl_433 -R20 -F json -M utc | mosquitto_pub -t home/rtl_433 -l 
