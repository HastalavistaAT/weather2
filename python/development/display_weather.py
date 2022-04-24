#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

import logging
from waveshare_epd import epd2in7b
import time
from PIL import Image,ImageDraw,ImageFont
import traceback

logging.basicConfig(level=logging.DEBUG)

try:
    logging.info("Weather Display")
    
    epd = epd2in7b.EPD()
    epd.init()

    fontbold34 = ImageFont.truetype(os.path.join(picdir, 'ARLRDBD.TTF'), 34)
    fontbold24 = ImageFont.truetype(os.path.join(picdir, 'ARLRDBD.TTF'), 24)
    fontbold16 = ImageFont.truetype(os.path.join(picdir, 'ARLRDBD.TTF'), 16)
    font24 = ImageFont.truetype(os.path.join(picdir, 'arial.ttf'), 24)
    font18 = ImageFont.truetype(os.path.join(picdir, 'arial.ttf'), 18)
    font16 = ImageFont.truetype(os.path.join(picdir, 'arial.ttf'), 16)
    font14 = ImageFont.truetype(os.path.join(picdir, 'arial.ttf'), 14)
    font12 = ImageFont.truetype(os.path.join(picdir, 'arial.ttf'), 12)

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
    
    drawred.rectangle((201, 0, 264, 176), fill = 0)
#
    # first row first column
    drawred.text((50, 23), '-18.8°', font = fontbold34, align='center', fill = 0, anchor="mm")
    drawblack.text((75, 55), '48%', font = font24, align='center', fill = 0, anchor="mm")
    # drawblack.text((50, 78), "Garten", font = font18, align='center', fill = 0, anchor="mm")
    
    # first row second column
    drawblack.text((150, 23), '22.7°', font = fontbold34, align='center', fill = 0, anchor="mm")
    drawblack.text((175, 55), '42%', font = font24, align='center', fill = 0, anchor="mm")   
    # drawblack.text((150, 78), "Wohnraum", font = font18, align='center', fill = 0, anchor="mm")

    # second row first column
    drawred.text((33, 104), '-10.8°', font = fontbold24, align='center', fill = 0, anchor="mm")
    drawblack.text((52, 130), '99%', font = font14, align='center', fill = 0, anchor="mm")   
    # drawblack.text((33, 148), "Gewächsh.", font = font12, align='center', fill = 0, anchor="mm")

    # second row second column
    drawblack.text((100, 104), '35.7°', font = fontbold24, align='center', fill = 0, anchor="mm")
    drawblack.text((118, 130), '54%', font = font14, align='center', fill = 0, anchor="mm")   
    # drawblack.text((100, 148), "Dachboden", font = font12, align='center', fill = 0, anchor="mm")
    
    # second row third column
    drawblack.text((166, 104), '19.7°', font = fontbold24, align='center', fill = 0, anchor="mm")
    drawblack.text((182, 130), '58%', font = font14, align='center', fill = 0, anchor="mm")   
    # drawblack.text((166, 148), "Schlafz.", font = font12, align='center', fill = 0, anchor="mm")

    # bottom line
    drawblack.text((42, 166), "05:58", font = fontbold16, align='center', fill = 0, anchor="mm")
    drawblack.text((100, 166), "18:12", font = fontbold16, align='center', fill = 0, anchor="mm")
    drawblack.text((176, 166), "20:05", font = fontbold16, align='center', fill = 0, anchor="mm")



#    drawblack.text((10, 20), str(epd.width), font = font24, fill = 0)
#    drawblack.text((150, 0), str(epd.height), font = font24, fill = 0)    
#    drawblack.line((20, 50, 70, 100), fill = 0)
#    drawblack.line((70, 50, 20, 100), fill = 0)
#    drawblack.rectangle((20, 50, 70, 100), outline = 0)    
#    drawred.line((165, 50, 165, 100), fill = 0)
#    drawred.line((140, 75, 190, 75), fill = 0)
#    drawred.arc((140, 50, 190, 100), 0, 360, fill = 0)
#    drawred.rectangle((80, 50, 130, 100), fill = 0)
#    drawred.chord((200, 50, 250, 100), 0, 360, fill = 0)
    epd.display(epd.getbuffer(HBlackimage), epd.getbuffer(HRedimage))
#    time.sleep(20)
    
    # Drawing on the Vertical image
#    logging.info("2.Drawing on the Vertical image...")
#    LBlackimage = Image.new('1', (epd.width, epd.height), 255)  # 126*298
#    LRedimage = Image.new('1', (epd.width, epd.height), 255)  # 126*298
#    drawblack = ImageDraw.Draw(LBlackimage)
#    drawred = ImageDraw.Draw(LRedimage)
    
#    drawblack.text((2, 0), 'hello world', font = font18, fill = 0)
#    drawblack.text((2, 20), '2.9inch epd', font = font18, fill = 0)
#    drawblack.text((20, 50), u'微雪电子', font = font18, fill = 0)
#    drawblack.line((10, 90, 60, 140), fill = 0)
#    drawblack.line((60, 90, 10, 140), fill = 0)
#    drawblack.rectangle((10, 90, 60, 140), outline = 0)
#    drawred.line((95, 90, 95, 140), fill = 0)
#    drawred.line((70, 115, 120, 115), fill = 0)
#    drawred.arc((70, 90, 120, 140), 0, 360, fill = 0)
#    drawred.rectangle((10, 150, 60, 200), fill = 0)
#    drawred.chord((70, 150, 120, 200), 0, 360, fill = 0)
#    epd.display(epd.getbuffer(LBlackimage), epd.getbuffer(LRedimage))
#    time.sleep(2)
    
#    logging.info("3.read bmp file")
#    blackimage1 = Image.new('1', (epd.height, epd.width), 255)  # 298*126
#    redimage1 = Image.new('1', (epd.height, epd.width), 255)  # 298*126 
#    newimage = Image.open(os.path.join(picdir, '2in7_Scale.bmp'))
#    blackimage1.paste(newimage, (0,0))    
#    epd.display(epd.getbuffer_4Gray(blackimage1), epd.getbuffer(redimage1))
    #epd.display_4Gray(epd.getbuffer_4Gray(blackimage1))
#    time.sleep(2)
    
#    logging.info("4.read bmp file on window")
#    blackimage1 = Image.new('1', (epd.height, epd.width), 255)  # 298*126
#    redimage1 = Image.new('1', (epd.height, epd.width), 255)  # 298*126    
#    newimage = Image.open(os.path.join(picdir, '100x100.bmp'))
#    blackimage1.paste(newimage, (50,10))    
#    epd.display(epd.getbuffer(blackimage1), epd.getbuffer(redimage1))
    
#    logging.info("Clear...")
#    epd.init()
#    epd.Clear()
    
    logging.info("Goto Sleep...")
    epd.sleep()
        
except IOError as e:
    logging.info(e)
    
except KeyboardInterrupt:    
    logging.info("ctrl + c:")
    epd2in7b.epdconfig.module_exit()
    exit()
