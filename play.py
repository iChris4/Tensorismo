#!/usr/bin/env python

from utils import resize_image, XboxController, Screenshot
from termcolor import cprint
import mss
import cv2
import pyvjoy
import time
from matplotlib import pyplot as plt
from datetime import datetime
from PIL import Image

from train import create_model
import numpy as np

# Play
class Actor(object):

    def __init__(self):
        # Load in model from train.py and load in the trained weights
        self.model = create_model(keep_prob=1) # no dropout
        self.model.load_weights('model_weights.h5')

        # Init contoller for manual override
        self.real_controller = XboxController()

    def get_action(self, obs):

        ### determine manual override
        manual_override = self.real_controller.LeftBumper == 1

        if not manual_override:
            ## Look
            vec = resize_image(obs)
            vec = np.expand_dims(vec, axis=0) # expand dimensions for predict, it wants (1,66,200,3) not (66, 200, 3)
            ## Think
            joystick = self.model.predict(vec, batch_size=1)[0]

        else:
            joystick = self.real_controller.read()
            joystick[1] *= -1 # flip y (this is in the config when it runs normally)


        ## Act

        ### calibration
        output = [
            float(joystick[0]),
            0,
            1,
            0,
            0,
        ]

        ### print to console
        if manual_override:
            cprint("Manual: " + str(output), 'yellow')
        else:
            cprint("AI: " + str(output), 'green')

        return output

def get_screenshot():
        # Get raw pixels from the screen
        sct = mss.mss()
        sct_img = sct.grab({"top": Screenshot.OFFSET_Y,
                            "left": Screenshot.OFFSET_X,
                            "width": Screenshot.SRC_W,
                            "height": Screenshot.SRC_H})

        # Create the Image
        img = np.array(sct_img)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        return img

def play(action, vjoy, old_time):
    x_value = int(16384 * action[0] + 16384)
    y_value = int(16384 * action[1] + 16384)
    vjoy.data.wAxisX = int(hex(x_value), 16)
    vjoy.data.wAxisY = int(hex(y_value), 16)

    now = int(round(time.time() * 1000))
    if now - old_time > 200 :
        #vjoy.data.lButtons = 1 - vjoy.data.lButtons
        vjoy.data.lButtons = 1
        vjoy.update()
        return now
    vjoy.update()
    return old_time

if __name__ == '__main__':

    actor = Actor()
    old_time = int(round(time.time() * 1000))
    vjoy = pyvjoy.VJoyDevice(1)
    vjoy.data.wAxisX = 0x4000
    vjoy.data.wAxisY= 0x4000
    vjoy.data.lButtons = 0
    vjoy.update()
    print('actor ready!')

    print('beginning loop')

    while True:
        screenshot = get_screenshot()
        action = actor.get_action(screenshot)
        old_time = play(action, vjoy, old_time)

    input('press <ENTER> to quit')

