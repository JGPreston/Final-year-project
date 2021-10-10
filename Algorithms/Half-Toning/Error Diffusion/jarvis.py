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

#Map for Jarvis error diffusion
jarvisMap = (
        (1, 0,  7 / 48),	# Position [y, x], weighting
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

def convert_halftoning(image):
	width, height = image.size
	image = np.array(image, 'float64')									#Image to numpy array
	for x in range(height):					
		for y in range(width):
			old_pixel = image[x,y]
			new_pixel = (255 if old_pixel >= 127 else 0)
			quant_err = old_pixel-new_pixel
			image[x, y] = new_pixel
			for ypos, xpos, weighting in jarvisMap:						#For every element in the matrix
				newx, newy = x + xpos, y + ypos							#For every neighbouring pixel defined by the matrix
				if (0 <= newx < height) and (0 <= newy < width):			#Check whether the new x and y positions are still valid
					image[newx, newy] += (quant_err * weighting)		#If so, diffuse the error
				
					
	return Image.fromarray(np.array(image, 'uint8')) 					#Return image from the numpy array


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
		
	imageConverted.save("../../Images/Basic Halftone/Error Diffusion/Jarvis/"+filename)

	psnr, ssim = returnValues(original,imageConverted)											#Send original and processed image to get PSNR and SSIM values
	psnrValues.append(psnr)
	ssimValues.append(ssim)
	times.append(finalTime)
	

excel_document = openpyxl.load_workbook("../../../Data/Data.xlsx")		#Open excel 
sheet = (excel_document['Basic Halftone'])								#Selects sheet

#Input values to the sheet. 
multiple_cells = sheet['G4' : 'G51']
for value, row in enumerate(multiple_cells):
    for cell in row:
    	cell.value = psnrValues[value]

multiple_cells = sheet['H4' : 'H51']
for value, row in enumerate(multiple_cells):
    for cell in row:
    	cell.value = ssimValues[value]

multiple_cells = sheet['I4' : 'I51']
for value, row in enumerate(multiple_cells):
    for cell in row:
    	cell.value = times[value]
#End of inputting values

excel_document.save("../../../Data/Data.xlsx")