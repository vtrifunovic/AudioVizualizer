import cv2
import numpy as np
import colorsplitter
import hueshift

class k9effects:
	
	def __init__(self, img):
		self.kernel = np.array(([1, -1, 1], [-1, 1, -1], [1, -1, 1]), dtype='uint8')
		self.a = img.copy()
	
	# creates simple rgb split
	def split_color(self, img):
		img = colorsplitter.create_img(img, False) # set 2nd param to true for sideways split
		return img
		
	# shifts hue slightly, allows for tearing in the image
	def shift_hue(self, img):
		img = hueshift.create_img(img, False)
		return img
	
	# Treble effect, performs contrast stretching and convolution
	def add_treble(self, img, dim):
		original = img.copy()
		xp = [0, 64, 128, 190, 255]
		fp = [0, 16, 128, 240, 255]
		x = np.arange(256)
		table = np.interp(x, xp, fp).astype('uint8')
		img = cv2.LUT(img, table)
		img = np.convolve(img.flatten(), self.kernel.flatten(), 'same')
		img.shape = dim
		#img = cv2.multiply(self.a, img)
		return img
	
	# SubBass effect, high contrast stretch and hue shift
	def add_subbass(self, img):
		img = hueshift.create_img(img, 'High')
		return img
		
	# ScratchyBass effect, low contrast stretch, hue shift, and dilation	
	def add_scratchybass(self, img):
		img = hueshift.create_img(img, 'Low')
		img = cv2.dilate(img, (5, 15))
		return img

	# MidBass effect, hue shift and dilation. no contrast stretch
	def add_midbass(self, img):
		img = hueshift.create_img(img, False)
		img = cv2.dilate(img, (5, 5))
		return img
	
	# Real effect, adds 40 to the saturation channel, creates a white-spots effect
	def add_real(self, img):
		img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
		h, s, v = cv2.split(img)
		s += 40
		img = cv2.merge([h, s, v])
		img = cv2.cvtColor(img, cv2.COLOR_HSV2BGR)
		return img
	
	# Glow effect, performs contrast stretch, and then a open-cv GBlur and added weight to create glow like feel
	def add_glow(self, img):
		original = img.copy()

		xp = [0, 64, 128, 190, 255]
		fp = [0, 16, 128, 240, 255]

		x = np.arange(256)
		table = np.interp(x, xp, fp).astype('uint8')
		img = cv2.LUT(img, table)
		img_b = cv2.GaussianBlur(img, (17, 17), 1)
		img = cv2.addWeighted(img, 1, img_b, 3, 0)
		#img = cv2.multiply(self.a, -img)
		return img
	
	# checks for dead frame, if found re-starts visual
	def check_black(self, img):
		return np.mean(img)
			
class k9effects2:
	
	def __init__(self, img):
		self.kernel = np.array(([1, -1, 1], [-1, 7, -1], [1, -1, 1]), dtype='uint8')
		self.a = img.copy()
		self.dim = img.shape
	
	# creates simple rgb split
	def split_color(self, img):
		img = colorsplitter.create_img(img, True) # set 2nd param to true for sideways split
		return img
		
	# shifts hue slightly, allows for tearing in the image
	def shift_hue(self, img):
		img = hueshift.create_img(img, 'High')
		return img
	
	# Treble effect, performs contrast stretching and convolution
	def add_treble(self, img, dim):
		original = img.copy()
		xp = [0, 64, 128, 190, 255]
		fp = [0, 16, 128, 240, 255]
		x = np.arange(256)
		table = np.interp(x, xp, fp).astype('uint8')
		img = cv2.LUT(img, table)
		img = np.convolve(img.flatten(), self.kernel.flatten(), 'same')
		img.shape = dim
		#img = cv2.multiply(self.a, img)
		return img
	
	# SubBass effect, high contrast stretch and hue shift
	def add_subbass(self, img):
		img = hueshift.create_img(img, 'High')
		img = cv2.dilate(img, (15,15))
		return img
		
	# ScratchyBass effect, low contrast stretch, hue shift, and dilation	
	def add_scratchybass(self, img):
		#img = np.convolve(img.flatten(), self.kernel.flatten(), 'same')
		#img.shape = self.dim
		img = hueshift.create_img(img, 'Low')
		img = cv2.dilate(img, (50, 15)) # was erode
		return img

	# MidBass effect, hue shift and dilation. no contrast stretch
	def add_midbass(self, img, i):
		img = hueshift.create_img(img, 'Low')
		if i%2 == 0:
			img = colorsplitter.create_img(img, True)
			img = colorsplitter.create_img(img, True)
			img = colorsplitter.create_img(img, True)
			img = colorsplitter.create_img(img, True)
			img = colorsplitter.create_img(img, True)
		else:
			img = colorsplitter.create_img(img, False)
			img = colorsplitter.create_img(img, False)
			img = colorsplitter.create_img(img, False)
			img = colorsplitter.create_img(img, False)
			img = colorsplitter.create_img(img, False)

		img = cv2.dilate(img, (25, 25))
		return img
	
	# Real effect, adds 40 to the saturation channel, creates a white-spots effect
	def add_real(self, img):
		img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
		h, s, v = cv2.split(img)
		s += 40
		img = cv2.merge([h, s, v])
		img = cv2.cvtColor(img, cv2.COLOR_HSV2BGR)
		return img
	
	# Glow effect, performs contrast stretch, and then a open-cv GBlur and added weight to create glow like feel
	def add_glow(self, img, img2):

		xp = [0, 64, 128, 190, 255]
		fp = [0, 16, 128, 240, 255]

		x = np.arange(256)
		table = np.interp(x, xp, fp).astype('uint8')
		img = cv2.LUT(img2, table)
		img2 = cv2.GaussianBlur(img, (17, 17), 1)
		img = cv2.addWeighted(img, 1, img2, 3, 0)
		#img = cv2.multiply(self.a, -img)
		return img
	
	# checks for dead frame, if found re-starts visual
	def check_black(self, img):
		if np.mean(img) == 0:
			return True
		else:
			return False			
			
