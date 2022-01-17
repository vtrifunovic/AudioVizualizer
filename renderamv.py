import argparse
import sys
import threading
from aubio import source, pitch, onset
import sounddevice as sd
import effects
import cv2
import numpy as np
import time
import random
from os import listdir

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
	out = cv2.VideoWriter('2077.avi',cv2.VideoWriter_fourcc('M','J','P','G'), 23.99, (1920,1080))
	i = 0
	samplerate = int(sd.query_devices(args.device, 'output')['default_samplerate'])
    	# windows can only do wavs for now
	s = source("./songs/2077.mp3", samplerate, hop_s)
	samplerate = s.samplerate
	tolerance = 0.74 # 0.74 is best on average, but more intense songs might be better at higher numbers
	pitch_o = pitch("default", win_s, hop_s, samplerate) # setting a pitch detector
	pitch_x = onset("default", win_s, hop_s, samplerate) # setting a onset detector
	pitch_y = pitch("mcomb", win_s, hop_s, samplerate)
	pitch_o.set_tolerance(tolerance)
	pitch_y.set_tolerance(tolerance)
	clips = listdir("./clips")
	
	global pastpitch
	pastpitch = 0
	
	# change to will, this will determine how often the "flashy" effects will occur. Shorter queue = more frequent flashes
	queue = ['x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x']
	
	# this is the function which plays and analyzes the audio
	def callback(outdata, frames, time, status):
		my_choice = random.choice(clips)
		clip = f'./clips/{my_choice}'
		print(f"New clip: {my_choice}")
		vidcap = cv2.VideoCapture(clip)
		success, img = vidcap.read()
		dim = img.shape
		kv = effects.k9effects2(img)
		pastImgx = 'None'
		
		clips.remove(my_choice)
		kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7,7))
		
		if status:
			print(status, file=sys.stderr)
		
		# still working on reducing the globals
		global start_idx
		global pastpitch
		global i
		global ixx
		ixx = 0
		global pasteffect
		# here we detect  the pitch and onset
		while vidcap.isOpened():
			ixx +=1
			samples, read = s()
			pitch2 = pitch_o(samples)[0] # use o for most artists
			onset = pitch_x(samples)[0]
			pitch = pitch_y(samples)[0] # use y for Flare
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
			outdata[:] = samples
			start_idx += read
			# if no more audio data to read, set effect as 'End' and kill current thread
			if read == 0:
				effect = 'End'
				print("Song ended")
				raise sd.CallbackStop
				out.release()
				return
			#################### Start Code ##################
			if ixx%5==0:
				success, img = vidcap.read()
				if success:
					print(f"New frame: {i}")
					i+=1
					if pastImgx == 'None':
						pastImgx = "x"
						pastImg = img.copy()
					else:
						pastImg = kv.split_color(pastImg) # split color for every frame
						if i%2==0: # every other frame is either hue-shifted and dilated or eroded
							#img[0:667,495:505] = cv2.dilate(img[0:677,495:505], (8,12))
							pastImg = cv2.dilate(pastImg, (40,60))
							pastImg = kv.shift_hue(pastImg)
						else:
							pastImg = cv2.erode(pastImg, (9,1))
						
						if effect == 'Treble':
							pastImg = kv.add_treble(pastImg, dim)
							pastImg2 = img
							img = cv2.add(pastImg,img)
							pastImg = pastImg2
							
						elif effect == 'SubBass':
							#pastImg = kv.add_subbass(pastImg)
							for i in range(5):
								img = kv.add_midbass(img, i)
								img = cv2.dilate(img, kernel)
							#img = kv.add_subbass(img)
							#pastImg = np.abs(pastImg - pastImgx)
							img = cv2.divide(img, pastImg)
							#img = img // pastImg
						elif effect == 'ScratchyBass':
							#img = kv.add_scratchybass(img)
							pastImgx = kv.add_scratchybass(pastImg)
							pastImg = cv2.add(pastImg, pastImgx)
							#pastImg2 = img
							img = cv2.add(img, pastImg)
							pastImg = img
							#img = pastImg
							
						elif effect == 'MidBass':
							img = kv.add_midbass(pastImg, i)
							#img = kv.add_midbass(img, i)
							#img = cv2.multiply(pastImg, img)
							pastImg2 = img
						
						elif effect == 'Real':
							pastImg = kv.add_real(pastImg)
							img = kv.add_real(img)
							pastImg2 = img
							img = cv2.add(pastImg,img)
							pastImg = pastImg2
						
						elif effect == 'Glow':
							pastImg = kv.add_glow(pastImg, img)
							pastImg2 = img
							pastImg = pastImg2
						
						elif effect == 'End':
							cv2.destroyAllWindows()
							print("Done rendering")
							return
						else:
							pastImg = img
						if kv.check_black(img) == True:
							success, img = vidcap.read()
							if not success:
								break
						out.write(img)
						pastpitch = pitch
						pasteffect = effect
						queue.pop(0)
				else:
					break

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
    
