'''
Author: James Howe
Author 2022:  Matt Lamparter

A basic class which keeps track of the current location of the stepper motor and
allows one to either set it's poistion or move it

I use CW for clockwise and CCW for counter clockwise

This library is based on the Adafruit product 2927:
https://www.adafruit.com/product/2927
which in turn relies on the PC9685 and TB6612 devices
We use "stepper 1" on the Adafruit board on the custom DAMNED PCB

////////////////////////// from James//////////////////
not using `style = stepper.DOUBLE` for the movement results in inaccuracies

some examples are at the end

CircuitPython motor functions references:
https://github.com/adafruit/Adafruit_CircuitPython_Motor/blob/main/adafruit_motor/stepper.py
https://github.com/adafruit/Adafruit_CircuitPython_MotorKit/blob/c6118a65b68f00256bb88168de38179e6dd20721/adafruit_motorkit.py#L51
https://github.com/adafruit/Adafruit_CircuitPython_MotorKit/blob/c6118a65b68f00256bb88168de38179e6dd20721/examples/motorkit_stepper_test.py


'''
import board
import time
from adafruit_motorkit import MotorKit
from adafruit_motor import stepper


class ECEGMotor():
    '''
    A basic class which keeps track of the current stepper motor position
    and allows the user to move it
    '''
    #STEPS_FOR_FULL = 48 #The number of steps for full rotation of the stepper with the magnet on the rotor
    STEPS_FOR_FULL = 32*16*4 #The number of steps for a full rotation for a 1/64 reduction motor
    '''
    Adafruit page https://www.adafruit.com/product/858
    "Small Reduction Stepper Motor - 5VDC 32-Step 1/16 Gearing"
    Motor printed part number on back:  28BYJ-48 5v DC
    Adafruit lists this stepper as having 32 steps and a 1/16.128 reduction
    for a total step count of 32 * 16.128 = 516
    BUT - they got a batch in at one point (January 2021) with a reduction of 64 which means step
    count in that case would be 32 * 64 = 2048
    '''


    def __init__(self, debug):
        """
        The intilizer for the method

        """
        self.__debug = debug
        self.__kit = MotorKit(i2c=board.I2C())
        self.__stepper = self.__kit.stepper1
        self.__stepper.release()
        self.__current_step = 0 #the current number of steps CW from home(step 0)
        self.__motor_state = True
        print("INITIALIZATION COMPLETE")


    def find_home(self):
        """
        A method for finding the peg on the device, just moves it CCW 1 full rotation
        """
        if self.__debug:
            print("Finding the home of the stepper motor")
        for i in range((ECEGMotor.STEPS_FOR_FULL)):
           self.__stepper.onestep(direction = stepper.BACKWARD, style = stepper.DOUBLE)
           time.sleep(0.001)
        if self.__debug:
            self.__current_step = 0 # reset the step counter to 0 once home is found
        print("Home found\n")

    def get_current_step(self):
        """
        A getter method that returns the current number of steps CW from home(step 0)

        Returns: int, current number of steps CW
        range of returned values is 0 to STEPS_FOR_FULL in increments of 1
        """
        return self.__current_step

    def get_stepper(self):
        """
        A getter method for the stepper

        Returns: MotorKit.stepper1()
        """
        return self.__stepper

    def get_current_degree(self):
        """
        A method which calculates and returns the position of the arm as the number of degrees from home

        Returns: float
        """
        return (float(self.__current_step) / float(ECEGMotor.STEPS_FOR_FULL)) * 360.0

    def set_position_degrees_monotonic(self, pos):
        """
        Takes in the position in degrees from home (absolute) and then moves the arm to that location

        Params: The position in degrees that you want the arm to go to, could be int or float will do nothing if its not 0-360
        """

        if(pos < 0 or pos > 360):
            print("Input not between 0 and 360, the motor will not be moved")
            return

        goal_pos_in_steps = int(((pos/360) * ECEGMotor.STEPS_FOR_FULL))

        steps_to_take =  goal_pos_in_steps - self.__current_step

        # for i in range(abs(steps_to_take)):
        # if self.__motor_state == True:

        #Move the arm CCW
        if(steps_to_take < 0):
            self.__stepper.onestep(direction = stepper.BACKWARD, style = stepper.DOUBLE)
            self.__current_step -= 1
            # time.sleep(.001)

        #Move the arm CW
        else:
            self.__stepper.onestep(style = stepper.DOUBLE)
            self.__current_step += 1
            # time.sleep(.001)

    def set_position_degrees(self, pos):
        """
        Takes in the position in degrees from home (absolute) and then moves the arm to that location

        Params: The position in degrees that you want the arm to go to, could be int or float will do nothing if its not 0-360
        """

        if(pos < 0 or pos > 360):
            print("Input not between 0 and 360, the motor will not be moved")
            return

        goal_pos_in_steps = int(((pos/360) * ECEGMotor.STEPS_FOR_FULL))

        steps_to_take =  goal_pos_in_steps - self.__current_step

        for i in range(abs(steps_to_take)):

            #Move the arm CCW
            if(steps_to_take < 0):
                self.__stepper.onestep(direction = stepper.BACKWARD, style = stepper.DOUBLE)
                self.__current_step -= 1
                time.sleep(0.001)

            #Move the arm CW
            else:
                self.__stepper.onestep(style = stepper.DOUBLE)
                self.__current_step += 1
                time.sleep(0.001)

    def set_position_steps(self, pos):
        """
        Takes in the position in steps from home (step 0) and then moves the arm to that location (absolute)

        Params: The position in steps that you want the arm to go to, should be int. It will do nothing if its not between 0 and STEPS_FOR_FULL
        """

        if(pos < 0 or pos > ECEGMotor.STEPS_FOR_FULL):
            print("Input not between 0 and", ECEGMotor.STEPS_FOR_FULL, "the motor will not be moved")
            return
        #convert any floats to ints
        pos = int(pos)
        steps_to_take =  pos - self.__current_step

        for i in range(abs(steps_to_take)):

            #Move the arm CCW
            if(steps_to_take < 0):
                self.__stepper.onestep(direction = stepper.BACKWARD, style = stepper.DOUBLE)
                self.__current_step -= 1
                time.sleep(0.001)

            #Move the arm CW
            else:
                self.__stepper.onestep(style = stepper.DOUBLE)
                self.__current_step += 1
                time.sleep(0.001)

    def reset_position(self):
        """
        Resets the position of the arm to home
        """

        for i in range(self.__current_step):
            self.__stepper.onestep(direction = stepper.BACKWARD, style = stepper.DOUBLE)
            time.sleep(0.001)
        self.__current_step = 0


    def move_arm_steps(self, amount):
        """
        Moves the arm amount steps, if amount is negative then the arm is moved CCW and if its positive it moves CW
        This is a relative movement from the current position of the arm
        """
        amount = int(amount)
        if (abs(amount) > ECEGMotor.STEPS_FOR_FULL):
            print("Input beyond limits of max motor steps: ", ECEGMotor.STEPS_FOR_FULL,". The motor will not move.")
            return

        for i in range(abs(amount)):

            if(amount < 0):
                if(self.__current_step == 0):
                    print("Motor already at home, ie current_step = 0")
                    return

                self.__stepper.onestep(direction = stepper.BACKWARD,style = stepper.DOUBLE)
                self.__current_step -= 1
                time.sleep(0.001)

            else:
                if(self.__current_step == ECEGMotor.STEPS_FOR_FULL):
                    print("Motor already at max steps, ie current_step = ", ECEGMotor.STEPS_FOR_FULL)
                    return

                self.__stepper.onestep(style = stepper.DOUBLE)
                self.__current_step += 1
                time.sleep(0.001)


    def move_arm_degrees(self, degrees):
        """
        Moves the arm an absolute number of degrees from current position
        degrees must be between -360 and 360
        If degrees is negative then the arm is moved CCW and if its positive it moves CW
        function checks to see if requested movement would take the arm out of the absolute range (0,360)
        If requested movement would fall outside of that range then the arm stops at 0 or 360 degrees
        current_step is updated accordingly
        """

        if(abs(degrees) > 360):
            print("Input not between -360 and 360, the motor will not be moved")
            return
        # determine the number of corresponding motor steps required to move the requested degrees
        # steps need to be integer values
        requested_steps = int(((degrees/360) * ECEGMotor.STEPS_FOR_FULL))

        for i in range(abs(requested_steps)):

            if(requested_steps < 0):
                if(self.__current_step == 0):
                    print("Motor already at home, ie current_step = 0")
                    return

                self.__stepper.onestep(direction = stepper.BACKWARD,style = stepper.DOUBLE)
                self.__current_step -= 1
                time.sleep(0.001)

            else:
                if(self.__current_step == ECEGMotor.STEPS_FOR_FULL):
                    print("Motor already at max steps, ie current_step = ", ECEGMotor.STEPS_FOR_FULL)
                    return

                self.__stepper.onestep(style = stepper.DOUBLE)
                self.__current_step += 1
                # time.sleep(0.001)



##EXAMPLES
'''
print("starting")
myMotor = ECEGMotor()



myMotor.set_position_degrees(90)
print(myMotor.get_current_degree())
myMotor.reset_position()

myMotor.set_position_degrees(180)
print(myMotor.get_current_degree())
myMotor.reset_position()
myMotor.set_position_degrees(340)
print(myMotor.get_current_degree())
myMotor.reset_position()
myMotor.stepper.release()

'''
