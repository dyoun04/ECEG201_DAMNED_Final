import espFunctions as espFun
import neoPixelFunctions as neoFun
import motorFunctions as motorFun
import json
import board
from adafruit_seesaw import seesaw, rotaryio, digitalio
import adafruit_character_lcd.character_lcd_i2c as character_lcd
import time
import random


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

def Flash(flashvalue, color_index):
        color_list = [[0,191,255,24,18], [0,200,0,5,0], [255,0,0,11,6], [255,255,0,17,12]]
        if flashvalue:
            neoFun.bar_graph((0,0,0), color_list[color_index][3], True, color_list[color_index][4])
        else:
            neoFun.bar_graph(tuple(color_list[color_index][0:3]), color_list[color_index][3], True, color_list[color_index][4])


def Flash_3(color_index):
        color_list = [[0,191,255,24,18], [0,200,0,5,0], [255,0,0,11,6], [255,255,0,17,12]]
        for i in range(1):
            time.sleep(.25)
            neoFun.bar_graph(tuple(color_list[color_index][0:3]), color_list[color_index][3], True, color_list[color_index][4])
            time.sleep(.25)
            neoFun.bar_graph((0,0,0), color_list[color_index][3], True, color_list[color_index][4])

def next_color():
    return random.randint(0,3)

def update_scores():
    scores = json.loads(net_tool.api_get(hostServer + scorePath))
    lcd.message = f'Player 1: {str(scores["1"])}\nPlayer 2: {str(scores["2"])}'

def match_sequence(color_sequence):
    color_select = 0
    success = True
    position = -encoder.position
    button_state = button.value
    button_prev = button_state
    prev_position = position
    prev_time = time.monotonic()
    flash_on = False

    for color in color_sequence:
        if not success:
            break
        while(success):
            position = -encoder.position
            if position != prev_position:
                if (prev_position > position): ## if counterclockwise
                    GenerateColors()
                    color_select -= 1
                    color_select %= 4
                else:
                    GenerateColors()
                    color_select += 1
                    color_select %= 4
                prev_position = position
                prev_time = time.monotonic() - 0.25
                flash_on = False

            if time.monotonic() - prev_time > .25: #in terms of milseconds
                prev_time = time.monotonic()
                flash_on = not flash_on
                Flash(flash_on,color_select)

            button_state = button.value
            if not button_state and button_prev:
                if color_select != eval(color):
                    success = False
                else:
                    button_prev = button_state
                    break
            button_prev = button_state
    return success

hostServer = 'http://134.82.159.191:8000'
joinPath = '/join'
startPath = '/start'
scorePath = '/scores'

################################################################# Startup Code for Rotary Encoder ##############################################################
I2C = board.I2C()
seesaw = seesaw.Seesaw(I2C, addr=0x36)
seesaw.pin_mode(24, seesaw.INPUT_PULLUP)
button = digitalio.DigitalIO(seesaw,24)
encoder = rotaryio.IncrementalEncoder(seesaw)

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
#motor_tool.find_home()

################################################################# Main Loop #################################################################

color_index = 0
color_sequence = ''

lcd.backlight = True
lcd.message = 'Connecting...'
net_tool = espFun.ESP_Tools(NETWORK_NAME, NETWORK_PASS)
lcd.clear()
lcd.message = 'Connected to\nnetwork!'

playerID = 0
gameID = 0
scores = {'1' : 0, '2' : 0}

txt = net_tool.api_get(hostServer + joinPath)
playerID = txt[-2:-1]
lcd.clear()
lcd.message = txt

# If player 1, wait for player 2. Otherwise, start game
if(playerID == '1'):
    lcd.clear()
    lcd.message = 'Waiting for\nPlayer 2...'

    while(True):
        #time.sleep(3)
        gameID = json.loads(net_tool.api_get(hostServer + startPath))['id']
        if(gameID != 0):
            break
else:
    net_tool.api_post(hostServer + startPath, data='start')
    gameID = json.loads(net_tool.api_get(hostServer + startPath))['id']
random.seed(gameID)

lcd.clear()
lcd.message = f'Player 1: {str(scores["1"])}\nPlayer 2: {str(scores["2"])}'

while(True):

    neoFun.set_ring_color((0,0,0))
    time.sleep(0.5)
    color_sequence += str(next_color())
    for color in color_sequence:
        Flash_3(eval(color))
    time.sleep(0.5)
    GenerateColors()

    update_scores()
    if match_sequence(color_sequence):
        scores[playerID] += 1
    else:
        neoFun.set_ring_color((255,0,0))
        prev_time_scores = time.monotonic()
        while(True):
            if time.monotonic() - prev_time_scores > 1:
                update_scores()
                prev_time_scores = time.monotonic()

    net_tool.api_post(hostServer + scorePath, data=str(str(playerID) + ' ' + str(scores[playerID])))
    update_scores()
