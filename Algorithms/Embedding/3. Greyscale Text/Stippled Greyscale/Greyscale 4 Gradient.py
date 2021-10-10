from PIL import Image
import time
import numpy as np
import binascii
import os
import traceback
import cv2
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

gradient0 = Image.open("Gradients/stipple0.png")
gradient0 = np.array(gradient0, 'float64')

gradient2 = Image.open("Gradients/stipple2.png")
gradient2 = np.array(gradient2, 'float64')

gradient4 = Image.open("Gradients/stipple4.png")
gradient4 = np.array(gradient4, 'float64')

gradient6 = Image.open("Gradients/stipple6.png")
gradient6 = np.array(gradient6, 'float64')

length =8

def greyScale(image):
	imageArray = np.array(image, 'float64')
	imageArray = cv2.GaussianBlur(imageArray,(9,9),0)



	i,j = 0,0
	
	#print(imageList)
	message = "Why do programmers always mix up Halloween and Christmas?    Because 31 OCT = 25 DEC!"
	message = bin(int.from_bytes(message.encode('utf-8', 'surrogatepass'), 'big'))[2:]
	message = message.zfill(8*((len(message) + 7)//8))
	#print(height,width)
	variableY=0
	counter =0
	for x in range(height):
		for y in range(variableY,width,length):
			#print(x,y)
			if((x == height-1) and (y+length > width)):
				theGroup = imageArray[x,y:y+(width-y)]

			elif(y+length <= width):
				theGroup = imageArray[x,y:y+length]
				variableY=0
		
			elif(y+length > width):
				theGroup = np.append(imageArray[x,y:y+(width-y)],imageArray[x+1,0:(length-(width-y))])
				variableY = length-(width-y)

			#Halftone values of the greyscale group selected
			wcounter = len([i for i in halftoneValue(np.copy(theGroup),x,y) if i > 128]) 
			
			c = length-2*wcounter 
			t = int((length*2)/5)
			
			if((0-t) <= float(c) <= 0+t):
				if(j < len(message)):
					ei = minimum_error(theGroup, message[j], length, c,t,x,y)
					embeddedGroup = [x+y for x,y in zip(theGroup,ei)]

					wcounter1 = len([i for i in halftoneValue(np.copy(embeddedGroup),x,y) if i > 128])
					d = length-2*wcounter1
				
					if((0-t) <= float(d) <= 0+t):
						for g in range(0,length,1):
							imageArray[x,y+g] = embeddedGroup[g]

						halftoneGroup(x,y,imageArray,length)

						j += 1
					else:
						halftoneGroup(x,y,imageArray,length)

				else:
					halftoneGroup(x,y,imageArray,length)
					
					
			else:
				halftoneGroup(x,y,imageArray,length)
				
		
	imageConverted = Image.fromarray(np.array(imageArray,'uint8'))
	return imageConverted

def minimum_error(theGroup, messageBit, length,c,t,x,y):
	eu, ed = [0]*length, [0]*length
	n = 1

	k = 0
	while((halftoneValue([x+y for x,y in zip(theGroup,eu)],x,y).count(255)) % (2**n) != int(messageBit)):
		eu[k] += 1
		k = (k+1)%length


	k = 0
	while(halftoneValue([x+y for x,y in zip(theGroup,ed)],x,y).count(255) % (2**n) != int(messageBit)):
		ed[k] -= 1
		k = (k+1)%length
		


	for counter, value in enumerate(eu):
		if(value < abs(ed[counter])):
			ei = eu
			#return eu
		else:
			ei = ed
			#return ed

	embeddedGroup = [x+y for x,y in zip(theGroup,ei)]
	wcounter1 = len([i for i in halftoneValue(np.copy(embeddedGroup),x,y) if i > 128])
	d = length-2*wcounter1

	if((0-t) <= float(d) <= 0+t):
		return ei
	else:
		for counter, value in enumerate(eu):
			if(value < abs(ed[counter])):
				ei = ed
			else:
				ei = eu

	return ei

def halftoneValue(theGroup,x,y):
	for i in range(0,len(theGroup)):
		if(0 <= theGroup[i] <= (255/4)*1):
			theGroup[i] = gradient0[x][y]
		elif((255/4)*1  <= theGroup[i] <= (255/4)*2):
			theGroup[i] = gradient2[x][y]
		elif((255/4)*2 <= theGroup[i] <= (255/4)*3):
			theGroup[i] = gradient4[x][y]
		elif((255/4)*3 <= theGroup[i] <= 255):
			theGroup[i] = gradient6[x][y]
		y+=1

	return theGroup


def halftoneGroup(x,y,imageArray, length):
	for i in range(0,length):
		if(0 <= imageArray[x][y] <= (255/4)*1):
			imageArray[x][y] = gradient0[x][y]
		elif((255/4)*1  <= imageArray[x][y] <= (255/4)*2):
			imageArray[x][y] = gradient2[x][y]
		elif((255/4)*2 <= imageArray[x][y] <= (255/4)*3):
			imageArray[x][y] = gradient4[x][y]
		elif((255/4)*3 <= imageArray[x][y] <= 255):
			imageArray[x][y] = gradient6[x][y]
		y+=1

	return imageArray


def extraction(image):
	imageArray = np.array(image, 'float64')
	message = []

	variableY=0
	for x in range(height):
		for y in range(variableY,width,length):
			if((x == height-1) and (y+length > width)):
				theGroup = imageArray[x,y:y+(width-y)]

			elif(y+length <= width):
				theGroup = imageArray[x,y:y+length]
				variableY=0
		
			elif(y+length > width):
				theGroup = np.append(imageArray[x,y:y+(width-y)],imageArray[x+1,0:(length-(width-y))])
				variableY = length-(width-y)


			wcounter = len([i for i in theGroup if i > 128]) 

			c = length-2*wcounter 
			t = int((length*2)/5)
			n = 1
			#print(x,y)	
			if((0-t) <= float(c) <= 0+t):
				#print(x,y,c)
				#print(wcounter)
				messageBit = wcounter % (2**n)
				message.append(str(messageBit))
	

	extractedMessage = ''.join(message)
	#print(message)
	finalMessage =[]
	for i in range(0, len(extractedMessage), 8):
		message = int(extractedMessage[i:i+8],2)
		#print(message.to_bytes((message.bit_length() + 7)//8, 'big').decode('utf-8', 'ignore') or '\0')
		character = message.to_bytes((message.bit_length() + 7)//8, 'big').decode('utf-8', 'ignore')
		if(re.match(r'[\w ?=]+', character)):
			finalMessage.append(character)
	print(''.join(finalMessage)[:84])	
	print()
	analyse(finalMessage)												#Analyse the final message

def analyse(decryptMessage):
	message = "Why do programmers always mix up Halloween and Christmas?    Because 31 OCT = 25 DEC!"
	#decryptMessage = ''.join(decryptMessage[:84])
	message = list(message)

	value = 0
	for item in message:
		if item in decryptMessage:
			#print(item)
			value +=1

	messagePercents.append(((value/84)*100))


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
	if filename.endswith(".png") or filename.endswith(".jpg") or filename.endswith(".gif"): 
		# print(os.path.join(directory, filename))
		image = Image.open("../../../Images/Original/"+filename)
		height, width = image.size
		original = Image.open("../../../Images/Basic Halftone/Stippled/4 Gradient/"+filename)
		print(filename)

		start_time = time.time()
		imageConverted = greyScale(image)
		embedTime = time.time() - start_time
		
		imageConverted.save("../../../Images/Embedded/3. Greyscale Text/Stippled/4 Gradient/"+filename)


		imageDecode = Image.open("../../../Images/Embedded/3. Greyscale Text/Stippled/4 Gradient/"+filename)
		start_time = time.time()
		extraction(imageDecode)
		decryptTime = time.time() - start_time

		psnr, ssim = returnValues(original,imageConverted)
		psnrValues.append(psnr)
		ssimValues.append(ssim)
		embedTimes.append(embedTime)
		decryptTimes.append(decryptTime)
		continue
	else:
		continue



excel_document = openpyxl.load_workbook("../../../../Data/Data.xlsx")
sheet = (excel_document['Greyscale Embed'])

multiple_cells = sheet['AO4' : 'AO51']
for value, row in enumerate(multiple_cells):
    for cell in row:
    	cell.value = psnrValues[value]

multiple_cells = sheet['AP4' : 'AP51']
for value, row in enumerate(multiple_cells):
    for cell in row:
    	cell.value = ssimValues[value]

multiple_cells = sheet['AQ4' : 'AQ51']
for value, row in enumerate(multiple_cells):
    for cell in row:
    	cell.value = embedTimes[value]

multiple_cells = sheet['AR4' : 'AR51']
for value, row in enumerate(multiple_cells):
    for cell in row:
    	cell.value = decryptTimes[value]

multiple_cells = sheet['AS4' : 'AS51']
for value, row in enumerate(multiple_cells):
    for cell in row:
    	cell.value = messagePercents[value]


excel_document.save("../../../../Data/Data.xlsx")