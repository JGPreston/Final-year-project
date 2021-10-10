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

skip = 4

def watermark(image):
	imageArray = np.array(image, 'float64')									#Image to numpy array

	#Bottom half of the image
	for x in range(0,int(height/2),skip):
		for y in range(0,width,skip):
			if imageToHide[x,y] != imageArray[int(height/2)+x,y]:
				if imageToHide[x,y] == 0 and imageArray[int(height/2)+x,y] == 255:
					imageArray[int(height/2)+x,y] = 0
		
	return Image.fromarray(np.array(imageArray, 'uint8'))

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
for file in os.listdir("../../../Images/Basic Halftone/Ordered/4x4/"):
	fileList.append(file[:-4])
fileList = sorted(fileList, key=int)

for file in fileList:
	filename = os.fsdecode(file)
	filename+=".png"
	
	image = Image.open("../../../Images/Basic Halftone/Ordered/4x4/"+filename)
	width, height = image.size
	original = Image.open("../../../Images/Basic Halftone/Ordered/4x4/"+filename)
	imageToHide = np.array(Image.open("../Image To Hide/toHide.png"), 'float64')

	print(filename)
		
	start_time = time.time()
	imageConverted = watermark(image)
	embedTime = time.time() - start_time
	imageConverted.save("../../../Images/Embedded/4. Basic Watermark/Ordered/4x4/"+filename)


	toAnalyse = Image.open("../../../Images/Embedded/4. Basic Watermark/Ordered/4x4/"+filename)
	
	psnr, ssim = returnValues(original,imageConverted)		#Send original and processed image to get PSNR and SSIM values
	psnrValues.append(psnr)
	ssimValues.append(ssim)
	embedTimes.append(embedTime)
	decryptTimes.append("N/A")
	messagePercents.append(analyse(toAnalyse))




excel_document = openpyxl.load_workbook("../../../../Data/Data.xlsx")	#Open excel
sheet = (excel_document['Basic Watermark'])							#Selects sheet


#Input values to the sheet
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
