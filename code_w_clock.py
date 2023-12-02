import espFunctions as espFun
import neoPixelFunctions as neoFun
import motorFunctions as motorFun
import json
import board
from adafruit_seesaw import seesaw, rotaryio, digitalio
import adafruit_character_lcd.character_lcd_i2c as character_lcd
import time
# import asyncio

#Wifi and Thingspeak stuff
try:
    from secrets import secrets_Bucknell as secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise
NETWORK_NAME = secrets["ssid"]
NETWORK_PASS = secrets["password"]

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

hostServer = 'http://134.82.159.191:8000'
joinPath = '/join.json'
rotaryPath = '/rotary.json'
genPath = '/genPurpose.json'

################################################################# Startup Code for Rotary Encoder ##############################################################
I2C = board.I2C()
seesaw = seesaw.Seesaw(I2C, addr=0x36)
seesaw.pin_mode(24, seesaw.INPUT_PULLUP)
button = digitalio.DigitalIO(seesaw,24)
encoder = rotaryio.IncrementalEncoder(seesaw)

button_prev = button.value
button_state = button_prev

################################################################# Startup Code for Rotary Encoder ##############################################################
cols = 16
rows = 2
lcd = character_lcd.Character_LCD_I2C(I2C, cols, rows)

############################################################ Other Startup Code (Given from David Berry) ###########################################################

NEO_BRIGHTNESS = 0.3

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
starttime2 = 0
flash_on = False
color_list_value = None
prev_position = 0

lcd.backlight = True
lcd.message = 'Connecting...'
net_tool = espFun.ESP_Tools(NETWORK_NAME, NETWORK_PASS)
lcd.clear()
lcd.message = 'Connected to\nnetwork!'



# async def set_end_timer(motor_tool):
#     motor_tool.set_position_degrees(360)

#  asyncio.gather(set_end_timer(motor_tool))

while(True):

    light_time = time.monotonic()
    arm_time = time.monotonic()

    if sample_game_bool:
        for i in range(len(sample_game)):
            print(sample_game[i])
            Flash_3(color_list[sample_game[i]][0], color_list[sample_game[i]][1], color_list[sample_game[i]][2], color_list[sample_game[i]][3], color_list[sample_game[i]][4])
        sample_game_bool = False

    if sample_game_bool == False:

        button_state = button.value
        if button_prev == False and button_state == True and color_list_value != None:
            combination_list.append(idx)
            print(combination_list) ## will push this list to the LCD screen to make sure they have enough
            # net_tool.api_post(hostServer + genPath, data=str(combination_list))
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

        if light_time - starttime > .25 and color_list_value != None: #in terms of milseconds
            starttime = light_time
            flash_on = not flash_on
            Flash(flash_on,color_list_value[0], color_list_value[1], color_list_value[2], color_list_value[3], color_list_value[4])

        if arm_time - starttime2 > .001:
            starttime2 = arm_time
            motor_tool.set_position_degrees_monotonic(360)
            if motor_tool.__current_step == 2042:
                break
            print(motor_tool.__current_step)

