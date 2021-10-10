import numpy as np
import os
import time
from PIL import Image
import cv2

#Excel
import openpyxl

#Other directories
import sys 
sys.path.append("../../../Analysis/PSNR+SSIM/")
from PSNRSSIM import returnValues

#Gradients to be used
gradient1 = Image.open("Gradients/stipple1.png")
gradient1 = np.array(gradient1, 'float64')

gradient6 = Image.open("Gradients/stipple6.png")
gradient6 = np.array(gradient6, 'float64')

threshold = 40

#Stipple each half
def stipple(theHalf):
	for x in range(len(theHalf)):
		for y in range(len(theHalf[0])):
			if(0 <= theHalf[x,y] <= (255/2)*1):
				theHalf[x,y] = gradient1[x,y]
			elif((255/2)*1  <= theHalf[x,y] <= 255):
				theHalf[x,y] = gradient6[x,y]

	return theHalf

#Return what value would be put if it was stippled
def tempValue(pixel,x,y):
	if(0 <= pixel <= (255/2)*1):
		return gradient1[x,y]
	elif((255/2)*1  <= pixel <= 255):
		return gradient6[x,y]

#Change gradient
def findNewGradient(x,y, neededValue, currentPixelValue):

	#If the proposed gradient selection doesn't give the correct value (1 or 0) needed, find how much to change the value in order to get the correct value. 
	#Change greyscale value to change gradient.
	#Until threshold is met or otherwise it could be an endless loop
	addValue = 0
	while(tempValue((currentPixelValue+addValue),x,y) != neededValue) and (addValue < threshold):										
		addValue+=1
	
	minusValue = 0
	while(tempValue((currentPixelValue+minusValue),x,y) != neededValue) and (abs(minusValue) < threshold):
		minusValue-=1
	
	#If the new values get the right number, see which achieves it in less change
	if(tempValue((currentPixelValue+addValue),x,y) == neededValue) or (tempValue((currentPixelValue+minusValue),x,y) == neededValue):
		if(addValue > abs(minusValue)):
			return minusValue
		else:
			return addValue
	else:
		return 0


def watermark(image):

	imageArray = np.array(image, 'float64')
	imageArray = cv2.GaussianBlur(imageArray,(9,9),0)			#Blur the image slightly so the gradients aren't as harsh on boundaries


	#Halftone the top of the image
	topHalf = imageArray[0:0+256, 0:0+512]
	topHalf = stipple(topHalf)
	imageArray[0:0+256,0:0+512] = topHalf
	#End of halftoning top half

	#Halftone the bottom half of the image
	bottomHalf = imageArray[256:256+256, 0:0+512]
	for x in range(len(imageToHide)):
		for y in range(len(imageToHide[0])):
			old_pixel = bottomHalf[x,y] 
			new_pixel = tempValue(old_pixel,x,y)
			
			if imageToHide[x,y] == 0:																#For every black pixel in the image to hide
				if imageArray[int(height/2)-x-1,width-y-1] == 0 and new_pixel == 0:					#If the top half pixel is black and the new pixel is black...
					value = findNewGradient(x,y,255, old_pixel)										#See if it can be changed
					
					bottomHalf[x,y]+=value


				elif imageArray[int(height/2)-x-1, width-y-1] == 255 and new_pixel == 255:			#If the top half pixel is white and the new pixel is white...
					value = findNewGradient(x,y,0, old_pixel)										#See if it can be changed

					bottomHalf[x,y]+=value
					
	imageArray[256:256+256, 0:0+512] = stipple(bottomHalf)
	#End of halftoning bottom half

	return Image.fromarray(np.array(imageArray, 'uint8'))



def decode(filename):
	#Open encoded image and rotate it against eachother at 180 degrees
	first = Image.open("../../../Images/Embedded/5. Watermark/Stippled/2 Gradient/"+filename)
	firstArray = np.array(first, 'float64')
	second = Image.open("../../../Images/Embedded/5. Watermark/Stippled/2 Gradient/"+filename).rotate(180)
	secondArray = np.array(second, 'float64')

	#Iterate through the image
	for i in range(0,int(len(firstArray))):
		for j in range(len(firstArray[0])):
			if firstArray[i,j] != secondArray[i,j]:				#If the images are not the same colour (one image is rotated ontop of the other)
				firstArray[i,j] = 0								#Make the image pixel black
			else:												#If the images are the same colour
				firstArray[i,j] = 255							#Make the pixel white

	
	newImage = Image.fromarray(np.array(firstArray,'uint8'))
	return newImage												#Return the XOR image


		
def analyse(image):
	image = np.asarray(image, dtype='float64')
	hiddenImage = np.count_nonzero(imageToHide == 0)

	#Compare the decoded image against the hidden image
	value = 0
	for x in range(0, int(height/2)):
		for y in range(0, width):
			if image[x+(int(height/2)),y] == 0 and imageToHide[x,y] == 0:
				value +=1
	print((value/hiddenImage)*100)
	print()
	return(value/hiddenImage)*100


embedTimes = []
decryptTimes = []
psnrValues = []
ssimValues = []
messagePercents = []

fileList = []
for file in os.listdir("../../../Images/Original/"):
	fileList.append(file[:-4])
fileList = sorted(fileList, key=int)

for file in fileList:
	filename = os.fsdecode(file)
	filename+=".png"
	 
	image = Image.open("../../../Images/Original/"+filename)
	width, height = image.size
	original = Image.open("../../../Images/Basic Halftone/Stippled/2 Gradient/"+filename)
	imageToHide = np.array(Image.open("../Image To Hide/toHide.png"), 'float64')

	print(filename)
		
	start_time = time.time()
	imageConverted = watermark(image)
	embedTime = time.time() - start_time
	imageConverted.save("../../../Images/Embedded/5. Watermark/Stippled/2 Gradient/"+filename)

	start_time = time.time()
	decodeXOR = decode(filename)
	decryptTime = time.time() - start_time
	
	decodeXOR.save("../../../Images/Embedded/5. Watermark/Stippled/2 Gradient/XOR/"+filename)
	
	psnr, ssim = returnValues(original,imageConverted)		#Send original and processed image to get PSNR and SSIM values
	psnrValues.append(psnr)
	ssimValues.append(ssim)
	embedTimes.append(embedTime)
	decryptTimes.append(decryptTime)
	messagePercents.append(analyse(decodeXOR))


excel_document = openpyxl.load_workbook("../../../../Data/Data.xlsx")
sheet = (excel_document['1 Image Watermark'])

multiple_cells = sheet['AJ4' : 'AJ51']
for value, row in enumerate(multiple_cells):
    for cell in row:
    	cell.value = psnrValues[value]

multiple_cells = sheet['AK4' : 'AK51']
for value, row in enumerate(multiple_cells):
    for cell in row:
    	cell.value = ssimValues[value]

multiple_cells = sheet['AL4' : 'AL51']
for value, row in enumerate(multiple_cells):
    for cell in row:
    	cell.value = embedTimes[value]

multiple_cells = sheet['AM4' : 'AM51']
for value, row in enumerate(multiple_cells):
    for cell in row:
    	cell.value = decryptTimes[value]

multiple_cells = sheet['AN4' : 'AN51']
for value, row in enumerate(multiple_cells):
    for cell in row:
    	cell.value = messagePercents[value]


excel_document.save("../../../../Data/Data.xlsx")
