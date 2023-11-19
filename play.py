#!/usr/bin/env python

from utils import resize_image, XboxController, Screenshot
from termcolor import cprint
import mss
import cv2
import vgamepad as vg
import time
from datetime import datetime
from PIL import Image

import pygetwindow as gw
import pyautogui

from train import create_model
import numpy as np

# Play
class Actor(object):
    def __init__(self):
        # Load in model from train.py and load in the trained weights
        self.model = create_model(keep_prob=1) # no dropout
        self.model.load_weights('model_weights.h5')

        # Init controller for manual override
        self.real_controller = XboxController()

    def get_action(self, obs):
        ### determine manual override
        manual_override = self.real_controller.LeftBumper == 1

        if not manual_override:
            ## Look
            vec = resize_image(obs)
            vec = np.expand_dims(vec, axis=0) # expand dimensions for predict
            ## Think
            joystick = self.model.predict(vec, batch_size=1)[0]
        else:
            joystick = self.real_controller.read()
            joystick[1] *= -1 # flip y

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
    # Find the window by its name
    window = gw.getWindowsWithTitle('Chiaki | Stream')[0]  # Adjust the title if necessary

    if window is not None:
        # Get the window's position and size
        x, y, width, height = window.left, window.top, window.width, window.height

        # Adjust for window borders if necessary
        border_thickness = 8  # This is a typical value, but it might vary
        title_bar_height = 30  # This also varies

        with mss.mss() as sct:
            # Define the region to capture
            monitor = {"top": y + title_bar_height, "left": x + border_thickness, 
                       "width": width - 2 * border_thickness, 
                       "height": height - title_bar_height - border_thickness}

            # Capture the image
            sct_img = sct.grab(monitor)

            # Convert to an array
            img = np.array(sct_img)
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)  # Adjust color format if necessary

            # Display the image
            #cv2.imshow('Screenshot', img)
            #cv2.waitKey(1)  # Waits for a key press for 1 millisecond

            return img
    else:
        print("Window not found")
        return None


def play(action, gamepad, old_time):
    x_value = int(32767 * action[0])
    y_value = int(32767 * action[1])

    # Updating the gamepad values using the correct vgamepad methods
    gamepad.left_joystick_float(x_value_float=x_value/32767.0, y_value_float=0)

    now = int(round(time.time() * 1000))
    if now - old_time > 200:
     # gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
        gamepad.right_trigger_float(value_float=1.0)
        gamepad.update()
#        time.sleep(0.1)
#        gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
        return now
    gamepad.update()
    return old_time

if __name__ == '__main__':
    actor = Actor()
    old_time = int(round(time.time() * 1000))
    gamepad = vg.VX360Gamepad()

    print('actor ready!')
    print('beginning loop')

    while True:
        screenshot = get_screenshot()
        action = actor.get_action(screenshot)
        old_time = play(action, gamepad, old_time)

    input('press <ENTER> to quit')
