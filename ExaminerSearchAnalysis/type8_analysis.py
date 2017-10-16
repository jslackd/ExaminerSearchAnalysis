"""Analysis for type 8 forms"""
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
import re

import pdf_to_image

input_dir = "input"  # default input path

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

def image_process(fname,fwrap_path):
    # Read text using tesseract OCR
    imagein = Image.open(os.path.join(fwrap_path, fname, "0.png"))
    width, height = imagein.size
    imagein = imagein.crop((0,0,width,np.round(height/3).astype(int)))
    imagein = imagein.filter(ImageFilter.MedianFilter())
    tessdata_dir_config = '--tessdata-dir "C:\\Program Files (x86)\\Tesseract-OCR\\tessdata" -oem 2 -psm 3'    
    text_read = pytesseract.image_to_string(imagein, config=tessdata_dir_config)

    # Screen for Type8 forms
    if type8_text_score(text_read) == False:
        #print("---failure----" + fname)
        return False, False
    else:
        # Extract text from Type8 form [can be False value]
        list_of_files = os.listdir(os.path.join(fwrap_path, fname))
        last_file = list_of_files[-1]
        # Read text using tesseract OCR
        imagein1 = Image.open(os.path.join(fwrap_path, fname, last_file))
        width, height = imagein.size
        #imagein1 = imagein1.filter(ImageFilter.MedianFilter())
        tessdata_dir_config = '--tessdata-dir "C:\\Program Files (x86)\\Tesseract-OCR\\tessdata" -oem 2 -psm 3'    
        text_read1 = pytesseract.image_to_string(imagein1, config=tessdata_dir_config)     

        date = type8_extract_text(text_read1)
        return True, date

def type8_text_score(text_in):
    # Must score 2 to pass
    score = 0

    # Test 1 --> "STN International"
    if "STN International" in text_in: score += 1

    # Test 2 --> "Welcome to STN"
    if "Welcome to STN" in text_in: score+= 1

    # Test 3 --> "Winsock"
    if "Winsock" in text_in and "SIRA" in text_in: score += 1

    if score >= 2:
        return True
    else:
        return False

def type8_extract_text(text_in):
    # Extract date from Type8 form
    text_in = text_in.replace(" ","")
    # Pair down string length
    exit_cond = 0
    text_reverse = text_in[::-1].lower()
    for term in ["logoff", "international", "stn"]:
        term_reverse = term[::-1]
        snip_pos = text_reverse.find(term_reverse)

        if snip_pos != -1:
            exit_cond = 1
            break

    # Unsearchable, return False value
    if exit_cond == 0: return False

    # We found one of the terms, continue analysis
    text_in = text_in[((-1*snip_pos)-1):].lower()
    sbstr1 = re.compile(':[0-9][0-9]on')
    sbstr1_found = re.findall(sbstr1,text_in)
    
    if len(sbstr1_found) == 0:
        return False
    else:
        sbstr1_found = sbstr1_found[0]
        index1 = text_in.find(sbstr1_found)
        try:
            day = text_in[index1+5:index1+7]
            month = text_in[index1+7:index1+10]
            year = text_in[index1+10:index1+14]
        except:
            return False
        
        date = translate_date(month,day,year)

    return date

def translate_date(month_in, day, year):
    # Translate Type7 date into standard date
    months = {"jan":"01", "feb":"02", "mar":"03", "apr":"04", "may":"05", "jun":"06",
                "jul":"07", "aug":"08", "sep":"09", "oct":"10", "nov":"11","dec":"12"}

    try: month = months[month_in]
    except KeyError:
        return False

    return year + "/" + month + "/" + day

def recognize_and_rip(app_info, fwrap_path):
    ## Create image files for analysis
    pdf_to_image.main(app_info["SRNT_files"],"first and last",fwrap_path)

    # Analyze images for Type8 form
    counter = 0
    for fname in app_info["SRNT_files"]:
        # Immediately throw out Type7-identified forms
        typer = app_info["SRNT_type"][counter]
        if typer == "Type7" or typer == "Type7-Unreadable":
            counter += 1
            continue

        type_check, date = image_process(fname,fwrap_path)

        # Not identified as a Type7 form
        if type_check == False and date != False:
            app_info["SRNT_type"][counter] = "Type8-Unreadable"
            #print(app_info["app_num"])
            #print("Type8 unreadable")

        #elif type_check == False and date == False:
        #    print(app_info["app_num"])
        #    print("Not Type8")

        # Identified as a Type8 form
        elif type_check == True and date != False:
            app_info["SRNT_type"][counter] = "Type8"
            app_info["SRNT_dates"]["Type8"].append(date)
            
            #print("Type8 date:")
            #print(app_info["app_num"])
            #print(date)

        counter += 1

    return app_info