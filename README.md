Tensorismo
==========

Self-driving for Gran Turismo 7 with TensorFlow

I'm not responsable for any action that could be taken by Sony or Polyphony Digital if you use this programm  


Dependencies
------------
* `python` and `pip` then run `pip install -r requirements.txt`
* `A Playstation 5 or 4`
* `GT7`
* `Chiaki : https://git.sr.ht/~thestr4ng3r/chiaki`


Recording Samples
-----------------
1. Start a remote play session and start a race
2. Make sure you have a joystick connected
3. Run `record_chiaki.py` or `record.py`
4. Make sure the graph responds to joystick input.
5. Make sure the image is captured by the program (top left corner for `record.py`)
6. Press record and play through the course. You can trim some images off the front and back of the data you collect afterwards (by removing lines in `samples/data.csv`).


Notes
- the GUI fot `record.py` will stop updating while recording to avoid any slow downs.
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

(Optional) Telemetry and Auto Restart
--------
Open and edit the `gt7telemetry` file to enter the ip to your console on the corresponding line

Launch `gt7telemetry` before `play.py` or the input of the IA will not be overide and the restart input sequence will fail

If a window appear with the current Speed and Lap, the programm is working correctly

Play
----
The `play.py` program will use `vgamepad` to control the game throught remote play. The programm will provide the screenshots of the emulator. These images will be sent to the model to acquire the joystick command to send.


Special Thanks To
-----------------
* https://github.com/SullyChen/Autopilot-TensorFlow
* https://github.com/Sblerky/TensorKart
* https://github.com/Bornhall/gt7telemetry
