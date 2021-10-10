from PIL import Image
import time
import numpy as np
import binascii
import os
import traceback
import re
import statistics
import collections
import matplotlib.pyplot as plt 
from collections import Counter

#Excel
import openpyxl

#Add path to directory
import sys 
sys.path.append("../../../Analysis/PSNR+SSIM/")
from PSNRSSIM import returnValues


#Variable threshold
blockSize = 4
sizeDifference = 1


#Main encoding section to access various parts to the encoding stage
def encoding(image):
	message = "Why do programmers always mix up Halloween and Christmas?    Because 31 OCT = 25 DEC!"

	originalImage = np.array(image, 'float64')							#Stores the original image to numpy array. Used later to compare what has changed
	imageArray = np.array(image, 'float64')								#Image to numpy array
	blockPixels, density = getBlocks(imageArray)						#Get the block pixels (threshold)x(threshold)

	#Histogram of densities
	#histogram(density)													#Density histogram
	
	embeddedBlocks = checkBlocksAndEmbed(blockPixels,density, message)	#Creates blocks that contains part of the message

	#Put created blocks into image
	replaceBlocks(embeddedBlocks, imageArray, originalImage)			#Replace the image blocks with the embedded blocks
	
	return Image.fromarray(np.array(imageArray, 'uint8'))				#Return image from the numpy array


#Uses the image parsed in and splits it into blocks determined by the block size
def getBlocks(imageArray):
	blockPixels = []
	density = []

	for x in range(0, height,blockSize):					#Iterate through the image in the size of the block
		for y in range(0, width,blockSize):
			pixels = []
			for a in range(blockSize):						#Get the block size section of x,y coordinates	
				for b in range(blockSize):
					pixels.append(imageArray[x+a,y+b])
			blockPixels.append(pixels)
			density.append(pixels.count(0))					#The amount of black pixels in the block
	return(blockPixels,density)								#Return the image in seperate blocks and return corresponding density list



