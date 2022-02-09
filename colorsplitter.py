# import statements
import cv2
import numpy as np
import argparse

# this is the main function that creates the r-g-b split
# debug set to True for actual split, set to False for video style
def create_img(filename, DEBUG):
	
	# tries to read the file in as a filetype if it fails it defaults to opencv image type
	try:
		img = cv2.imread(filename)
	except:
		img = filename
	
	# splitting the image into the blue green and red channels
	b, g, r = cv2.split(img)
	
	# getting the width and height of the image
	width = int(b.shape[1])
	height = int(b.shape[0])
	
		
	# divides the image by 250 to determine how much to stretch it by
	wdivisor = int(width/250)
	hdivisor = int(height/250)
	
	# calculating the new width and height by adding the divisor to it
	nwidth = width+wdivisor
	nheight = height+hdivisor
	
	
	# resizes the red channel to the big size, crops image down, and then resizes back to original shape
	nr = cv2.resize(r,(nwidth,nheight))
	rc = nr[hdivisor:height+3,wdivisor:width]
	rc = cv2.resize(rc,(width,height))

	# resizes the green channel to the big size, crops image down, and then resizes back to original shape
	ng = cv2.resize(g,(nwidth,nheight))
	
	# if True itll split it sideways, otherwise it splits it up
	if DEBUG:
		rg = ng[hdivisor:height,wdivisor-1:width]
	else:
		rg = ng[hdivisor+1:height+1,wdivisor:width]
	rg = cv2.resize(rg,(width,height))


	# resizes the blue channel to the big size, crops image down, and then resizes back to original shape
	rb = cv2.resize(b,(nwidth,nheight))
	
	# if True itll split it sideways, otherwise it splits it down
	if DEBUG:
		rb = rb[hdivisor:height,wdivisor+1:width]
	else:
		rb = rb[hdivisor+1:height,wdivisor:width]
	rb = cv2.resize(rb,(width,height))

	# re-merges the re-sized color channels and returns final image
	merged = cv2.merge([rb,rg,rc])
	return merged


def main():
    parser = argparse.ArgumentParser()
    
    parser.add_argument('--file', dest='imgFile', required=True)
    parser.add_argument('--out', dest='outFile', required=False)
    args = parser.parse_args()

    imgFile = args.imgFile
    
    if args.outFile:
    	outfile = args.outFile
    else:
    	outfile = 'out.png'

    merged = create_img(imgFile , True)
    cv2.imwrite(outfile, merged)

if __name__ == '__main__':
    main()
