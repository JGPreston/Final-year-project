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
gradient0 = Image.open("Gradients/stipple0.png")
gradient0 = np.array(gradient0, 'float64')

gradient1 = Image.open("Gradients/stipple1.png")
gradient1 = np.array(gradient1, 'float64')

gradient2 = Image.open("Gradients/stipple2.png")
gradient2 = np.array(gradient2, 'float64')

gradient3 = Image.open("Gradients/stipple3.png")
gradient3 = np.array(gradient3, 'float64')

gradient4 = Image.open("Gradients/stipple4.png")
gradient4 = np.array(gradient4, 'float64')

gradient5 = Image.open("Gradients/stipple5.png")
gradient5 = np.array(gradient5, 'float64')

gradient6 = Image.open("Gradients/stipple6.png")
gradient6 = np.array(gradient6, 'float64')

gradient7 = Image.open("Gradients/stipple7.png")
gradient7 = np.array(gradient7, 'float64')

def convert_halftoning(image):
	height, width = image.size
	imageArray = np.array(image, 'float64')							#Image to numpy array
	imageArray = cv2.GaussianBlur(imageArray,(9,9),0)				#Smooth out the image a little so that the have a slight blend
	
	for x in range(height):					
		for y in range(width):
		
			#If pixel value is in a defined range, make the pixel value the gradients value
			if((255/8)*0 <= imageArray[x,y] <= (255/8)*1):
				imageArray[x,y] = gradient0[x,y]
			elif((255/8)*1  <= imageArray[x,y] <= (255/8)*2):
				imageArray[x,y] = gradient1[x,y]
			elif((255/8)*2 <= imageArray[x,y] <= (255/8)*3):
				imageArray[x,y] = gradient2[x,y]
			elif((255/8)*3 <= imageArray[x,y] <= (255/8)*4):
				imageArray[x,y] = gradient3[x,y]
			elif((255/8)*4 <= imageArray[x,y] <= (255/8)*5):
				imageArray[x,y] = gradient4[x,y]
			elif((255/8)*5 <= imageArray[x,y] <= (255/8)*6):
				imageArray[x,y] = gradient5[x,y]
			elif((255/8)*6 <= imageArray[x,y] <= (255/8)*7):
				imageArray[x,y] = gradient6[x,y]
			elif((255/8)*7 <= imageArray[x,y] <= (255/8)*8):
				imageArray[x,y] = gradient7[x,y]
		
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
		
	imageConverted.save("../../Images/Basic Halftone/Stippled/8 Gradient/"+filename)

	psnr, ssim = returnValues(original,imageConverted)											#Send original and processed image to get PSNR and SSIM values
	psnrValues.append(psnr)
	ssimValues.append(ssim)
	times.append(finalTime)
	

excel_document = openpyxl.load_workbook("../../../Data/Data.xlsx")		#Open excel 
sheet = (excel_document['Basic Halftone'])								#Selects sheet

#Input values to the sheet
multiple_cells = sheet['AG4' : 'AG51']
for value, row in enumerate(multiple_cells):
    for cell in row:
    	cell.value = psnrValues[value]

multiple_cells = sheet['AH4' : 'AH51']
for value, row in enumerate(multiple_cells):
    for cell in row:
    	cell.value = ssimValues[value]

multiple_cells = sheet['AI4' : 'AI51']
for value, row in enumerate(multiple_cells):
    for cell in row:
    	cell.value = times[value]
#End of inputting values


excel_document.save("../../../Data/Data.xlsx")