#Check blocks densities and embed when a block matches a density
def checkBlocksAndEmbed(blockPixels, density, message):
	densityValue = density_selection(density)												#Get two densities to embed to from the densities obtained during the blocking process
	print("Embedding densities: " + str(densityValue))
	#histogram(density)
	message = bin(int.from_bytes(message.encode('utf-8', 'surrogatepass'), 'big'))[2:]		#Message to binary
	message = message.zfill(8*((len(message) + 7)//8))										#Fill in binary to make it 8 bits for 1 character

	#totalDensityCount = density.count(densityValue[0]) + density.count(densityValue[1])
	
	
	binaryCounter = 0
	for counter, value in enumerate(blockPixels):											#For every block
		if(density[counter] == densityValue[0] or density[counter]== densityValue[1]):		#Check if the density of the block is one of the two returned
			if(binaryCounter < len(message)):												#Only embed until the total length of the message is embedded
				blockPixels[counter] = messageEmbed(value, int(message[binaryCounter]), density[counter], densityValue, counter)	#Update the block (position is controlled with counter) with the embedded message block
				binaryCounter+=1															#Add 1 to the binaryCounter so the next character in the message is embedded
	return blockPixels																		#Return the newly made blockPixels 


#Replace original image blocks with the created embedded blocks
def replaceBlocks(embeddedBlock, imageArray, originalImage):
	original,density = getBlocks(originalImage)										#Original image into blocks (so comparisons can be made)

	counter = 0																		#To iterate through the original blocks and the embedded blocks (comparisons)
	for x in range(0,height,blockSize):
		for y in range(0,width,blockSize):
			if(embeddedBlock[counter] != original[counter]):						#If the original block isn't the same as the embedded one...
				counter1=0
				for a in range(blockSize):
					for b in range(blockSize):
						imageArray[x+a,y+b] = embeddedBlock[counter][counter1]		#Update the image to contain the embedded blocks values
						counter1+=1
			counter += 1
	return imageArray																#Return the image


#Embed the message into the block
def messageEmbed(value,toEmbed,density, densityValue, counter):
	lower = densityValue[0]
	higher = densityValue[1]
	if((density == lower and toEmbed == 0) or (density == higher and toEmbed == 1)):	#If the message bit to embed is 0 and the density value is lower or the message bit is 1 and the density value is higher, return an unaltered block
		return(value)

		
	if(density == lower and toEmbed == 1):			#If the message bit to embed is 1 and the density value is lower, update the density to the higher one
		for j in range(0,sizeDifference):
			for counter,i in enumerate(value):
				if i == 255:
					value[counter] = 0
					break
		return(value)

	if(density == higher and toEmbed == 0):			#If the message bit to embed is 0 and the density is higher, update the density to the lower one
		for j in range(0,sizeDifference):
			for counter,i in enumerate(value):
				if i == 0:
					value[counter] = 255
					break
		return(value)
	

#Shows the density values in the image
def histogram(density):
	labels, counts = np.unique(density,return_counts=True)							#Labels and counts are a sum of the values from density
	ticks = range(len(counts))														#The axis is a range of the total count
	plt.bar(ticks,counts, align='center', label="Num of black pixels per block")	#Plot bars
	plt.xticks(ticks, labels)														#Axis labels
	plt.legend()																	#Plot the legend

	plt.show()			


#Selects two density values close to the mean of the densities
def density_selection(lst):
	lst = sorted(lst, key=int)
	mean = Counter(lst).keys() # equals to list(set(words))
	meanCalc = 0
	for i in mean:
		meanCalc += i
	mean = int(np.ceil((meanCalc/len(set(lst)))))

	plusMean = abs(lst.count(mean+sizeDifference) - lst.count(mean))
	minusMean =  abs(lst.count(mean-sizeDifference) - lst.count(mean))

	#Returns the lowest difference densities between the mean and the two densities either side
	if(plusMean > minusMean):
		return(mean-sizeDifference, mean)
	else:
		return(mean, mean+sizeDifference)


#To extract the message from the embedded image
def decode(decodeImage):
	decodeImage = np.array(decodeImage, 'float64')							#Image to numpy array

	blockPixels,density = getBlocks(decodeImage)							#Get the image into blocks and obtain density values

	densityValue = density_selection(density)								#Get the two densities to be used from the densities list
	print("Extraction densities:" + str(densityValue))
	extractedMessage = []
	for counter, value in enumerate(blockPixels):							#Iterate through the blocks
		if(density[counter] == densityValue[0]):							#If the density of the block matches the lower density value, append a 0 to the extracted message
			extractedMessage.append('0')
		elif(density[counter] == densityValue[1]):							#If the density of the block matches the higher density value, append a 1 to the extracted message
			extractedMessage.append('1')

	extractedMessage = ''.join(extractedMessage)							#Combine all of the 1's and 0's into a string
	finalMessage =[]
	for i in range(0, len(extractedMessage), 8):							#Iterate through the extracted message 8 bits at a time					
		message = int(extractedMessage[i:i+8],2)
		character = message.to_bytes((message.bit_length() + 7)//8, 'big').decode('utf-8', 'ignore')	#Convert the 8 bits into a character
		if(re.match(r'[\w ?=]+', character)):								#Regex so that only characters, numbers and select symbols are converted to characters and stored
			finalMessage.append(character)									#Append the character that passed the regex criteria
	print(''.join(finalMessage)[:84])										
	print()
	analyse(finalMessage)													#Send extracted message to be analysed against the original


def analyse(decryptMessage):
	message = "Why do programmers always mix up Halloween and Christmas?    Because 31 OCT = 25 DEC!"		#Original message
	message = list(message)																					#to list

	value = 0
	for item in message:
		if item in decryptMessage:
			value +=1								#Every time the characters match in the original and extracted list, add 1.

	#print((value/84)*100)
	messagePercents.append(((value/84)*100))		#As the original message  


embedTimes = []
decryptTimes = []
psnrValues = []
ssimValues = []
messagePercents = []

fileList = []
for file in os.listdir("../../../Images/Basic Halftone/Ordered/8x8/"):
	fileList.append(file[:-4])															#Remove the file extension so 
fileList = sorted(fileList, key=int)													#it can be sorted by int

for file in fileList:						#For every file in the sorted file list	
	filename = os.fsdecode(file)
	filename+=".png"						#Add png file extension. Converts any file format to png 
	
	image = Image.open("../../../Images/Basic Halftone/Ordered/8x8/"+filename)			#Open halftoned image
	original = Image.open("../../../Images/Basic Halftone/Ordered/8x8/"+filename)		#For comparing

	height, width = image.size
	print(filename)


	start_time = time.time()
	imageConverted = encoding(image)
	embedTime = time.time() - start_time
		
	imageConverted.save("../../../Images/Embedded/2. Density Text/Ordered/8x8/"+filename)


	imageDecode = Image.open("../../../Images/Embedded/2. Density Text/Ordered/8x8/"+filename)
	start_time = time.time()
	decode(imageDecode)
	decryptTime = time.time() - start_time

	psnr, ssim = returnValues(original,imageConverted)
	psnrValues.append(psnr)
	ssimValues.append(ssim)
	embedTimes.append(embedTime)
	decryptTimes.append(decryptTime)




excel_document = openpyxl.load_workbook("../../../../Data/Data.xlsx")	#Open excel
sheet = (excel_document['Density Embed'])								#Selects sheet

#Input values to the sheet
multiple_cells = sheet['AD4' : 'AD51']
for value, row in enumerate(multiple_cells):
    for cell in row:
    	cell.value = psnrValues[value]

multiple_cells = sheet['AE4' : 'AE51']
for value, row in enumerate(multiple_cells):
    for cell in row:
    	cell.value = ssimValues[value]

multiple_cells = sheet['AF4' : 'AF51']
for value, row in enumerate(multiple_cells):
    for cell in row:
    	cell.value = embedTimes[value]

multiple_cells = sheet['AG4' : 'AG51']
for value, row in enumerate(multiple_cells):
    for cell in row:
    	cell.value = decryptTimes[value]

multiple_cells = sheet['AH4' : 'AH51']
for value, row in enumerate(multiple_cells):
    for cell in row:
    	cell.value = messagePercents[value]
#End of inputting values


excel_document.save("../../../../Data/Data.xlsx")
