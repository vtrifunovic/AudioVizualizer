import argparse
import sys
import threading
from aubio import source, pitch, onset
import sounddevice as sd
import effects
import cv2
import numpy as np
import time

def int_or_str(text):
    try:
        return int(text)
    except ValueError:
        return text
        

def create_sound():
	global img
	global i
	win_s = 4096
	hop_s = 384 # hop_s will need to change depending on the system
	samplerate = 0
	out = cv2.VideoWriter('six.avi',cv2.VideoWriter_fourcc('M','J','P','G'), 56, (1920,1080))
	img = cv2.imread('anime.jpg')
	dim = img.shape
	print(dim)
	kv = effects.k9effects(img)
	i = 0
	samplerate = int(sd.query_devices(args.device, 'output')['default_samplerate'])
    	# windows can only do wavs for now
	s = source("./songs/six.mp3", samplerate, hop_s)
	samplerate = s.samplerate
	tolerance = 0.74 # 0.74 is best on average, but more intense songs might be better at higher numbers
	pitch_o = pitch("default", win_s, hop_s, samplerate) # setting a pitch detector
	pitch_x = onset("default", win_s, hop_s, samplerate) # setting a onset detector
	pitch_y = pitch("mcomb", win_s, hop_s, samplerate)
	pitch_o.set_tolerance(tolerance)
	pitch_y.set_tolerance(tolerance)
	
	global pastpitch
	pastpitch = 0
	
	# change to will, this will determine how often the "flashy" effects will occur. Shorter queue = more frequent flashes
	queue = ['x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x']
	
	# this is the function which plays and analyzes the audio
	def callback(outdata, frames, time, status):
		if status:
			print(status, file=sys.stderr)
		
		# still working on reducing the globals
		global start_idx
		global pastpitch
		global img
		global i
		global pasteffect
		# here we detect  the pitch and onset
		samples, read = s()
		pitch = pitch_o(samples)[0] # use o for most artists
		onset = pitch_x(samples)[0]
		pitch2 = pitch_y(samples)[0] # use y for Flare
		# testing various parameters to determine which efect is best to be applied
		if pitch == 0 and pastpitch != 0 and pasteffect != 'Glow':
			if 'Treble' in queue or 'Glow' in queue:
				effect = 'SubBass'
				queue.append('SubBass')
			else:
				effect = 'Treble'
				queue.append(str(effect))
		elif pitch < 70 and pitch > 30 and pitch is not pastpitch:
			# remove this part for songs that aren't Flare's
			if queue.count('MidBass') <= 2 and pasteffect == 'MidBass':
				effect = 'Treble'
				queue.append(str(effect))
			else:
				############################################
				effect = 'SubBass'
				queue.append(str(effect))
		elif pitch > 70 and pitch < 80 or pitch == 280:
			effect = "ScratchyBass"
			queue.append(str(effect))
		elif pitch < 120 and pitch > 87:
			effect = 'MidBass'
			queue.append(str(effect))
		elif pitch > 8000 and pitch is not pastpitch and pasteffect != 'Treble':
			if 'Treble' in queue or 'Glow' in queue:
				effect = ''
				queue.append('x')
			else:
				effect = 'Treble'
				queue.append(str(effect))
		elif onset != 0 and pasteffect != 'Treble' and pasteffect != 'Glow':
			if 'Glow' in queue or 'Treble' in queue:
				effect = ''
				queue.append('x')
			else:
				effect = 'Real'
				queue.append(str(effect))
		else:
			effect = ''
			queue.append(str(effect))
		# print data, this can be supressed since it's really only for de-bugging
		#print(int(pitch), effect, onset, int(pitch2))
		# re-shaping and passing audio data to the speakers
		outdata.shape = samples.shape
		outdata[:] = 0
		start_idx += read
		# if no more audio data to read, set effect as 'End' and kill current thread
		if read == 0:
			effect = 'End'
			print(queue)
			raise sd.CallbackStop
			return
		if kv.check_black(img) == True:
			img = cv2.imread('anime.jpg')
		i+=1
		img = kv.split_color(img) # split color for every frame
		if i%2==0: # every other frame is either hue-shifted and dilated or eroded
			img[0:1080,950:970] = cv2.dilate(img[0:1080,950:970], (8,12))
			#img = cv2.dilate(img, (4,6))
			img = kv.shift_hue(img)
		else:
			img = cv2.erode(img, (9,1))
		
		if effect == 'Treble':
			img = kv.add_treble(img, dim)
			
		elif effect == 'SubBass':
			img = kv.add_subbass(img)
			
		elif effect == 'ScratchyBass':
			img = kv.add_scratchybass(img)
			
		elif effect == 'MidBass':
			img = kv.add_midbass(img)
		
		elif effect == 'Real':
			img = kv.add_real(img)
		
		elif effect == 'Glow':
			img = kv.add_glow(img)
		
		# Not an effect, done to synchronize thread killing
		elif effect == 'End':
			cv2.destroyAllWindows()
		out.write(img)
		pastpitch = pitch
		pasteffect = effect
		queue.pop(0) # removing most recent effect from the queue, so that it stays the same length

	# running the output stream to play audio
	with sd.OutputStream(device=args.device, channels=1, callback=callback, samplerate=samplerate):
		input()
	return

if __name__ == "__main__":
	global pasteffect
	pasteffect = ''
	start_idx = 0
	parser = argparse.ArgumentParser(add_help=False)
	parser.add_argument('-l', '--list-devices', action='store_true', help='show list of audio devices and exit')
	args, remaining = parser.parse_known_args()
	if args.list_devices:
		print(sd.query_devices())
		parser.exit(0)
	parser.add_argument('-d', '--device', type=int_or_str, help='output device (numeric ID or substring)')
	args = parser.parse_args(remaining)
	create_sound()
    
