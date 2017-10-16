"""Analysis for type 2 forms"""
# Jonathan Slack
# jslackd@gmail.com

import numpy as np
import cv2
import os
from math import pi
import random
import sys
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
import collections
import re

import pdf_to_image

input_dir = "app_data"  # default: read images from os.path.join(input_dir, <filename>)
output_dir = "output"  # default: write images to os.path.join(output_dir, <filename>)

def scaleFloatToUint8(imagei,preserve):
# This function will scale and convert a float image channel to uint8 image channel
# preserve represents sensitivity to actual pixel values (i.e. if the max
# is below 255.0, we should not scale up to 255.0 if preserve == True 
    minb = np.min(imagei)
    if minb < 0:
        imagei = imagei + (-1.0*minb)
    elif minb > 0 and preserve == False:
        imagei = imagei - minb
   
    maxb = np.max(imagei)
    if maxb > 255.0 or preserve == False:
        imageo = np.multiply(imagei,(255.0/maxb))
    else:
        imageo = imagei
    return imageo.astype(np.uint8)  

def type2_process(fname, fwrap_path):
    # Declar file path to image
    folder_path = fwrap_path + "\\" + fname
    # Import image, convert to grayscale, and smooth image with a Gaussian kernel
    img2 =  cv2.imread(os.path.join(folder_path, "0.png"), 0) # 0 to ensure grayscale
    img2_smooth = cv2.GaussianBlur(img2,ksize=(3,131),sigmaX=0.8,sigmaY=31)
    ####img2_smooth = cv2.GaussianBlur(img2_smooth,(3,101),0)
    ####cv2.imwrite(os.path.join(output_dir, 'ps2-4-a-1.png'), img2_smooth)

    # Create an edge image for the smoothed image
    img2_edges = cv2.Canny(img2_smooth,0,300,2000,L2gradient=True)
    #####cv2.imwrite(os.path.join(output_dir, 'ps2-4-b-1.png'), img2_edges)

    # Opencv line detection
    min_line_len = int(np.shape(img2)[0]/66)
    max_line_gap = int(np.shape(img2)[0]/7)
    lines = []
    while len(lines) < 8:
        lines = cv2.HoughLinesP(img2_edges,1,np.pi/180,150,min_line_len,max_line_gap)

        # Error catch (lines empty)
        if lines is None:        
            lines = []
        # On each iteration, decrease max_line_gap
        max_line_gap_new = round(max_line_gap/2)

        # If there are simply no lines, exit
        if max_line_gap_new == max_line_gap:
            if lines == []:
                lines = [[[1,1,3,3]]] # arbitrary small line
            break
        # Otherwise, set the new max_line_gap
        else:
            max_line_gap = max_line_gap_new

    # Exception case where lines has a single entry
    if len(np.shape(lines)) == 1:
        lines = [[lines]]

    ## draw lines and output
    #imgout = np.ones((img2.shape[0],img2.shape[1],3),dtype=np.int8)*255

    #for line in lines[0:8]:
    #    for x1,y1,x2,y2 in line:
    #        cv2.line(imgout,(x1,y1),(x2,y2),(np.random.rand()*255,np.random.rand()*255,np.random.rand()*255),2) 
    #cv2.imwrite(os.path.join(output_dir, "test.png"), imgout)

    if type2_line_screen(lines,8,img2,fname) == True:
        if type2_text_screen(fname, os.path.join(folder_path, "0.png")) == True:
            #print(fname)
            return True
    
    return False

def type2_line_screen(lines,num_max,img,fname):
    # Helper function - finding vertical lines
    def vertORnot(x1,y1,x2,y2,img):
        dif = np.abs(x2-x1)
        cols = img.shape[1]

        factor_vert = 300
        if dif <= np.ceil(cols/factor_vert):
            return True
        else:
            return False
    # Helper function - determining if a line is long enough
    def long_enough(x1,y1,x2,y2,img):
        dist = np.sqrt((x2-x1)**2 + (y2-y1)**2)
        diagonal = np.sqrt((img.shape[0]-0)**2 + (img.shape[1]-0)**2)
        factor_long = 20
        if dist >= np.floor(diagonal/factor_long):
            return True
        else:
            return False

    # Collect data on lines
    vert_container = []
    length_container = []
    right_most_vert = 0

    for line in lines[0:num_max]:
        for x1,y1,x2,y2 in line:
            length_container.append(long_enough(x1,y1,x2,y2,img))
            orient = vertORnot(x1,y1,x2,y2,img)
            vert_container.append(orient)
            if orient == True:
                candidate = np.amax([x1,x2])
                if candidate > right_most_vert:
                    right_most_vert = candidate

    # Vertical Check
    if np.sum(vert_container) < 7:
        #print("-----")   
        #print("vertical fail " + fname)
        #print("-----")
        return False
    # Length Check
    if np.sum(length_container) < 1:
        #print("-----")
        #print("length fail " + fname)
        #print("-----")
        return False
    # Right-most Position Check
    if (img.shape[1] - right_most_vert)/np.float(img.shape[1]) > 0.50:
        #print("-----")
        #print("right-most fail " + fname)
        #print("-----")
        return False

    return True

