import numpy as np
import os
import time
from PIL import Image

#Excel
import openpyxl

#Add path to directory
import sys 
sys.path.append("../../Analysis/PSNR+SSIM/")
from PSNRSSIM import returnValues



def convert_halftoning(image):
	#Matrix for 8x8 Ordered
	the_8x8 = np.array([[0, 48, 12, 60, 3, 51, 15, 63],
					    [32, 16, 44, 28, 35, 19, 47, 31],
					    [8, 56, 4, 52, 11, 59, 7, 55],
					    [40, 24, 36, 20, 43, 27, 39, 23],
					    [2, 50, 14, 62, 1, 49, 13, 61],
					    [34, 18, 46, 30, 33, 17, 45, 29],
					    [10, 58, 6, 54, 9, 57, 5, 53],
					    [42, 26, 38, 22, 41, 25, 37, 21]])


	image = np.array(image, 'float64') 								#Image to numpy array
	image = np.divide(image, 256)									#Divides image values by the range of pixel values. 256 for 8 bit images

	the_8x8 = np.divide(the_8x8,64)									#Divide the matrix by size
	tiled = np.tile(the_8x8,(64,64))								#So the matrix spans the entire image
	
	thresh_test = image > tiled										#If the image value is larger than the threshold value, return true
	image[thresh_test == True] = 255								#If true, make the pixel on the image white
	image[thresh_test == False] = 0									#If false, make the pixel on the image black

	return Image.fromarray(np.array(image, 'uint8'))				#Return image from the numpy array


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
		
	imageConverted.save("../../Images/Basic Halftone/Ordered/8x8/"+filename)

	psnr, ssim = returnValues(original,imageConverted)											#Send original and processed image to get PSNR and SSIM values
	psnrValues.append(psnr)
	ssimValues.append(ssim)
	times.append(finalTime)
	

excel_document = openpyxl.load_workbook("../../../Data/Data.xlsx")		#Open excel 
sheet = (excel_document['Basic Halftone'])								#Selects sheet

#Input values to the sheet
multiple_cells = sheet['T4' : 'T51']
for value, row in enumerate(multiple_cells):
    for cell in row:
    	cell.value = psnrValues[value]

multiple_cells = sheet['U4' : 'U51']
for value, row in enumerate(multiple_cells):
    for cell in row:
    	cell.value = ssimValues[value]

multiple_cells = sheet['V4' : 'V51']
for value, row in enumerate(multiple_cells):
    for cell in row:
    	cell.value = times[value]
#End of inputting values


excel_document.save("../../../Data/Data.xlsx")