import numpy as np
import os
import time
from PIL import Image

#Excel
import openpyxl

#Other directories
import sys 
sys.path.append("../../../Analysis/PSNR+SSIM/")
from PSNRSSIM import returnValues

#Matrix for Jarvis error diffusion
jarvisMap = (
        (1, 0,  7 / 48),	# Position [y , x], weighting
        (2, 0,  5 / 48),
        (-2, 1, 3 / 48),
        (-1, 1, 5 / 48),
        (0, 1,  7 / 48),
        (1, 1,  5 / 48),
        (2, 1,  3 / 48),
        (-2, 2, 1 / 48),
        (-1, 2, 3 / 48),
        (0, 2,  5 / 48),
        (1, 2,  3 / 48),
        (2, 2,  1 / 48),
    )

threshold = 40


def watermark(image):
	imageArray = np.array(image, 'float64')									#Image to numpy array

	#Halftone the top half of the image
	for x in range(int(len(imageArray)/2)):
		for y in range(len(imageArray[0])):

			old_pixel = imageArray[x,y]
			new_pixel = (255 if old_pixel >= 128 else 0)
			quant_err=old_pixel-new_pixel
			imageArray[x,y] = new_pixel
			for ypos, xpos, weighting in jarvisMap:						#For every element in the matrix
				newx, newy = x + xpos, y + ypos							#For every neighbouring pixel defined by the matrix
				if (0 <= newx < height) and (0 <= newy < width):		#Check whether the new x and y positions are still valid
					imageArray[newx, newy] += (quant_err * weighting)		#If so, diffuse the error
	#End of halftoning top half
		
	#Bottom half of the image
	for x in range(len(imageToHide)):
		for y in range(len(imageToHide[0])):
			old_pixel = imageArray[int(height/2)+x,y] 					#Pixel in lower half of the image



			#This section is to enforce flipping of colours
			new_pixel = (255 if old_pixel >= 128 else 0)				#Black or white depending on this value
			
			if imageToHide[x,y] == 0:															#If the value of the image to hide is 0
				if imageArray[int(height/2)-x-1,width-y-1] == 0 and new_pixel == 0:					#If the value in the top half of the image is 0 and the new pixel is 0
					testing = abs((128-old_pixel)-0)												#Get minimum value to make new pixel white

					if abs(testing) < threshold:													#If value of change is less than threshold
						old_pixel+=testing															#Add change to pixel value
						
				elif imageArray[int(height/2)-x-1, width-y-1] == 255 and new_pixel == 255:			#If value of the image to hide is 255 
					testing = -1*abs((128-old_pixel)-0)-1											#Get minimum value to make the new pixel black
					if abs(testing) < threshold:													#If value of change is less than threshold
						old_pixel+=testing															#Add change to pixel value
			#End of flipping colours
						
			#Normal process carries on with the updated pixels
			new_pixel = (255 if old_pixel >= 128 else 0)						
			imageArray[int(height/2)+x,y] = new_pixel
			quant_err = old_pixel - new_pixel

			for ypos, xpos, weighting in jarvisMap:						#For every element in the matrix
				newx, newy = int(height/2) + x + xpos, y + ypos							#For every neighbouring pixel defined by the matrix
				if (0 <= newx < height) and (0 <= newy < width):		#Check whether the new x and y positions are still valid
					imageArray[newx, newy] += (quant_err * weighting)		#If so, diffuse the error
	#End of halftoning bottom half
		
	return Image.fromarray(np.array(imageArray, 'uint8'))


def decode(filename):
	#Open encoded image and rotate it against eachother at 180 degrees
	first = Image.open("../../../Images/Embedded/5. Watermark/Error Diffusion/Jarvis/"+filename)
	firstArray = np.array(first, 'float64')
	second = Image.open("../../../Images/Embedded/5. Watermark/Error Diffusion/Jarvis/"+filename).rotate(180)
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
	original = Image.open("../../../Images/Basic Halftone/Error Diffusion/Jarvis/"+filename)
	imageToHide = np.array(Image.open("../Image To Hide/toHide.png"), 'float64')

	print(filename)
		
	start_time = time.time()
	imageConverted = watermark(image)
	embedTime = time.time() - start_time
	imageConverted.save("../../../Images/Embedded/5. Watermark/Error Diffusion/Jarvis/"+filename)

	start_time = time.time()
	decodeXOR = decode(filename)
	decryptTime = time.time() - start_time

	decodeXOR.save("../../../Images/Embedded/5. Watermark/Error Diffusion/Jarvis/XOR/"+filename)
		
	psnr, ssim = returnValues(original,imageConverted)		#Send original and processed image to get PSNR and SSIM values
	psnrValues.append(psnr)
	ssimValues.append(ssim)
	embedTimes.append(embedTime)
	decryptTimes.append(decryptTime)
	messagePercents.append(analyse(decodeXOR))




excel_document = openpyxl.load_workbook("../../../../Data/Data.xlsx")	#Open excel
sheet = (excel_document['1 Image Watermark'])							#Selects sheet

#Input valeus to the sheet
multiple_cells = sheet['I4' : 'I51']
for value, row in enumerate(multiple_cells):
    for cell in row:
    	cell.value = psnrValues[value]

multiple_cells = sheet['J4' : 'J51']
for value, row in enumerate(multiple_cells):
    for cell in row:
    	cell.value = ssimValues[value]

multiple_cells = sheet['K4' : 'K51']
for value, row in enumerate(multiple_cells):
    for cell in row:
    	cell.value = embedTimes[value]

multiple_cells = sheet['L4' : 'L51']
for value, row in enumerate(multiple_cells):
    for cell in row:
    	cell.value = decryptTimes[value]

multiple_cells = sheet['M4' : 'M51']
for value, row in enumerate(multiple_cells):
    for cell in row:
    	cell.value = messagePercents[value]
#End of inputting values


excel_document.save("../../../../Data/Data.xlsx")