def type2_text_screen(fname, path):
    # Read text using tesseract OCR
    imagein = Image.open(path)
    # First, crop the image into three snipets
    width, height = imagein.size
    imagein1 = imagein.crop((np.round(width/3).astype(int),np.round(height/15).astype(int),width,np.round(height/4).astype(int)))
    imagein2 = imagein.crop((np.round(width/3).astype(int)*2,np.round(height/15).astype(int),width,np.round(height/2).astype(int)))
    imagein3 = imagein.crop((np.round(width/3).astype(int),np.round(height/15).astype(int),width,np.round(height/2).astype(int)))

    # Apply median filter to the snipets
    imagein1 = imagein1.convert('L')
    imagein1 = imagein1.filter(ImageFilter.SHARPEN)
    imagein2 = imagein2.convert('L')
    imagein2 = imagein2.filter(ImageFilter.SHARPEN)
    imagein3 = imagein3.convert('L')
    imagein3 = imagein3.filter(ImageFilter.SHARPEN)

    ## Output images for analysis
    #imagein1.save(path + "crop1")
    #imagein2.save(path + "crop2")
    #imagein3.save(path + "crop3")

    tessdata_dir_config1 = '--tessdata-dir "C:\\Program Files (x86)\\Tesseract-OCR\\tessdata" -oem 2 -psm 3'
    tessdata_dir_config2 = '--tessdata-dir "C:\\Program Files (x86)\\Tesseract-OCR\\tessdata" -oem 2 -psm 3'
    tessdata_dir_config3 = '--tessdata-dir "C:\\Program Files (x86)\\Tesseract-OCR\\tessdata" -oem 2 -psm 3'

    text_read1 = pytesseract.image_to_string(imagein1, boxes = False, config=tessdata_dir_config1)
    text_read2 = pytesseract.image_to_string(imagein2, boxes = False, config=tessdata_dir_config2)
    text_read3 = pytesseract.image_to_string(imagein2, boxes = False, config=tessdata_dir_config3)

    if type2_text_score(text_read1) == True or type2_text_score(text_read2) == True or type2_text_score(text_read3) == True:
        return True
    else:
        #print("-----")
        #print("text screen fail " + fname)
        #print(text_read1)
        #print(text_read2)
        #print("-----")
        return False

def type2_text_score(text_in):
    # Must score 2 to pass
    score = 0

    # Test 1 --> "Time"
    if "Time" in text_in: 
        score += 1

    # Test 2 --> "Stamp"
    if "Stamp" in text_in: 
        score += 1

    # Test 3 --> "Plural"
    if "Plural" in text_in: 
        score += 1

    # Test 4 --> "OFF" or "ON"
    if "OFF" in text_in or "ON" in text_in:
        score += 1

    # Test 5 --> "Default"
    if "Default" in text_in:
        score += 1

    if score >= 2:
        return True
    else:
        return False

