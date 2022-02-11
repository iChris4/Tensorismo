TensorKart
==========

self-driving Mario Kart 8 Deluxe with TensorFlow


Dependencies
------------
* `python` and `pip` then run `pip install -r requirements.txt`
* `yuzu`


Recording Samples
-----------------
1. Start your emulator program (`yuzu`) and run Mario Kart 8 Deluxe
2. Make sure you have a joystick connected
3. Run `record.py`
4. Make sure the graph responds to joystick input.
5. Position the emulator window so that the image is captured by the program (top left corner)
6. Press record and play through a level. You can trim some images off the front and back of the data you collect afterwards (by removing lines in `data.csv`).


Notes
- the GUI will stop updating while recording to avoid any slow downs.
- double check the samples, sometimes the screenshot is the desktop instead. Remove the appropriate lines from the `data.csv` file


Viewing Samples
---------------
Run `python utils.py viewer samples/your_sample` to view the samples


Preparing Training Data
-----------------------
Run `python utils.py prepare samples/*` with an array of sample directories to build an `X` and `y` matrix for training. (zsh will expand samples/* to all the directories. Passing a glob directly also works)

`X` is a 3-Dimensional array of images

`y` is the expected joystick ouput as an array:

```
  [0] joystick x axis
```


Training
--------
The `train.py` program will train a model using Google's TensorFlow framework and cuDNN for GPU acceleration. Training can take a while (~1 hour) depending on how much data you are training with and your system specs. The program will save the model to disk when it is done.


Play
----
The `play.py` program will use `vjoy` to control the game on yuzu. The programm will provide the screenshots of the emulator. These images will be sent to the model to acquire the joystick command to send. The AI joystick commands can be overridden by holding the 'LB' button on the controller.


Special Thanks To
-----------------
* https://github.com/SullyChen/Autopilot-TensorFlow
