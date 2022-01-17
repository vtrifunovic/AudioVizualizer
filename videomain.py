'''Import statements'''
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

def render(filename):
	global img2
	global effect
	out = cv2.VideoWriter('demons.avi',cv2.VideoWriter_fourcc('M','J','P','G'), 56, (1254,878))
	img2 = cv2.imread(filename)
	while 1:
		if effect == 'End':
			break
		else:
			out.write(img2)
			#time.sleep(0.1)
	out.release()
	return
	
'''Default sounddevice code, leaving this in'''
def int_or_str(text):
    try:
        return int(text)
    except ValueError:
        return text
        
'''Creates a full-screen open-cv window which displays the video'''
def create_visual(filename):
	global effect
	#global img2
	#img = cv2.imread(filename)
	i = 0
	clips = listdir("./clips")
	#out = cv2.VideoWriter('biva.avi',cv2.VideoWriter_fourcc('M','J','P','G'), 23.98, (1920,1080))
	while 1:
		my_choice = random.choice(clips)
		clip = f'./clips/{my_choice}'
		clips.remove(my_choice)
		print(clip)
		vidcap = cv2.VideoCapture(clip)
		success, img = vidcap.read()
		dim = img.shape
		kv = effects.k9effects2(img)
		pastImgx = 'None'
		kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7,7))
		while vidcap.isOpened():
			success, img = vidcap.read()
			if success:
				# checks for dead frame, if found re-starts visual
				#s_time = time.perf_counter()
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
					
					# Not an effect, done to synchronize thread killing
					elif effect == 'End':
						cv2.destroyAllWindows()
						return
					else:
						pastImg = img
					if kv.check_black(img) == True:
						success, img = vidcap.read()
						if not success:
							break
					# displays full screen video 
					cv2.namedWindow("Video", cv2.WINDOW_FREERATIO)
					cv2.setWindowProperty("Video", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
					cv2.imshow("Video", img)
					cv2.waitKey(25) # put as 1 on cpu's below 4GHZ max frequency or if dealing with 1920x1080
					#video.append(img)
					#out.write(img)
					#try:
					#	time.sleep(0.0417-(time.perf_counter()-s_time))
					#except ValueError:
					#	pass
			else:
				break
	
	# kills window and ends thread
	print("Killing Window!")
	cv2.destroyAllWindows()
	#print("Rendering")
	#for frame in video:
	#	out.write(frame)
	#out.release()
	print(i)
	#print("Done!")
	return


'''Plays and samples audio to determine what effect to use'''
def create_sound(songname):
	win_s = 4096
	hop_s = 384 # hop_s will need to change depending on the system
	samplerate = 0

    # windows can only do wavs for now
	s = source("./songs/" + songname, samplerate, hop_s)
	samplerate = s.samplerate
	tolerance = 0.74 # 0.74 is best on average, but more intense songs might be better at higher numbers
	pitch_o = pitch("default", win_s, hop_s, samplerate) # setting a pitch detector
	pitch_x = onset("default", win_s, hop_s, samplerate) # setting a onset detector
	pitch_y = pitch("mcomb", win_s, hop_s, samplerate)
	pitch_o.set_tolerance(tolerance)
	pitch_y.set_tolerance(tolerance)
	
	try:
		samplerate = sd.query_devices(args.device, 'output')['default_samplerate']
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
			global pasteffect
			global effect
			
			# here we detect  the pitch and onset
			samples, read = s()
			pitch2 = pitch_o(samples)[0] # use o for most artists
			onset = pitch_x(samples)[0]
			pitch = pitch_y(samples)[0] # use y for Flare
			# testing various parameters to determine which efect is best to be applied
			if pitch == 0 and pastpitch != 0 and pasteffect != 'Glow':
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
			print(int(pitch), effect, onset, int(pitch2))
			# re-shaping and passing audio data to the speakers
			outdata.shape = samples.shape
			outdata[:] = samples
			start_idx += read
			# if no more audio data to read, set effect as 'End' and kill current thread
			if read == 0:
				effect = 'End'
				print(queue)
				raise sd.CallbackStop
				return
			pastpitch = pitch
			pasteffect = effect
			queue.pop(0) # removing most recent effect from the queue, so that it stays the same length

		# running the output stream to play audio
		with sd.OutputStream(device=args.device, channels=1, callback=callback, samplerate=samplerate):
			input()
		return

	except KeyboardInterrupt:
		parser.exit('User killed program')
	except Exception as e:
		parser.exit(type(e).__name__ + ': ' + str(e))

if __name__ == "__main__":
	# forgive me for global usage
	global effect
	global pasteffect
	effect = ''
	pasteffect = ''
	
	# adding argparse to so setting can be changed from command-line
	parser = argparse.ArgumentParser(add_help=False)
	parser.add_argument('-l', '--list-devices', action='store_true', help='show list of audio devices and exit')
	args, remaining = parser.parse_known_args()
	if args.list_devices:
		print(sd.query_devices())
		parser.exit(0)
	parser.add_argument('-d', '--device', type=int_or_str, help='output device (numeric ID or substring)')
	parser.add_argument('--image', dest='imgFile', required = True)
	parser.add_argument('--song', dest='sngFile', required = True)
	args = parser.parse_args(remaining)
	
	# parsing for required imagefile and songfile
	filename = args.imgFile
	songname = args.sngFile
	
	# set start position for sound
	start_idx = 0
	# set tx as daemon or it wont properly terminate program
	# setting two threads one for audio and one for visuals
	tx = threading.Thread(target=create_sound, args=(songname,), daemon=True) 
	t2 = threading.Thread(target=create_visual, args=(filename,))
	#t3 = threading.Thread(target=render, args=(filename,))
	tx.start()
	t2.start()
	#t3.start()
	t2.join()
	print("Thread 2 complete!")
	# without timeout thread wont end. idk why !!!!! HELP
	tx.join(timeout=0.5)
	print("Thread 1 complete!")
	#t3.join()

