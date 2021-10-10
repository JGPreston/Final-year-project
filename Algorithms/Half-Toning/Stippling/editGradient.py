from PIL import Image
from PIL import ImageFilter
import math
import matplotlib.pyplot as plt
import numpy as np
import os
import time
import itertools
import binascii
from array import array
import re
import copy
import random

gradient0 = Image.open("Gradient/stipple0.png")
gradient0 = np.array(gradient0, 'float')

gradient1 = Image.open("Gradient/stipple1.png")
gradient1 = np.array(gradient1, 'float')

gradient2 = Image.open("Gradient/stipple2.png")
gradient2 = np.array(gradient2, 'float')

gradient3 = Image.open("Gradient/stipple3.png")
gradient3 = np.array(gradient3, 'float')

gradient4 = Image.open("Gradient/stipple4.png")
gradient4 = np.array(gradient4, 'float')

gradient5 = Image.open("Gradient/stipple5.png")
gradient5 = np.array(gradient5, 'float')

gradient6 = Image.open("Gradient/stipple6.png")
gradient6 = np.array(gradient6, 'float')

gradient7 = Image.open("Gradient/stipple7.png")
gradient7 = np.array(gradient7, 'float')

def stipple(image):
	image = image.convert('L', dither = False)
	#image = image.filter(ImageFilter.EDGE_ENHANCE_MORE)

	imageArray = np.array(image, 'float')
	for i in range(len(imageArray)):
		for j in range(len(imageArray[0])):
			new_pixel = (255 if imageArray[i,j] >= 128 else 0)
			imageArray[i,j] = new_pixel

		
			

	return Image.fromarray(np.array(imageArray, 'uint8'))


for file in os.listdir("Gradient"):
	start_time = time.time()
	filename = os.fsdecode(file)
	if filename.endswith(".png") or filename.endswith(".jpg") or filename.endswith(".gif"): 
		# print(os.path.join(directory, filename))
		image = Image.open("Gradient/"+filename)
		print(filename)
		
		imageConverted = stipple(image)

		imageConverted.save("Gradient/"+filename)
		print("--- %s seconds ---" % (time.time() - start_time))
		continue
	else:
		continue