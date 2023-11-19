#!/usr/bin/env python

import numpy as np
import os
import shutil
import mss
import matplotlib
matplotlib.use('TkAgg')
from datetime import datetime
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg as FigCanvas
import random

import pygetwindow as gw
import pyautogui

from PIL import ImageTk, Image

import sys

PY3_OR_LATER = sys.version_info[0] >= 3

if PY3_OR_LATER:
    # Python 3 specific definitions
    import tkinter as tk
    import tkinter.ttk as ttk
    import tkinter.messagebox as tkMessageBox
else:
    # Python 2 specific definitions
    import Tkinter as tk
    import ttk
    import tkMessageBox

from utils import Screenshot, XboxController

IMAGE_SIZE = (640, 360)
IDLE_SAMPLE_RATE = 30
SAMPLE_RATE = 30

class MainWindow():
    """ Main frame of the application
    """

    def __init__(self):
        self.root = tk.Tk()
        self.sct = mss.mss()

        self.root.title('Data Acquisition')
        self.root.geometry("800x720")
        self.root.resizable(False, False)

        # Init controller
        self.controller = XboxController()

         # Create GUI
        self.create_main_panel()

        # Timer
        self.rate = IDLE_SAMPLE_RATE
        self.sample_rate = SAMPLE_RATE
        self.idle_rate = IDLE_SAMPLE_RATE
        self.recording = False
        self.t = 0
        self.pause_timer = False
        self.on_timer()

        self.root.mainloop()

    def create_main_panel(self):
        # Panels
        top_half = tk.Frame(self.root)
        top_half.pack(side=tk.TOP, expand=True, padx=5, pady=5)
        message.pack(side=tk.TOP, padx=5)
        bottom_half = tk.Frame(self.root)
        bottom_half.pack(side=tk.LEFT, padx=5, pady=10)

        # Images
        self.img_panel = tk.Label(top_half, image=ImageTk.PhotoImage("RGB", size=IMAGE_SIZE)) # Placeholder
        self.img_panel.pack(side = tk.LEFT, expand=False, padx=5)

        # Joystick
        self.init_plot()
        self.PlotCanvas = FigCanvas(figure=self.fig, master=top_half)
        self.PlotCanvas.get_tk_widget().pack(side=tk.RIGHT, expand=False, padx=5)

        # Recording
        textframe = tk.Frame(bottom_half, width=332, height=15, padx=5)
        textframe.pack(side=tk.LEFT)
        textframe.pack_propagate(0)
        self.outputDirStrVar = tk.StringVar()
        self.txt_outputDir = tk.Entry(textframe, textvariable=self.outputDirStrVar, width=100)
        self.txt_outputDir.pack(side=tk.LEFT)
        self.outputDirStrVar.set("samples/" + datetime.now().strftime('%Y-%m-%d_%H_%M_%S'))

        self.record_button = ttk.Button(bottom_half, text="Record", command=self.on_btn_record)
        self.record_button.pack(side = tk.LEFT, padx=5)


    def init_plot(self):
        self.plotMem = 50 # how much data to keep on the plot
        self.plotData = [[0] * (5)] * self.plotMem # mem storage for plot

        self.fig = Figure(figsize=(4,3), dpi=80) # 320,240
        self.axes = self.fig.add_subplot(111)


    def on_timer(self):
        self.poll()

        # stop drawing if recording to avoid slow downs
#        if self.recording == False:
        self.draw()

        if not self.pause_timer:
            self.root.after(self.rate, self.on_timer)


    def poll(self):
        self.img = self.take_screenshot()
        self.controller_data = self.controller.read()
        self.update_plot()

        if self.recording == True:
            # save only X% of driving straigth to reduce bias
            if self.controller_data[0] == 0 :
                if random.random() < 2 :
                    self.save_data()
                    self.t += 1
            else :
                self.save_data()
                self.t += 1




    def take_screenshot(self):
        try:
            # Find the window by title
            window = gw.getWindowsWithTitle('Chiaki | Stream')[0]
            if window:
                # Bring the window to the front
                window.activate()

                # Use pyautogui to capture the specific window
                x, y, width, height = window.left, window.top, window.width, window.height
                screenshot = pyautogui.screenshot(region=(x + 8, y + 20, width - 16, height - 40))
                return Image.fromarray(np.array(screenshot))
            else:
                raise Exception("Window not found")
        except Exception as e:
            print("Error capturing screenshot:", e)
            return None



    def update_plot(self):
        self.plotData.append(self.controller_data) # adds to the end of the list
        self.plotData.pop(0) # remove the first item in the list, ie the oldest


    def save_data(self):
        image_file = self.outputDir+'/'+'img_'+str(self.t)+'.png'
        self.img.save(image_file)

        # write csv line
        self.outfile.write( image_file + ',' + ','.join(map(str, self.controller_data)) + '\n' )


    def draw(self):
        # Image
        self.img.thumbnail(IMAGE_SIZE) # Resize
        self.img_panel.img = ImageTk.PhotoImage(self.img)
        self.img_panel['image'] = self.img_panel.img

        # Joystick
        x = np.asarray(self.plotData)
        self.axes.clear()
        self.axes.plot(range(0,self.plotMem), x[:,0], 'r')
        self.axes.plot(range(0,self.plotMem), x[:,1], 'b')
        self.axes.plot(range(0,self.plotMem), x[:,2], 'g')
        self.axes.plot(range(0,self.plotMem), x[:,3], 'k')
        self.axes.plot(range(0,self.plotMem), x[:,4], 'y')
        self.PlotCanvas.draw()


    def on_btn_record(self):
        # pause timer
        self.pause_timer = True

        if self.recording:
            self.recording = False
        else:
            self.start_recording()

        if self.recording:
            self.t = 0 # Reset our counter for the new recording
            self.record_button["text"] = "Stop"
            self.rate = self.sample_rate
            # make / open outfile
            self.outfile = open(self.outputDir+'/'+'data.csv', 'a')
        else:
            self.record_button["text"] = "Record"
            self.rate = self.idle_rate
            self.outfile.close()

        # un pause timer
        self.pause_timer = False
        self.on_timer()


    def start_recording(self):
        should_record = True

        # check that a dir has been specified
        if not self.outputDirStrVar.get():
            tkMessageBox.showerror(title='Error', message='Specify the Output Directory', parent=self.root)
            should_record = False

        else: # a directory was specified
            self.outputDir = self.outputDirStrVar.get()

            # check if path exists - i.e. may be saving over data
            if os.path.exists(self.outputDir):

                # overwrite the data, yes/no?
                if tkMessageBox.askyesno(title='Warning!', message='Output Directory Exists - Overwrite Data?', parent=self.root):
                    # delete & re-make the dir:
                    shutil.rmtree(self.outputDir)
                    os.mkdir(self.outputDir)

                # answer was 'no', so do not overwrite the data
                else:
                    should_record = False
                    self.txt_outputDir.focus_set()

            # directory doesn't exist, so make one
            else:
                os.mkdir(self.outputDir)

        self.recording = should_record


if __name__ == '__main__':
    app = MainWindow()
