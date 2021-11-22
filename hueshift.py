# import statements 
import cv2
import numpy as np
import argparse


# function that creates the color shift
def create_img(filename, DEBUG):
	
	# trys reading in the image as a file, if not its passed as an cv2 image object
	try:
		img = cv2.imread(filename)
	except:
		img = filename
	
	# splits the image into the blue green and red channels
	b, g, r = cv2.split(img)

	# adding 2 to all blue pixels, if debug is passed as high/low an appropriate contrast stretch is performed
	b = b + 2
	if DEBUG == 'High':
		original = b.copy()

		xp = [0, 64, 128, 192, 255]
		fp = [0, 16, 128, 240, 255]

		x = np.arange(256)
		table = np.interp(x, xp, fp).astype('uint8')
		b = cv2.LUT(b, table)
	elif DEBUG == 'Low':
		original = b.copy()

		xp = [0, 20, 128, 236, 255]
		fp = [0, 16, 128, 240, 255]

		x = np.arange(256)
		table = np.interp(x, xp, fp).astype('uint8')
		b = cv2.LUT(b, table)
	
	# adding 1 to all green pixels, if debug is passed as high/low an appropriate contrast stretch is performed
	g = g + 1
	if DEBUG == 'High':
		original = g.copy()

		xp = [0, 64, 128, 192, 255]
		fp = [0, 16, 128, 240, 255]

		x = np.arange(256)
		table = np.interp(x, xp, fp).astype('uint8')
		g = cv2.LUT(g, table)
	elif DEBUG == 'Low':
		original = g.copy()

		xp = [0, 20, 128, 236, 255]
		fp = [0, 16, 128, 240, 255]

		x = np.arange(256)
		table = np.interp(x, xp, fp).astype('uint8')
		g = cv2.LUT(g, table)
		
	# adding 1 to all red pixels, if debug is passed as high/low an appropriate contrast stretch is performed
	r = r + 1
	if DEBUG == 'High':
		original = r.copy()

		xp = [0, 64, 128, 192, 255]
		fp = [0, 16, 128, 240, 255]

		x = np.arange(256)
		table = np.interp(x, xp, fp).astype('uint8')
		r = cv2.LUT(r, table)
	elif DEBUG == 'Low':
		original = r.copy()

		xp = [0, 20, 128, 236, 255]
		fp = [0, 16, 128, 240, 255]

		x = np.arange(256)
		table = np.interp(x, xp, fp).astype('uint8')
		r = cv2.LUT(r, table)
	
	# merging the channels back together and returning the final image
	merged = cv2.merge([b, g, r])

	return merged


# creates a simple shift in hue if used by itself
def main():
    parser = argparse.ArgumentParser()
    
    parser.add_argument('--file', dest='imgFile', required=True)
    args = parser.parse_args()

    imgFile = args.imgFile

    merged = create_img(imgFile, False)
    cv2.imwrite('out.png',merged)

if __name__ == '__main__':
    main()
