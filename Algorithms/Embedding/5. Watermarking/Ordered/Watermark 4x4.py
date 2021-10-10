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

threshold = 40/256


def watermark(image):
	imageArray = np.array(image, 'float64')							#Image to numpy array
	imageArray = np.divide(imageArray, 256)							#Divides image values by the range of pixel values. 256 for 8 bit images


	#Matrix for Ordered dither
	the_4x4 = np.array([[0,8,2,10],
					[12,4,14,6],
					[3,11,1,9],
					[15,7,13,5]])


	the_4x4 = np.divide(the_4x4,16)									#Divide the matrix by size
	tiled = np.tile(the_4x4,(64,128))								#So the matrix spans the entire image
	
	#Halftone the top half of the image
	topHalf = imageArray[0:0+256, 0:0+512]
	thresh_test = topHalf > tiled
	
	topHalf[thresh_test == True] = 255								#If true, make the pixel on the image white
	topHalf[thresh_test == False] = 0								#If false, make the pixel on the image black

	imageArray[0:0+256,0:0+512] = topHalf	
	#End of halftoning top half


	#Halftone the bottom half of the image
	bottomHalf = imageArray[256:256+256, 0:0+512]

	for x in range(len(imageToHide)):
		for y in range(len(imageToHide[0])):
			old_pixel = bottomHalf[x,y] 


			#This section is to enforce flipping of colours
			new_pixel = (255 if (old_pixel>tiled[x,y]) else 0)
			#if True:
			if imageToHide[x,y] == 0:
				if imageArray[int(height/2)-x-1,width-y-1] == 0 and new_pixel == 0:
					testing = abs((old_pixel)- tiled[x,y])
					testing+=0.0000000000001
					
					if abs(testing) < threshold:
						old_pixel+=testing


				elif imageArray[int(height/2)-x-1, width-y-1] == 255 and new_pixel == 255:
					testing = -1*abs(old_pixel-tiled[x,y])
					testing -= 0.00000000000001

					if abs(testing) < threshold:
						old_pixel+=testing


			#Normal process carries on with the updated pixels
			new_pixel = (255 if (old_pixel>tiled[x,y]) else 0)
			bottomHalf[x,y] = new_pixel
			
	
	thresh_test = bottomHalf > tiled
	bottomHalf[thresh_test == True] = 255								#If true, make the pixel on the image white
	bottomHalf[thresh_test == False] = 0								#If false, make the pixel on the image black

	imageArray[256:256+256, 0:0+512] = bottomHalf

	return Image.fromarray(np.array(imageArray, 'uint8'))



def decode(filename):
	#Open encoded image and rotate it against eachother at 180 degrees
	first = Image.open("../../../Images/Embedded/5. Watermark/Ordered/4x4/"+filename)
	firstArray = np.array(first, 'float64')
	second = Image.open("../../../Images/Embedded/5. Watermark/Ordered/4x4/"+filename).rotate(180)
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
	original = Image.open("../../../Images/Basic Halftone/Ordered/4x4/"+filename)
	imageToHide = np.array(Image.open("../Image To Hide/toHide.png"), 'float64')

	print(filename)
		
	start_time = time.time()
	imageConverted = watermark(image)
	embedTime = time.time() - start_time
	imageConverted.save("../../../Images/Embedded/5. Watermark/Ordered/4x4/"+filename)

	start_time = time.time()
	decodeXOR = decode(filename)
	decryptTime = time.time() - start_time

	decodeXOR.save("../../../Images/Embedded/5. Watermark/Ordered/4x4/XOR/"+filename)
	
	psnr, ssim = returnValues(original,imageConverted)		#Send original and processed image to get PSNR and SSIM values
	psnrValues.append(psnr)
	ssimValues.append(ssim)
	embedTimes.append(embedTime)
	decryptTimes.append(decryptTime)
	messagePercents.append(analyse(decodeXOR))




excel_document = openpyxl.load_workbook("../../../../Data/Data.xlsx")	#Open excel
sheet = (excel_document['1 Image Watermark'])							#Selects sheet

#Input valeus to the sheet
multiple_cells = sheet['Y4' : 'Y51']
for value, row in enumerate(multiple_cells):
    for cell in row:
    	cell.value = psnrValues[value]

multiple_cells = sheet['Z4' : 'Z51']
for value, row in enumerate(multiple_cells):
    for cell in row:
    	cell.value = ssimValues[value]

multiple_cells = sheet['AA4' : 'AA51']
for value, row in enumerate(multiple_cells):
    for cell in row:
    	cell.value = embedTimes[value]

multiple_cells = sheet['AB4' : 'AB51']
for value, row in enumerate(multiple_cells):
    for cell in row:
    	cell.value = decryptTimes[value]

multiple_cells = sheet['AC4' : 'AC51']
for value, row in enumerate(multiple_cells):
    for cell in row:
    	cell.value = messagePercents[value]
#End of inputting values


excel_document.save("../../../../Data/Data.xlsx")
