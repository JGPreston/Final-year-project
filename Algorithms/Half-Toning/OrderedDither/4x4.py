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
	#Matrix for 2x2 Ordered
	the_4x4 = np.array([[0,8,2,10],
						[12,4,14,6],
						[3,11,1,9],
						[15,7,13,5]])


	image = np.array(image, 'float64') 								#Image to numpy array
	image = np.divide(image, 256)									#Divides image values by the range of pixel values. 256 for 8 bit images

	the_4x4 = np.divide(the_4x4,16)									#Divide the matrix by size
	tiled = np.tile(the_4x4,(128,128))								#So the matrix spans the entire image
	
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
		
	imageConverted.save("../../Images/Basic Halftone/Ordered/4x4/"+filename)

	psnr, ssim = returnValues(original,imageConverted)											#Send original and processed image to get PSNR and SSIM values
	psnrValues.append(psnr)
	ssimValues.append(ssim)
	times.append(finalTime)
	

excel_document = openpyxl.load_workbook("../../../Data/Data.xlsx")		#Open excel 
sheet = (excel_document['Basic Halftone'])								#Selects sheet

#Input values to the sheet
multiple_cells = sheet['Q4' : 'Q51']
for value, row in enumerate(multiple_cells):
    for cell in row:
    	cell.value = psnrValues[value]

multiple_cells = sheet['R4' : 'R51']
for value, row in enumerate(multiple_cells):
    for cell in row:
    	cell.value = ssimValues[value]

multiple_cells = sheet['S4' : 'S51']
for value, row in enumerate(multiple_cells):
    for cell in row:
    	cell.value = times[value]
#End of inputting values


excel_document.save("../../../Data/Data.xlsx")




