"""Analysis for type 7 forms"""
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

    # Screen for Type7 forms
    if type7_text_score(text_read) == False:
        #print("---failure----" + fname)
        return False, False
    else:
        # Extract text from Type7 form [can be False value]
        date = type7_extract_text(text_read)
        return True, date

def type7_text_score(text_in):
    # Must score 2 to pass
    score = 0

    # Test 1 --> "Patent Linguistics Utility System"
    if "Patent Linguistics Utility System" in text_in: score += 1

    # Test 2 --> "(PLUS)"
    if "(PLUS)" in text_in: score+= 1

    # Test 3 --> "Scientific and Technical Information" and "SIRA"
    if "Scientific and Technical Information" in text_in and "SIRA" in text_in: score += 1

    if score >= 2:
        return True
    else:
        return False

def type7_extract_text(text_in):
    # Extract date from Type7 form
    text_in = text_in.replace(" ","")
    sbstr1 = re.compile('[0-9][0-9]:[0-9]')
    sbstr2 = re.compile('[0-9]EST')
    sbstr1_found = re.findall(sbstr1,text_in)
    sbstr2_found = re.findall(sbstr2,text_in)
    
    if len(sbstr1_found) == 0 or len(sbstr2_found) == 0:
        return False
    else:
        sbstr1_found = sbstr1_found[0]
        sbstr2_found = sbstr2_found[0]
        index1 = text_in.find(sbstr1_found)
        index2 = text_in.find(sbstr2_found)
        month_day = text_in[index1-5:index1]
        year = text_in[index2+4:index2+8]
        
        date = translate_date(month_day,year)

    return date

def translate_date(monthday, year):
    # Translate Type7 date into standard date
    months = {"jan":"01", "feb":"02", "mar":"03", "apr":"04", "may":"05", "jun":"06",
                "jul":"07", "aug":"08", "sep":"09", "oct":"10", "nov":"11","dec":"12"}

    try: month = months[monthday[:3].lower()]
    except KeyError:
        return False

    day = monthday[3:]
    return year + "/" + month + "/" + day

def recognize_and_rip(app_info, fwrap_path,resolution):
    # Create image files for analysis
    pdf_to_image.main(app_info["SRNT_files"],"first and last",fwrap_path,resolution)

    # Analyze images for Type7 form
    counter = 0
    for fname in app_info["SRNT_files"]:
        type_check, date = image_process(fname,fwrap_path)

        # Not identified as a Type7 form
        if type_check == False and date != False:
            app_info["SRNT_type"][counter] = "Type7-Unreadable"
            #print(app_info["app_num"])
            #print("Type7 unreadable")

        #elif type_check == False and date == False:
        #    print(app_info["app_num"])
        #    print("Not Type7")

        # Identified as a Type7 form
        elif type_check == True and date != False:
            app_info["SRNT_type"][counter] = "Type7"
            app_info["SRNT_dates"]["Type7"].append(date)
            
            #print("Type7 date:")
            #print(app_info["app_num"])
            #print(date)

        counter += 1

    return app_info