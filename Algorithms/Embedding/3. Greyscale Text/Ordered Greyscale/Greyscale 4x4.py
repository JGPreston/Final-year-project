from PIL import Image
import time
import numpy as np
import binascii
import os
import traceback
import re
import statistics
import collections
from collections import Counter

#Excel
import openpyxl

#Other directories
import sys 
sys.path.append("../../../Analysis/PSNR+SSIM/")
from PSNRSSIM import returnValues

#Matrix for Ordered dither
the_4x4 = np.array([[0,8,2,10],
					[12,4,14,6],
					[3,11,1,9],
					[15,7,13,5]])
the_4x4 = np.divide(the_4x4,16)
tiled =np.tile(the_4x4,(128,128))

length =8


def greyScale(image):
	imageArray = np.array(image, 'float64')			#Image to numpy array
	imageArray = np.divide(imageArray, 256)			#Divides image values by the range of pixel values. 256 for 8 bit images

	i,j = 0,0
	
	#Message to embed and conversion to binary
	message = "Why do programmers always mix up Halloween and Christmas?    Because 31 OCT = 25 DEC!"
	message = bin(int.from_bytes(message.encode('utf-8', 'surrogatepass'), 'big'))[2:]
	message = message.zfill(8*((len(message) + 7)//8))
	
	variableY=0
	counter =0
	for x in range(height):
		for y in range(0,width,length):			
			theGroup = imageArray[x,y:y+length]
				
		
			wcounter = len([i for i in halftoneValue(np.copy(theGroup),x,y) if i > 128]) 				#Count number of white pixels in the halftoned group
			
			c = length-2*wcounter 																	#Broadens the groups complexity value
			t = int((length*2)/5)																		#Defines the threshold to compare against the complexity
			
			
			if((0-t) <= float(c) <= 0+t):															#If the complexity is within the threshold
				if(j < len(message)):																#For iterating through the message
					ei = minimum_error(theGroup, message[j], length, c,t,x,y)							#Get the minimum error to change the greyscale values so that when halftoned, embeds the message bit
					embeddedGroup = [x+y for x,y in zip(theGroup,ei)]								#Creates a group for the combination of the selected group added with the error added

					wcounter1 = len([i for i in halftoneValue(np.copy(embeddedGroup),x,y) if i > 128])	#Count number of white pixels in the halftoned embedded group
					d = length-2*wcounter1															#Again, broadens the groups complexity value
				
					if((0-t) <= float(d) <= 0+t):													#If the new embedded group is within the complexity range...
						for g in range(0,length,1):
							imageArray[x,y+g] = embeddedGroup[g]									#Update the imageArray to store the greyscale values

						halftoneGroup(x,y,imageArray,length)				#Halftone the group

						j += 1																		#Iterate through the message by 1
					else:
						halftoneGroup(x,y,imageArray,length)				#Halftone the group

				else:
					halftoneGroup(x,y,imageArray,length)					#Halftone the group
					
					
			else:
				halftoneGroup(x,y,imageArray,length)						#Halftone the group
				
		
	return Image.fromarray(np.array(imageArray,'uint8'))


#Find the minimum change to embed the message
def minimum_error(theGroup, messageBit, length,c,t,x,y):
	eu, ed = [0]*length, [0]*length
	n = 1

	k = 0
	while((halftoneValue([x+y for x,y in zip(theGroup,eu)],x,y).count(255)) % (2**n) != int(messageBit)):		#While the number of white pixels from halftoning mod 2 is not equal to the message bit (1 or 0)
		eu[k] += 1																							#Add 1 to eu position k
		k = (k+1)%length 																					#Add 1 to k


	k = 0
	while(halftoneValue([x+y for x,y in zip(theGroup,ed)],x,y).count(255) % (2**n) != int(messageBit)):			#While the number of white pixels from halftoning mod 2 is not equal to the message bit (1 or 0)
		ed[k] -= 1																							#Take away 1 from ed position k
		k = (k+1)%length 																					#Add 1 to k


	for counter, value in enumerate(eu):		#Go through eu's values and compare them against ed. Whichever is smallest gets assigned to be returned
		if(value < abs(ed[counter])):
			ei = eu
			#return eu
		else:
			ei = ed
			#return ed

	embeddedGroup = [x+y for x,y in zip(theGroup,ei)]
	wcounter1 = len([i for i in halftoneValue(np.copy(embeddedGroup),x,y) if i > 128])
	d = length-2*wcounter1

	if((0-t) <= float(d) <= 0+t):				#If the complexity value is within the threshold...
		return ei  								#Return the error variance
	else:										#If not...
		for counter, value in enumerate(eu):	#Iterate through eu and return ed
			if(value < abs(ed[counter])):
				ei = ed
			else:
				ei = eu

	return ei


#Halftone value is what the group halftone values are
def halftoneValue(theGroup,x,y):
	for i in range(0, len(theGroup)):
		theGroup[i] = (255 if (theGroup[i]>tiled[x,y]) else 0)
		y+=1

	return theGroup


#Halftone group is halftoning the group and distrubuting to other pixels 
def halftoneGroup(x,y,imageArray, length):
	for i in range(0, length):
		imageArray[x,y] = (255 if (imageArray[x,y]>tiled[x,y]) else 0)
		y+=1

	return imageArray


#Extract the message from the embedded halftoned image
def extraction(image):
	imageArray = np.array(image, 'float64')								#Image to array							
	message = []

	for x in range(height):
		for y in range(0,width,length):
			theGroup = imageArray[x,y:y+length]							#Select the group
		
			wcounter = len([i for i in theGroup if i > 128]) 			#Number of white pixels in the group

			c = length-2*wcounter 										#Broaden the complexity value
			t = int((length*2)/5)											#Threshold
			n = 1
			
			if((0-t) <= float(c) <= 0+t):								#If the complexity is within the threshold
				
				messageBit = wcounter % (2**n)							#Get a 1 or a 0 from the white number count
				message.append(str(messageBit))							#Add the bit to the message list
	

	extractedMessage = ''.join(message)									#Join the extracted bits together
	finalMessage =[]
	for i in range(0, len(extractedMessage), 8):						#For every 8 bits (makes a character)
		message = int(extractedMessage[i:i+8],2)
		character = message.to_bytes((message.bit_length() + 7)//8, 'big').decode('utf-8', 'ignore')		#Convert to ASCII
		if(re.match(r'[\w ?=]+', character)):							#If the character is part of the regex
			finalMessage.append(character)								#Add it to the final message list
	print(''.join(finalMessage)[:84])	
	print()
	analyse(finalMessage)												#Analyse the final message


def analyse(decryptMessage):
	message = "Why do programmers always mix up Halloween and Christmas?    Because 31 OCT = 25 DEC!"		#Original message
	message = list(message)																					#Make the original message a list

	value = 0
	for item in message:
		if item in decryptMessage:						#Compare the two lists
			value +=1

	messagePercents.append(((value/84)*100))			#Get percentage of extracted message against the original message



embedTimes = []
decryptTimes = []
psnrValues = []
ssimValues = []
messagePercents = []


#Processes every file in the original images folder
fileList = []
for file in os.listdir("../../../Images/Original/"):
	fileList.append(file[:-4])							#Remove the file extension so
fileList = sorted(fileList, key=int)					#it can be sorted by int

for file in fileList:									#For every file in the sorted file list
	filename = os.fsdecode(file)
	filename+=".png"									#Add png file extension. Converts any file format to png
	

	image = Image.open("../../../Images/Original/"+filename)									#Open file to embed											
	original = Image.open("../../../Images/Basic Halftone/Ordered/4x4/"+filename)		#For comparing against original
	print(filename)

	height, width = image.size
	start_time = time.time()
	imageConverted = greyScale(image)
	embedTime = time.time() - start_time
		
	imageConverted.save("../../../Images/Embedded/3. Greyscale Text/Ordered/4x4/"+filename)


	imageDecode = Image.open("../../../Images/Embedded/3. Greyscale Text/Ordered/4x4/"+filename)
	start_time = time.time()
	extraction(imageDecode)
	decryptTime = time.time() - start_time

	psnr, ssim = returnValues(original,imageConverted)		#Send original and processed image to get PSNR and SSIM values
	psnrValues.append(psnr)
	ssimValues.append(ssim)
	embedTimes.append(embedTime)
	decryptTimes.append(decryptTime)


excel_document = openpyxl.load_workbook("../../../../Data/Data.xlsx")	#Open excel
sheet = (excel_document['Greyscale Embed'])								#Selects sheet

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