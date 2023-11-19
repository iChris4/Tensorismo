import signal
from datetime import datetime as dt
from datetime import timedelta as td
import socket
import sys
import struct
from salsa20 import Salsa20_xor

import tkinter as tk
from threading import Thread

import time
import vgamepad as vg

# Initialize variables to track carSpeed zero duration
speed_zero_time = None
speed_zero_duration = 5  # 5 seconds

# Initialize global variables
carSpeed = 0
curlap = 0
prevlap = -1
pktid = 0
pknt = 0
gamepad = vg.VX360Gamepad()

# Playstation Console IP Adress (Can be found in Chiaki)
ip = "192.168.1.XX"

# Function to update the speed and lap in the GUI
def update_telemetry():
    speed_label.config(text=f"Speed: {carSpeed:.1f} kph")
    lap_label.config(text=f"Lap: {curlap}")
    # Schedule the next update
    telemetry_window.after(100, update_telemetry)

# Function to run the Tkinter event loop
def run_gui():
    global telemetry_window, speed_label, lap_label
    telemetry_window = tk.Tk()
    telemetry_window.title("Car Telemetry")

    # Speed label
    speed_label = tk.Label(telemetry_window, text="Speed: 0.0 kph", font=("Helvetica", 20))
    speed_label.pack()

    # Lap label
    lap_label = tk.Label(telemetry_window, text="Lap: 0", font=("Helvetica", 20))
    lap_label.pack()

    # Initial call to update telemetry
    telemetry_window.after(100, update_telemetry)
    telemetry_window.mainloop()

# Start the GUI in a separate thread
gui_thread = Thread(target=run_gui)
gui_thread.start()

# ansi prefix
pref = "\033["

# ports for send and receive data
SendPort = 33739
ReceivePort = 33740

# Create a UDP socket and bind it
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('0.0.0.0', ReceivePort))
s.settimeout(10)

# data stream decoding
def salsa20_dec(dat):
	KEY = b'Simulator Interface Packet GT7 ver 0.0'
	# Seed IV is always located here
	oiv = dat[0x40:0x44]
	iv1 = int.from_bytes(oiv, byteorder='little')
	# Notice DEADBEAF, not DEADBEEF
	iv2 = iv1 ^ 0xDEADBEAF
	IV = bytearray()
	IV.extend(iv2.to_bytes(4, 'little'))
	IV.extend(iv1.to_bytes(4, 'little'))
	ddata = Salsa20_xor(dat, bytes(IV), KEY[0:32])
	magic = int.from_bytes(ddata[0:4], byteorder='little')
	if magic != 0x47375330:
		return bytearray(b'')
	return ddata

# send heartbeat
def send_hb(s):
	send_data = 'A'
	s.sendto(send_data.encode('utf-8'), (ip, SendPort))
	#print('send heartbeat')

# Initializing the flags
carSpeedZeroAlreadyHandled = False
carFinalLapAlreadyHandled = False


# start by sending heartbeat
send_hb(s)

while True:
	
	try:
		data, address = s.recvfrom(4096)
		pknt = pknt + 1
		ddata = salsa20_dec(data)
		
		gamepad.right_trigger_float(value_float=1.0)
		gamepad.update()

		if len(ddata) > 0 and struct.unpack('i', ddata[0x70:0x70+4])[0] > pktid:
			pktid = struct.unpack('i', ddata[0x70:0x70+4])[0]

			carSpeed = 3.6 * struct.unpack('f', ddata[0x4C:0x4C+4])[0]
			# printAt('{:7.1f}'.format(carSpeed), 12, 47)	# speed kph
			curlap = struct.unpack('h', ddata[0x74:0x74+2])[0]

			# Failsafe in case the car get stuck in the PIT
			if carSpeed == 0 and not carSpeedZeroAlreadyHandled:
				print("Car is in PIT")
				gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER)
				gamepad.update()
				time.sleep(5)
				gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN)
				gamepad.update()
				time.sleep(0.1)
				gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN)
				gamepad.update()
				time.sleep(1)
				gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
				gamepad.update()
				time.sleep(0.1)
				gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
				gamepad.update()
				time.sleep(5)
				gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER)
				gamepad.update()
				carSpeedZeroAlreadyHandled = True  # Set the flag to True after handling

				# Reset the flag once carSpeed is no longer zero
			elif carSpeed != 0:
				carSpeedZeroAlreadyHandled = False
				

			# Select Retry after the end of the race (Change to the max lap + 1, exemple 30 laps = 31)
			if curlap == 31 and not carFinalLapAlreadyHandled:
				print("Race finish")
         		# Press 1 'A', wait 8 seconds
				time.sleep(8)
				gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER)
				gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
				gamepad.update()
				time.sleep(0.1)
				gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
				gamepad.update()
				# Press 2 'A', wait 5 seconds
				time.sleep(2)
				gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
				gamepad.update()
				time.sleep(0.1)
				gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
				gamepad.update()
				# Wait 1 seconds, press 3 'A', wait 5 seconds
				time.sleep(1)
				gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
				gamepad.update()
				time.sleep(0.1)
				gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
				gamepad.update()
				# Wait 1 seconds, press 4 'A', wait 5 seconds
				time.sleep(1)
				gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
				gamepad.update()
				time.sleep(0.1)
				gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
				gamepad.update()
				# Wait 1 seconds, press 5 'A', wait 5 seconds
				time.sleep(1)
				gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
				gamepad.update()
				time.sleep(0.1)
				gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
				gamepad.update()
				# Wait 2 seconds, press 6 'A', wait 5 seconds
				time.sleep(2)
				gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
				gamepad.update()
				time.sleep(0.1)
				gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
				gamepad.update()
				# Wait 1 seconds, press 7 'A', wait 5 seconds
				time.sleep(1)
				gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
				gamepad.update()
				time.sleep(0.1)
				gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
				gamepad.update()
				# Wait 5 seconds, press 'dpad right', wait 5 seconds
				time.sleep(5)
				gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT)
				gamepad.update()
				time.sleep(0.1)
				gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT)
				gamepad.update()
				# Wait 1 seconds, press 8 'A'
				time.sleep(1)
				gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
				gamepad.update()
				time.sleep(0.1)
				gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
				gamepad.update()
				# Wait 5 seconds, press 9'A'
				time.sleep(5)
				gamepad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
				gamepad.update()
				time.sleep(0.1)
				gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
				gamepad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER)
				gamepad.update()
				print("New Race Started")
				carFinalLapAlreadyHandled = True

			elif curlap != 31:
				carFinalLapAlreadyHandled = False



		if pknt > 100:
			send_hb(s)
			pknt = 0
	except Exception as e:
		printAt('Exception: {}'.format(e), 41, 1, reverse=1)
		send_hb(s)
		pknt = 0
		pass
