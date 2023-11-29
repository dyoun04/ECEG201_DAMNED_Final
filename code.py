"""
PINS IN USE
>NeoPixel
->board.D5
>Motor
->board.I2C
>ESP
->board.11-13

ECEG 201 DA 10
David Berry, Matt Lamparter
Updated 11/01/2022
Changed hour and minute positions to accomodate new NeoPixel ring orientation on PCB v 3.1
Updated 4/13/2023
Moved from worldtimeapi.org to timeapi.io after worldtimeapi was repeatedly down
Updated 8/29/2023
Moved from weather.gov to open-meteo.com for weather API due to hourly weather data (15 minute available)
"""

#Import Libraries
import espFunctions as espFun
import neoPixelFunctions as neoFun
import motorFunctions as motorFun

#Other imports that are needed
import rtc
import board
import time
import json
import math
from adafruit_seesaw import seesaw, rotaryio, digitalio
import json

################################################################# Constants and Wifi stuff ################################################################

#Wifi and Thingspeak stuff
try:
    from secrets import secrets_Bucknell as secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise
NETWORK_NAME = secrets["ssid"]
NETWORK_PASS = secrets["password"]

I2C = board.I2C()

net_tool = espFun.ESP_Tools(NETWORK_NAME, NETWORK_PASS)

# hostServer = 'http://134.82.159.191:8000'
# joinPath = '/join.json'

# txt = net_tool.api_get(hostServer + joinPath)

# print(txt)

#NeoPixel settings
NEO_BRIGHTNESS = 0.3

#Determines whether or not debug messages are printed out
DEBUG = False

################################################################# Helper Functions #########################################################

def GetPosition():
    return -encoder.position

def GenerateColors():
    neoFun.bar_graph((0,200,0), 5, True, 0) #green
    neoFun.bar_graph((255,0,0), 11, True, 6) #red
    neoFun.bar_graph((255,255,0), 17, True, 12) #yellow
    neoFun.bar_graph((0,191,255), 24, True, 18) #blue


def Flash(flashvalue, color1, color2, color3, end_pos, start_pos):
        if flashvalue:
            neoFun.bar_graph((0,0,0), end_pos, True, start_pos)
        else:
            neoFun.bar_graph((color1, color2,color3), end_pos, True, start_pos)


def Flash_3(color1, color2, color3, end_pos, start_pos):
        for i in range(3):
            neoFun.bar_graph((0,0,0), end_pos, True, start_pos)
            time.sleep(.1)
            neoFun.bar_graph((color1, color2,color3), end_pos, True, start_pos)
            time.sleep(.1)


################################################################# Startup Code for Rotary Encoder ##############################################################
seesaw = seesaw.Seesaw(I2C, addr=0x36)
seesaw_product = (seesaw.get_version() >> 16) & 0xFFFF
print("Found product {}".format(seesaw_product))
if seesaw_product != 4991:
    print("Wrong firmware loaded?  Expected 4991")

encoder = rotaryio.IncrementalEncoder(seesaw)
button = digitalio.DigitalIO(seesaw, 24)

button_prev = button.value
button_state = button_prev

############################################################ Other Startup Code (Given from David Berry) ###########################################################

#Sets the neopixel rings brightness
neoFun.set_brightness(NEO_BRIGHTNESS)

#sets up the starter colors
GenerateColors()

#'motor_tool' handles all the motor related functions
motor_tool = motorFun.ECEGMotor(I2C)

#Calling this will automaticly make the motor try and find its home(i.e. try to make a full rotation and end up hitting the stop peg)
motor_tool.find_home()

################################################################# Main Loop #################################################################

color_list = [[0,191,255,24,18], [0,200,0,5,0], [255,0,0,11,6], [255,255,0,17,12]] #
combination_list = []
sample_game_bool = True
sample_game = [0,1,2,3,0]
list_position = 0
starttime = 0
flash_on = False
color_list_value = None
prev_position = 0

while(True):

    if sample_game_bool:
        for i in range(len(sample_game)):
            # print(sample_game[i])
            Flash_3(color_list[sample_game[i]][0], color_list[sample_game[i]][1], color_list[sample_game[i]][2], color_list[sample_game[i]][3], color_list[sample_game[i]][4])
        sample_game_bool = False

    if sample_game_bool == False:

        button_state = button.value
        if button_prev == False and button_state == True and color_list_value != None:
            combination_list.append(idx)
            print(combination_list) ## will push this list to the LCD screen to make sure they have enough
            if len(combination_list) == 5:
                if combination_list == sample_game:
                    print("correct")
                else:
                    print("incorrect")
                combination_list = []
                GenerateColors()
                break
        button_prev = button_state


        position = -encoder.position
        if position != prev_position:
            if (prev_position > position): ## if counterclockwise
                list_position -= 1
                GenerateColors()
                idx = list_position % 4
                color_list_value = color_list[idx]
            else:
                list_position += 1
                GenerateColors()
                idx = list_position % 4
                color_list_value = color_list[idx]
            prev_position = position

        if time.monotonic() - starttime > .25 and color_list_value != None: #in terms of milseconds
            starttime = time.monotonic()
            flash_on = not flash_on
            Flash(flash_on,color_list_value[0], color_list_value[1], color_list_value[2], color_list_value[3], color_list_value[4])



##########################################