def extract_dates(filename):
    # Read text using tesseract OCR
    imagein = Image.open(filename)
    # First, crop the image into three snipets
    width, height = imagein.size
    imagein1 = imagein.crop((np.round(width/3).astype(int)*2,np.round(height/20).astype(int),width,np.round(height/20).astype(int)*19))
    imagein2 = imagein.crop((np.round(width/3).astype(int)*2 + 50,np.round(height/20).astype(int),width,np.round(height/20).astype(int)*19))
    imagein3 = imagein.crop((np.round(width/3).astype(int)*2 - 200,np.round(height/20).astype(int),width,np.round(height/20).astype(int)*19))

    # Apply median filter to the snipets
    imagein1 = imagein1.convert('L')
    imagein1 = imagein1.filter(ImageFilter.SHARPEN)
    imagein2 = imagein2.convert('L')
    imagein2 = imagein2.filter(ImageFilter.SHARPEN)
    imagein3 = imagein3.convert('L')
    imagein3 = imagein3.filter(ImageFilter.SHARPEN)

    ## Output images for analysis
    #imagein1.save(os.path.join(output_dir, "crop1_.png"))
    #imagein2.save(os.path.join(output_dir, "crop2_.png"))
    #imagein3.save(os.path.join(output_dir, "crop3_.png"))

    tessdata_dir_config1 = '--tessdata-dir "C:\\Program Files (x86)\\Tesseract-OCR\\tessdata" -oem 2 -psm 3'
    tessdata_dir_config2 = '--tessdata-dir "C:\\Program Files (x86)\\Tesseract-OCR\\tessdata" -oem 2 -psm 3'
    tessdata_dir_config3 = '--tessdata-dir "C:\\Program Files (x86)\\Tesseract-OCR\\tessdata" -oem 2 -psm 3'

    text_read1 = pytesseract.image_to_string(imagein1, boxes = False, config=tessdata_dir_config1)
    text_read2 = pytesseract.image_to_string(imagein2, boxes = False, config=tessdata_dir_config2)
    text_read3 = pytesseract.image_to_string(imagein2, boxes = False, config=tessdata_dir_config3)

    # Process pulled text from Type2 forms
    dates_in = txt_date_process([text_read1,text_read2,text_read3])
    dates_out = []
    if len(dates_in[0])==0 and len(dates_in[1])==0 and len(dates_in[2])==0:
        return dates_out

    # Find longest list
    longest = max(enumerate(dates_in), key = lambda tup: len(tup[1]))[0]
    if longest == 0: other1 = 1; other2 = 2
    if longest == 1: other1 = 0; other2 = 2
    if longest == 2: other1 = 0; other2 = 1

    # Must occur at least twice to stay
    for date in dates_in[longest]:
        if date in dates_in[other1] or date in dates_in[other2]:
            dates_out.append(date)

    for date in dates_in[other1]:
        if date not in dates_out:
            if date in dates_in[other2]:
                dates_out.append(date)

    for date in dates_in[other2]:
        if date not in dates_out:
            if date in dates_in[other1]:
                dates_out.append(date)

    #print(filename)
    #print(dates_out)
    
    return dates_out

def txt_date_process(text_in):
    proc = []
    sstring = re.compile("[eq0-9][0-9][0-9][0-9]/[0-9][0-9]/[0-9][0-9]")
    
    i = 0
    for text in text_in:
        text = text.replace(" /", "/")
        text = text.replace("/ ", "/")
        text = text.lower()

        positions = [m.start() for m in re.finditer(sstring, text)]
        positions_end = np.add(positions,10)
        dates_list = [text[i:j] for i,j in zip(positions, positions_end)]
        dates_list = [w.replace('e', '2') for w in dates_list]
        dates_list = [w.replace('q', '2') for w in dates_list]          
            
        proc.append(dates_list)

        i += 1
    
    return proc      
    
def recognize(app_info, fwrap_path):
    # Analyze images for Type2 form
    counter = 0
    for fname in app_info["SRNT_files"]:
        # Immediately throw out Type8-identified and Type-7 identifies forms
        typer = app_info["SRNT_type"][counter]
        if typer=="Type7" or typer=="Type7-Unreadable" or typer=="Type8" or typer=="Type8-Unreadable":
            counter += 1
            continue

        type_check = type2_process(fname,fwrap_path)

        # Identified as a Type2 form
        if type_check == True:
            app_info["SRNT_type"][counter] = "Type2"

        counter += 1

    return app_info

def read(info_pass,fwrap_path,filename):
    # Create image files for analysis of full pdfs
    pdf_to_image.main([filename],"all",fwrap_path)

    # Declare folder path
    folder_path = os.path.join(fwrap_path,filename)
    list_of_imgs = os.listdir(folder_path)

    for img_name in list_of_imgs:
        path = os.path.join(folder_path,img_name)
        dates = extract_dates(path)

        if dates == []:
            info_pass["SRNT_check"] = False

        info_pass["SRNT_dates"]["Type2"].extend(dates)

    return info_pass

