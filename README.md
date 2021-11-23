# AudioVizualizer
Python3 Image processing based audio vizualizer. Utilizes various image processing techniques to "react" to the music being played as best as possible. 

Visual Example: https://youtu.be/qgZ1J5aoySA

# Required Dependencies:
- aubio
- sounddevice
- opencv-python
- numpy

# Running the program
Program is meant to run from the console with arguments for the image to be used and what song to play.
Currently Windows can only do .wav files, Linux can run .wav and mp3's, haven't tested on Mac.

Linux:
`python3 main.py --image paris.jpeg --song why.wav`

Windows:
`./main.py --image paris.jpeg --song why.wav`

If a *ValueError: cannot reshape array of size x into shape (384,)* error is given, change the "hop_s" value in line 74 of main.py into whatever the x value is given in the error message.

# Independent file notes:
Colorsplitter.py can be used as a regular rgb splitting file, just pass it multiple times on the same image until your desired distance is created.
Ex: `python3 colorsplitter.py --file paris.jpeg --out paris.jpeg` and run this a few times. 

Same can be done with hueshift.py although it's less exciting

# effects.py

It's a python class, so it can be imported and used to create simple visual effects.
Copy the file into the working directory, and construct the object using `kv = effects.k9effects()` then you can use the effects by calling which effect you want and passing your image to it. Each function returns a open-cv image object. `img = kv.add_subbass(img)`


Exception - Treble:

Since the treble effect uses image convolution, the original image dimensions need to be passed to it.

Example of using effects.py:

```import effects
img = cv2.imread('paris.jpeg')
kv = effects.k9effects()
glowing_img = kv.add_glow(img)
dim = img.shape
treble_img = kv.add_treble(img, dim)
```
