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
skip = 1

#Main encoding section to access various parts to the encoding stage
def encoding(image):
	message = "Why do programmers always mix up Halloween and Christmas?    Because 31 OCT = 25 DEC!"
	message = bin(int.from_bytes(message.encode('utf-8', 'surrogatepass'), 'big'))[2:]		#Message to binary
	message = message.zfill(8*((len(message) + 7)//8))										#Fill in binary to make it 8 bits for 1 character
	imageArray = np.array(image, 'float64')													#Image to numpy array
	
	j = 0
	for x in range(0,height, skip):
		for y in range(0,width, skip):														#Iterate through the image depending on the skip size 
			if j < len(message):															#Embed for the entire message

				if(float(message[j]) != imageArray[x,y]/255):								#If the message bit to embed isn't the same value as the image pixel
					if(message[j] == "0" and imageArray[x,y] == 255.0):						#Change it to match...
						imageArray[x,y] = 0.0

					elif(message[j] == "1" and imageArray[x,y] == 0.0):
						imageArray[x,y] = 255.0
					
					j+=1		#Go to next message bit
				else:
					j+=1		#If the values are equal, go to the next message bit
			
			
	return Image.fromarray(np.array(imageArray, 'uint8'))									#Return image from the numpy array



#To extract the message from the embedded image
def decode(decodeImage):
	decodeImage = np.array(decodeImage, 'float64')							#Image to numpy array
	
	extractedMessage = []
	for x in range(0,height,skip):
		for y in range(0,width,skip):
			messageBit = decodeImage[x,y]
			if messageBit == 0:
				extractedMessage.append('0')
			elif messageBit == 255:
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
for file in os.listdir("../../../Images/Basic Halftone/Ordered/4x4/"):
	fileList.append(file[:-4])															#Remove the file extension so 
fileList = sorted(fileList, key=int)													#it can be sorted by int

for file in fileList:						#For every file in the sorted file list	
	filename = os.fsdecode(file)
	filename+=".png"						#Add png file extension. Converts any file format to png 
	
	image = Image.open("../../../Images/Basic Halftone/Ordered/4x4/"+filename)				#Open halftoned image
	original = Image.open("../../../Images/Basic Halftone/Ordered/4x4/"+filename)				#For comparing

	height, width = image.size
	print(filename)


	start_time = time.time()
	imageConverted = encoding(image)
	embedTime = time.time() - start_time
		
	imageConverted.save("../../../Images/Embedded/1. Basic Text/Ordered/4x4/"+filename)


	imageDecode = Image.open("../../../Images/Embedded/1. Basic Text/Ordered/4x4/"+filename)
	start_time = time.time()
	decode(imageDecode)
	decryptTime = time.time() - start_time

	psnr, ssim = returnValues(original,imageConverted)
	psnrValues.append(psnr)
	ssimValues.append(ssim)
	embedTimes.append(embedTime)
	decryptTimes.append(decryptTime)




excel_document = openpyxl.load_workbook("../../../../Data/Data.xlsx")	#Open excel
sheet = (excel_document['Basic Pixel Embed'])								#Selects sheet

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