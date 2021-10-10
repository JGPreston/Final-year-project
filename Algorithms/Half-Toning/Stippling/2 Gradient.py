import numpy as np
import os
import time
import cv2
from PIL import Image

#Excel
import openpyxl

#Add path to directory
import sys 
sys.path.append("../../Analysis/PSNR+SSIM/")
from PSNRSSIM import returnValues

#Gradients to use
gradient1 = Image.open("Gradients/stipple1.png")
gradient1 = np.array(gradient1, 'float64')

gradient6 = Image.open("Gradients/stipple6.png")
gradient6 = np.array(gradient6, 'float64')


def convert_halftoning(image):
	height, width = image.size
	imageArray = np.array(image, 'float64')							#Image to numpy array
	imageArray = cv2.GaussianBlur(imageArray,(9,9),0)				#Smooth out the image a little so that the have a slight blend
	
	for x in range(height):					
		for y in range(width):

			#If pixel value is in a defined range, make the pixel value the gradients value
			if(0 <= imageArray[x,y] <= (255/2)*1):					
				imageArray[x,y] = gradient1[x,y]
			elif((255/2)*1  <= imageArray[x,y] <= 255):
				imageArray[x,y] = gradient6[x,y]
		
	return Image.fromarray(np.array(imageArray, 'uint8'))			#Return image from the numpy array


times = []
psnrValues = []
ssimValues = []

#Processes every file in the original images folder
fileList = []
for file in os.listdir("../../Images/Original/"):
	fileList.append(file[:-4])						#Remove the file extension so 
fileList = sorted(fileList, key=int)				#it can be sorted by int

for file in fileList:								#For every file in the sorted file list	
	filename = os.fsdecode(file)					
	filename+=".png"								#Add png file extension. Converts any file format to png 
	 
		
	image = Image.open("../../Images/Original/"+filename)										#Open original image to halftone
	original = Image.open("../../Images/Original/"+filename)									#For comparing
	print(filename)

	start_time = time.time()
	imageConverted = convert_halftoning(image)
	finalTime = time.time() - start_time
		
	imageConverted.save("../../Images/Basic Halftone/Stippled/2 Gradient/"+filename)

	psnr, ssim = returnValues(original,imageConverted)											#Send original and processed image to get PSNR and SSIM values
	psnrValues.append(psnr)
	ssimValues.append(ssim)
	times.append(finalTime)
	

excel_document = openpyxl.load_workbook("../../../Data/Data.xlsx")		#Open excel 
sheet = (excel_document['Basic Halftone'])								#Selects sheet

#Input values to the sheet
multiple_cells = sheet['X4' : 'X51']
for value, row in enumerate(multiple_cells):
    for cell in row:
    	cell.value = psnrValues[value]

multiple_cells = sheet['Y4' : 'Y51']
for value, row in enumerate(multiple_cells):
    for cell in row:
    	cell.value = ssimValues[value]

multiple_cells = sheet['Z4' : 'Z51']
for value, row in enumerate(multiple_cells):
    for cell in row:
    	cell.value = times[value]
#End of inputting values


excel_document.save("../../../Data/Data.xlsx")