"""Patent Search Date Analysis Solution"""
# Jonathan Slack
# jslackd@gmail.com

import numpy as np
import cv2
import os
from math import pi
import random
import sys
import csv
import collections
from datetime import date
from datetime import datetime
import statistics
import xlsxwriter
import pandas as pd
from pandas import ExcelWriter
from pandas import ExcelFile
import math

import type7_analysis, type8_analysis, type2_analysis, pdf_to_image, pull_reed_files

app_dir = "app_data"  # read apps from os.path.join(input_dir, <filename>)
input_dir = "input"  # read images from os.path.join(input_dir, <filename>)
output_dir = "output"  # write images to os.path.join(output_dir, <filename>)
targetapp_file = "target_app_data.xlsx"
allapp_file = "all_app_data.xlsx"
error_output_file = "error_output.txt"
error_output = []
resolution = 600

# Declare data structure
app_data = collections.OrderedDict()
# Format: {app_num (str): {attrib (str): val (---)}}
# Attributes:
#       "app_num"       : "11837541"
#       "f_date"        : "08-20-2007"
#       "app_type"      : "Utility"
#       "exam_name"     : "OHERN, BRENT T"
#       "art_unit"      : "1794"
#       "cls_sbcls"     : "428/068"
#       "stat"          : "Abandoned -- Failure to Respond to an Office Action"
#       "stat_date"     : "9/11/2009"
#       "pub_num"       : "US 2009-0053499 A1"
#       "pub_date"      : "2/26/2009"
#       "pat_num"       : None
#       "pat_date"      : None
#       "FOAM_date"     : "1/8/2009"
#       "pre_amend"     : []
#       "rest_requ"     : []
#       "cont_data"     : []
#       "continuation?" : None
#       "SRNT_num"      : 1
#       "SRNT_type"     : ["Type2"]     (in chronological order)
#       "SRNT_check"    : True
#       "SRNT_dates"    : {"Type2": ["1/4/2009", "1/4/2009", "1/4/2009"], "Type7":[], "Type8":[]}
#       "SRNT_files"    : [<str>.pdf,  <str>.pdf,  <str>.pdf]
#       "SRFW_occur"    : None
#       "FOAM_FS_diff:" : 4.0
#       "FOAM_LS_diff:" : 4.0
#       "FOAM_S_median" : 4.0
#       "FOAM_S_mean"   : 4.0
#       "analyze?"      : True


def create_dictionary_entry(app_num):
    app_data[app_num] = {
        "app_num":None,"f_date":None,"app_type":None,"exam_name":None,"art_unit":None,"cls_sbcls":None,
        "stat":None,"stat_date":None,"pub_num":None,"pub_date":None,"pat_num":None,"pat_date":None,
        "FOAM_date":None,"pre_amend":[],"rest_requ":[],"cont_data":[], "continuation?":None,
        "SRNT_num":0, "SRNT_type":[],"SRNT_check":None, "SRNT_files":[], "SRFW_occur":None,
        "FOAM_FS_diff":None,"FOAM_LS_diff":None,"FOAM_S_median":None,"FOAM_S_mean":None,
        "analyze?":None, "SRNT_dates":{"Type2":[], "Type7":[], "Type8":[]}
    }

def examine_application_info(app,path):
    # Exceptional case - no application info csv file
    if os.path.exists(path + "\\" + app + "-application_data.tsv") == False:
        error_output.append(app + " --> app info file path error")
        return False

    # Analyze the application info csv file
    with open(path + "\\" + app + "-application_data.tsv") as tsvfile:
        reader = csv.DictReader(tsvfile, dialect='excel-tab')

        # Store data in a temporary DICTIONARY
        temp_app_data = {}
        for row in reader:
            key = list(row.items())[0][1]
            value = list(row.items())[1][1]
            temp_app_data[key] = value

        # "app_num" : <srt>
        app_data[app]["app_num"] = list(row.items())[1][0]

    # "f_date" : <str>
    try: app_data[app]["f_date"] = temp_app_data["Filing or 371 (c) Date"]
    except KeyError:
        error_output.append(app + " --> f_date error")
        pass
    # "app_type" : <str>
    try: app_data[app]["app_type"] = temp_app_data["Application Type"]
    except KeyError:
        error_output.append(app + " --> app_type error")
        pass
    # "exam_name" : <str>
    try: app_data[app]["exam_name"] = temp_app_data["Examiner Name"]
    except KeyError:
        error_output.append(app + " --> exam_name error")
        pass
    # "art_unit" : <str>
    try: app_data[app]["art_unit"] = temp_app_data["Group Art Unit"]
    except KeyError:
        error_output.append(app + " --> art_unit error")
        pass
    # "cls_sbcls" : <str>
    try: app_data[app]["cls_sbcls"] = temp_app_data["Class / Subclass"]
    except KeyError:
        error_output.append(app + " --> cls_sbcls error")
        pass
    # "stat" : <str>
    try: app_data[app]["stat"] = temp_app_data["Status"]
    except KeyError:
        error_output.append(app + " --> stat error")
        pass
    # "stat_date" : <str>
    try: app_data[app]["stat_date"] = temp_app_data["Status Date"]
    except KeyError:
        error_output.append(app + " --> stat_date error")
        pass
    # "pub_num" : <str>
    try: app_data[app]["pub_num"] = temp_app_data["Earliest Publication No"]
    except KeyError:
        error_output.append(app + " --> pub_num error")
        pass
    # "pub_date" : <str>
    try: app_data[app]["pub_date"] = temp_app_data["Earliest Publication Date"]
    except KeyError:
        error_output.append(app + " --> pub_date error")
        pass
    # "pat_num" : <str>
    try: app_data[app]["pat_num"] = temp_app_data["Patent Number"]
    except KeyError:
        error_output.append(app + " --> pat_num error")
        pass
    # "pat_date" : <str>
    try: app_data[app]["pat_date"] = temp_app_data["Issue Date of Patent"]
    except KeyError:
        error_output.append(app + " --> pat_date error")
        pass

    # Check if continuation info csv file
    if os.path.exists(path + "\\" + app + "-continuity_data.tsv") == True:
       
        # Analyze the application info csv file
        with open(path + "\\" + app + "-continuity_data.tsv") as tsvfile:
            reader = csv.DictReader(tsvfile, dialect='excel-tab')

            # Store data in a temporary DICTIONARY
            tic1 = 0; tic2 = 0; tic3 = 0; tic4 = 0;
            for row in reader:
                keys = list(row.items())
                cont_DESC = keys[0][1]
                # "cont_data" : <str>
                if "is a continuation of" in cont_DESC.lower() and tic1 == 0:
                    # "continuation?" : None
                    app_data[app]["continuation?"] = True
                    app_data[app]["cont_data"].append("Continuation")
                    tic1 += 1
                elif "national state entry of" in cont_DESC.lower() and tic2 == 0:
                    app_data[app]["cont_data"].append("National State Entry")
                    tic2 += 1
                elif "claims priority from provisional application" in cont_DESC.lower() and tic3 == 0:
                    app_data[app]["cont_data"].append("Provisional Priority")
                    tic3 += 1
                elif "claims the benefit of " + app_data[app]["app_num"] in cont_DESC.lower() and tic4 == 0:
                    app_data[app]["cont_data"].append("Parent Application")
                    tic4 += 1
        
    # Succesful analysis; return True
    return True

def examine_image_wrapper(app,path):
    # Exceptional case - no image file wrapper csv file
    fwrap_fold = path + "\\" + app + "-image_file_wrapper" 
    fwrap_path = fwrap_fold + "\\" + app + "-image_file_wrapper.tsv"
    if os.path.exists(fwrap_path) == False:
        error_output.append(app + " --> image fwrapper file path error")
        return False

    # Analyze the image file wrapper csv file
    with open(fwrap_path) as tsvfile:
        reader = csv.DictReader(tsvfile, dialect='excel-tab')

        # Loop through lines and record info
        for row in reversed(list(reader)):
            keys = list(row.items())
            d = {}
            for key in keys: d[key[0]] = key[1]

            if "Mail Room Date" in d: info_DATE= d["Mail Room Date"]
            else: info_DATE = " "
            if "Document Code" in d: info_CODE= d["Document Code"]
            else: info_CODE = " "
            if "Filename" in d: info_FNAME= d["Filename"]
            else: info_FNAME = " "
            if "Document Description" in d: info_DESC= d["Document Description"]
            else: info_DESC = " "

            # "FOAM_date"     : <str>
            if info_CODE == "CTNF":
                app_data[app]["FOAM_date"] = info_DATE
                # Break b/c we have hit the upper end of the sandwich
                break

            # "pre_amend"     : [<str>]
            elif "amendment" in info_DESC.lower():
                app_data[app]["pre_amend"].append(info_DATE)
                # Reset values for SRNT and SRFW
                app_data[app]["SRNT_num"] = 0
                app_data[app]["SRNT_type"] = []
                app_data[app]["SRNT_dates"]["Type2"] = []
                app_data[app]["SRNT_dates"]["Type7"] = []
                app_data[app]["SRNT_dates"]["Type8"] = []
                app_data[app]["SRNT_files"] = []
                app_data[app]["SRFW_occur"] = None

            # "rest_requ"     : [<str>]
            elif "restriction" in info_DESC.lower():
                app_data[app]["rest_requ"].append(info_DATE)
                # Reset values for SRNT and SRFW
                app_data[app]["SRNT_num"] = 0
                app_data[app]["SRNT_type"] = []
                app_data[app]["SRNT_dates"]["Type2"] = []
                app_data[app]["SRNT_dates"]["Type7"] = []
                app_data[app]["SRNT_dates"]["Type8"] = []
                app_data[app]["SRNT_files"] = []
                app_data[app]["SRFW_occur"] = None

            # SRNT analysis
            elif info_CODE == "SRNT":
                # "SRNT_num" : <int>
                app_data[app]["SRNT_num"] += 1
                # "SRNT_type" : [<str>]
                app_data[app]["SRNT_type"].append("Unknown")
                # "SRNT_files" : [<str>]
                if info_FNAME == "":
                    app_data[app]["SRNT_files"].append(None)
                else:
                    our_name = info_FNAME[:-4]
                    app_data[app]["SRNT_files"].append(our_name)
                    ## Check for duplicate names
                    #our_name = info_FNAME[:-4]
                    #enter_cond = 1
                    #if our_name not in app_data[app]["SRNT_files"]:
                    #    app_data[app]["SRNT_files"].append(our_name)

                    #else:
                    #    # Duplicate name handling
                    #    while True:
                    #        if our_name in app_data[app]["SRNT_files"]:
                    #            if our_name[-1] == "T":
                    #                our_name = our_name+"(1)"

                    #                break
                    #            elif our_name[-1] == ")":
                    #                num = int(our_name[-2])
                    #                num += 1
                    #                our_name[-2] = str(num)    
                    #        else:
                    #            break               

                    #    file_rename(fwarp_fold,our_name)
                    #    app_data[app]["SRNT_files"].append(our_name)

            # "SRFW_occur" : True/None
            elif info_CODE == "SRFW":
                app_data[app]["SRFW_occur"] = None

    # Succesful analysis; return True
    return True

def write_app_data(data_in, keys, file_out, jump, to_add):
    # Delete existing file if it exists
    if os.path.isfile(file_out) == True:
        if os.path.isfile(os.path.join("output",file_out)) == True:
            os.remove(os.path.join("output",file_out))
        os.rename(file_out,os.path.join("output",file_out))
        

    # Open a workbook and a worksheet
    workbook = xlsxwriter.Workbook(file_out)
    worksheet = workbook.add_worksheet()
    worksheet.set_column(0,27,12)
    worksheet.set_column(0,1,15)
    worksheet.set_column(7,8,15)
    worksheet.set_column(11,16,15)
    worksheet.set_column(18,20,35)
    worksheet.set_column(24,26,20)

    # Set formats
    header_format = workbook.add_format({'bold': True, 'font_color': 'black', 'align' : 'center'})
    header_format.set_text_wrap()
    text_format = workbook.add_format({'font_color': 'black', 'align' : 'center'})
    text_format.set_text_wrap()
    #date1_format = workbook.add_format({'font_color': 'black', 'num_format':'yyyy/mm/dd', 'align' : 'center'})
    #date1_format.set_text_wrap()
    #date2_format = workbook.add_format({'font_color': 'black', 'num_format':'mm/dd/yyy', 'align' : 'center'})
    #date2_format.set_text_wrap()
    int_format = workbook.add_format({'font_color': 'black', 'num_format':'0', 'align' : 'center'})
    int_format.set_text_wrap() 
    float_format = workbook.add_format({'font_color': 'black', 'num_format':'0.00', 'align' : 'center'})
    float_format.set_text_wrap()
    special_format = workbook.add_format({'font_color': 'red', 'num_format':'0.00', 'align' : 'center'})

    # Write important findings
    worksheet.write('A1', 'Average First Search Diff. (days):', header_format)
    worksheet.write('A2', 'Average Last Search Diff. (days):', header_format)
    worksheet.write('A3', 'Average Mean Search Diff. (days):', header_format)
    worksheet.write('A4', 'Average Median Search Diff. (days):', header_format)
    #afs = findings["Average First Search"]; als = findings["Average Last Search"]
    #ams = findings["Average Mean Search"]; ads = findings["Average Median Search"]
    #if afs is not None: worksheet.write_number(0,1,afs,special_format)
    #else: worksheet.write_string(0,1," ",text_format)
    #if als is not None: worksheet.write_number(1,1,als,special_format)
    #else: worksheet.write_string(1,1," ",text_format)
    #if ams is not None: worksheet.write_number(2,1,ams,special_format)
    #else: worksheet.write_string(2,1," ",text_format)
    #if ads is not None: worksheet.write_number(3,1,ads,special_format)
    #else: worksheet.write_string(3,1," ",text_format)
    
    # Write headers below important findings:
    worksheet.write('A5', 'Application', header_format)
    worksheet.write('B5', 'Filing Date', header_format)
    worksheet.write('C5', 'Analyzed?', header_format)
    worksheet.write('D5', 'FOAM to FS', header_format)
    worksheet.write('E5', 'FOAM to LS', header_format)
    worksheet.write('F5', 'FOAM to S Mean', header_format)
    worksheet.write('G5', 'FOAM to S Median', header_format)
    worksheet.write('H5', 'App. Type', header_format)
    worksheet.write('I5', 'Examiner', header_format)
    worksheet.write('J5', 'Art Unit', header_format)
    worksheet.write('K5', 'Class/Subclass', header_format)
    worksheet.write('L5', 'Status', header_format)
    worksheet.write('M5', 'Status Date', header_format)
    worksheet.write('N5', 'Publication No.', header_format)
    worksheet.write('O5', 'Publication Date', header_format)
    worksheet.write('P5', 'Patent No.', header_format)
    worksheet.write('Q5', 'Patent Date', header_format)
    worksheet.write('R5', 'FOAM Date', header_format)
    worksheet.write('S5', 'Type2 SRNT Date(s)', header_format)
    worksheet.write('T5', 'Type7 SRNT Date(s)', header_format)
    worksheet.write('U5', 'Type8 SRNT Date(s)', header_format)
    worksheet.write('V5', 'SRNT Visual Pass?', header_format)
    worksheet.write('W5', 'No. of Active SRNT(s)', header_format)
    worksheet.write('X5', 'SRNT Type(s)', header_format)
    worksheet.write('Y5', 'Prel. Amendments', header_format)
    worksheet.write('Z5', 'Restriction Requ.', header_format)
    worksheet.write('AA5', 'Continuity Data', header_format)
    worksheet.write('AB5', 'Continuation?', header_format)
    worksheet.write('AC5', 'Active SRFW?', header_format)

    # Write in previously found data
    if jump != 0:
        row = 5; col = 0
        for adder in to_add:
            col = 0
            for add in adder:
                if isinstance(add,str):
                    worksheet.write_string(row,col,add,text_format)
                elif isinstance(add,float) and math.isnan(add) == False:
                    worksheet.write_number(row,col,add,float_format)
                elif isinstance(add,int) and math.isnan(add) == False:
                    worksheet.write_number(row,col,add,int_format)
                else:
                    worksheet.write_string(row,col,"",text_format)
                col += 1
            row += 1
    else:
        row = 5

    # Write in data for each application.
    bin_trans = {True: "Yes", False: "No", None: "No"}
    for key in keys:

        worksheet.write_number(row,0,int(key),int_format)

        filing_date = data_in[key]["f_date"]
        if filing_date is not None: worksheet.write_string(row,1,filing_date,text_format)
        else: worksheet.write_string(row,1," ",text_format)

        worksheet.write_string(row,2,bin_trans[data_in[key]["analyze?"]],text_format)

        r3 = data_in[key]["FOAM_FS_diff"]
        if r3 is not None: worksheet.write_number(row,3,r3,int_format)
        else: worksheet.write_string(row,3," ",text_format)

        r4 = data_in[key]["FOAM_LS_diff"]
        if r4 is not None: worksheet.write_number(row,4,r4,int_format)
        else: worksheet.write_string(row,4," ",text_format)

        r5 = data_in[key]["FOAM_S_mean"]
        if r5 is not None: worksheet.write_number(row,5,r5,float_format)
        else: worksheet.write_string(row,5," ",text_format)

        r6 = data_in[key]["FOAM_S_median"]
        if r6 is not None: worksheet.write_number(row,6,r6,int_format)
        else: worksheet.write_string(row,6," ",text_format)

        worksheet.write_string(row,7,data_in[key]["app_type"],text_format)
        worksheet.write_string(row,8,data_in[key]["exam_name"],text_format)
        worksheet.write_number(row,9,int(data_in[key]["art_unit"]),int_format)
        worksheet.write_string(row,10,data_in[key]["cls_sbcls"],text_format)
        worksheet.write_string(row,11,data_in[key]["stat"],text_format)
        worksheet.write_string(row,12,data_in[key]["stat_date"],text_format)        
        worksheet.write_string(row,13,data_in[key]["pub_num"],text_format)
        worksheet.write_string(row,14,data_in[key]["pub_date"],text_format)
        worksheet.write_string(row,15,data_in[key]["pat_num"],text_format)
        worksheet.write_string(row,16,data_in[key]["pat_date"],text_format)

        FOAM_date = data_in[key]["FOAM_date"]
        if FOAM_date is not None: worksheet.write_string(row,17,FOAM_date,text_format)
        else: worksheet.write_string(row,17," ",text_format)

        t2dates = data_in[key]["SRNT_dates"]["Type2"]
        t2dstringer = ""
        for t2d in t2dates:
            if t2dstringer == "":
                t2dstringer  = t2dstringer  + t2d
            else:
                t2dstringer  = t2dstringer  + "; " + t2d
        worksheet.write_string(row,18,t2dstringer,text_format)

        t7dates = data_in[key]["SRNT_dates"]["Type7"]
        t7dstringer = ""
        for t7d in t7dates:
            if t7dstringer == "":
                t7dstringer  = t7dstringer  + t7d
            else:
                t7dstringer  = t7dstringer  + "; " + t7d
        worksheet.write_string(row,19,t7dstringer,text_format)

        t8dates = data_in[key]["SRNT_dates"]["Type8"]
        t8dstringer = ""
        for t8d in t8dates:
            if t8dstringer == "":
                t8dstringer  = t8dstringer  + t8d
            else:
                t8dstringer  = t8dstringer  + "; " + t8d
        worksheet.write_string(row,20,t8dstringer,text_format)

        worksheet.write_string(row,21,bin_trans[data_in[key]["SRNT_check"]],text_format)
        worksheet.write_number(row,22,data_in[key]["SRNT_num"],int_format)

        # Compiling Types of SRNTs
        types_string = ""
        for types in data_in[key]["SRNT_type"]:
            if types_string == "":
                types_string = types_string + types
            else:
                types_string = types_string + "; " + types
        worksheet.write_string(row,23,types_string,text_format)

        # Compiling Amendments
        am_string = ""
        for am in data_in[key]["pre_amend"]:
            if am_string == "":
                am_string = am_string + am
            else:
                am_string = am_string + "; " + am
        worksheet.write_string(row,24,am_string,text_format)

        # Compiling Restriction Requirements
        rr_string = ""
        for rr in data_in[key]["rest_requ"]:
            if rr_string == "":
                rr_string = rr_string + rr
            else:
                r_string = rr_string + "; " + rr
        worksheet.write_string(row,25,rr_string,text_format)

        # Compiling Continuity Data
        cd_string = ""
        for cd in data_in[key]["cont_data"]:
            if cd_string == "":
                cd_string = cd_string + cd
            else:
                cd_string = cd_string + "; " + cd
        worksheet.write_string(row,26,cd_string,text_format)

        worksheet.write_string(row,27,bin_trans[data_in[key]["continuation?"]],text_format)
        worksheet.write_string(row,28,bin_trans[data_in[key]["SRFW_occur"]],text_format)       
        
        row += 1

    # Write final findings:
    worksheet.write_formula('B1', '=AVERAGE(D1:D' + str(row+1) + ')')
    worksheet.write_formula('B2', '=AVERAGE(E1:E' + str(row+1) + ')')
    worksheet.write_formula('B3', '=AVERAGE(F1:F' + str(row+1) + ')')
    worksheet.write_formula('B4', '=AVERAGE(G1:G' + str(row+1) + ')')

    workbook.close()

def main():
    print("Step 1")
    # Step 1: Read input excel file containing application numbers & process into application folders
    err_down = pull_reed_files.main()
    # If there are application files missing, then stop execution
    if err_down != []:
        print("")
        print("The following files could not be downloaded from Reed Tech:")
        for err_d in err_down:
            print(err_d)
        print("")
        #sys.exit("Execution has been terminated.")
    # Otherwise, continue with execution and display number of applications
    else:
        num_of_apps = len(os.listdir(app_dir))
        print("Analyzing {} Applications".format(num_of_apps))
        print("")

    print("")
    print("")

    # Step INT: figure out which apps have been analyzed
    app_folders = os.listdir(app_dir)
    if os.path.isfile(allapp_file) == True:
        # all apps file
        df = pd.read_excel(allapp_file, sheetname='Sheet1')
        app_list = df["Average First Search Diff. (days):"].tolist()
        jumper = len(app_list) + 1
        to_add_all = df.iloc[4:jumper]
        to_add_all = to_add_all.values.tolist()
        # target apps file
        df2 = pd.read_excel(targetapp_file, sheetname = 'Sheet1')
        app_list_2 = df2["Average First Search Diff. (days):"].tolist()
        jumper_target = len(app_list_2) + 1
        to_add_target = df2.iloc[4:jumper_target]
        to_add_target = to_add_target.values.tolist()
        # Revmove analyzed apps from the list
        app_list.remove("Average Last Search Diff. (days):")
        app_list.remove("Average Mean Search Diff. (days):")
        app_list.remove("Average Median Search Diff. (days):")
        app_list.remove("Application")
        for app_l in app_list:
            app_p = str(app_l)
            app_folders.remove(app_p)
    else:
        jumper = 0; jumper_target = 0
        to_add_all = []; to_add_target = []
  
    # Step 2: Compile app_data (application, continuation, file wrapper info)
    # Loop through application folders 
    print_cnt = 1
    print("Step 2")
    for app_folder in app_folders:
        
        # Initialize dictionary entry
        app = os.listdir(os.path.join(app_dir, app_folder))[0]
        create_dictionary_entry(app)
        app_path = os.path.join(app_dir, app_folder, app)

        # Pull and record application info
        examine_application_info(app,app_path)

        # Examine file wrapper info and identify target applications
        examine_image_wrapper(app,app_path)

        # OPTIONAL: percent complete print statement
        print(print_cnt/len(app_folders)*100,"percent complete", end = "\r")
        print_cnt+=1

    print("")
    print("")
    
    # Step 3: Identify targeted applications (round 1)
    tad = app_data.copy()
    # Must meet 4 conditions: 1. FOAM 2. NO restriction requirement 3. NO continuation 4. SRNT(s)
    tad = {k1: v1 for k1, v1 in tad.items() if (v1["FOAM_date"] != None and 
            v1["rest_requ"] == [] and v1["continuation?"] == None and 
            v1["SRNT_num"] > 0)}
    targets = tad.keys()

    # OPTIONAL: complete print statement
    print("Step 3")
    print("100.0 percent complete")
    print("")

    # Step 4: Loop through target applications and analyze SRNT(s) for types
    print_cnt = 1
    print("Step 4")
    for target in targets:
        info_pass = app_data[target].copy()
        fwrap_path = os.path.join(app_dir, target, target, target + "-image_file_wrapper")
        
        # Type7 form recognition; also pull Type7 search dates
        info_pass = type7_analysis.recognize_and_rip(info_pass,fwrap_path, resolution)

        # Type8 form recognition; also pull Type8 search dates
        info_pass = type8_analysis.recognize_and_rip(info_pass,fwrap_path, resolution)

        # Type2 form recognition
        info_pass = type2_analysis.recognize(info_pass,fwrap_path)

        # Set "SRNT_check" based on form types in "SRNT_type"
        if all(t == "Type2" or t == "Type7" or t == "Type8" for t in info_pass["SRNT_type"]):
            info_pass["SRNT_check"] = True

        # Update the app_data dictionary
        app_data[target] = info_pass

        # OPTIONAL: percent complete print statement
        print(print_cnt/len(targets)*100,"percent complete", end = "\r")
        print_cnt+=1

    print("", end="\n")
    print("")
    
    # Step 5: Refine targeted applications list (round 2)
    tad = app_data.copy()
    # Must meet 1 aggregate conditions: 1. For prior targets, all SRNT(s) are readable
    tad = {k1: v1 for k1, v1 in tad.items() if v1["SRNT_check"] == True}
    targets = tad.keys()

    # OPTIONAL: complete print statement
    print("Step 5")
    print("100.0 percent complete")
    print("")
    print("{} target applications identified".format(len(targets)))
    print("")
        
    # Step 6: Extract dates from Type2 forms in target applications
    print_cnt = 1;
    print("Step 6")
    for target in targets:
        info_pass = app_data[target].copy()
        fwrap_path = os.path.join(app_dir, target, target, target + "-image_file_wrapper")

        srnt_cnt = 0
        for srnt in info_pass["SRNT_type"]:

            # OPTIONAL: percent complete print statement
            print((print_cnt/len(targets))*100,"percent complete", end = "\r")

            if srnt != "Type2": 
                srnt_cnt += 1; print_cnt += 1
                continue
            else:
                # Pull dates from Type2 forms
                filename = info_pass["SRNT_files"][srnt_cnt]
                info_pass = type2_analysis.read(info_pass,fwrap_path,filename, resolution)
                srnt_cnt += 1; print_cnt += 1

        # Update the app_data dictionary
        app_data[target] = info_pass

    if print_cnt == 1:
        print("100.0 percent complete")

    print("", end="\n")
    print("")
        
    # Step 7: Refine targeted applications list (round 3)
    tad = app_data.copy()
    # Must meet 1 aggregate conditions: 1. For prior targets, all SRNT(s) are readable
    tad = {k1: v1 for k1, v1 in tad.items() if v1["SRNT_check"] == True}
    targets = tad.keys()

    # OPTIONAL: complete print statement
    print("Step 7")
    print("100.0 percent complete")
    print("")
    print("{} applications flagged for analysis".format(len(targets)))
    print("")

    # Step 8: Look at analyze flag and analyze dates
    print_cnt = 1
    print("Step 8")

    # Set datetime format
    dateformat = "%Y/%m/%d";  fs = []; ls = []; means = []; medians = []
    FOAMformat = "%m-%d-%Y";
    for target in targets:
        app_data[target]["analyze?"] = True

        # Pull crucial date metrics
        FOAMdate = datetime.strptime(app_data[target]["FOAM_date"], FOAMformat)
        Type8dates = app_data[target]["SRNT_dates"]["Type8"]
        Type7dates = app_data[target]["SRNT_dates"]["Type7"]
        Type2dates = app_data[target]["SRNT_dates"]["Type2"]
        all_dates = Type8dates + Type7dates + Type2dates
        all_dtdates = []
        for dater in all_dates:  
            all_dtdates.append(datetime.strptime(dater, dateformat))

        # "FOAM_FS_diff:" : <float>
        fsearch = min(all_dtdates)
        delta = FOAMdate - fsearch
        app_data[target]["FOAM_FS_diff"] = float(delta.days)
        fs.append(delta.days)

        # "FOAM_LS_diff:" : <float>
        lsearch = max(all_dtdates)
        delta = FOAMdate - lsearch
        app_data[target]["FOAM_LS_diff"] = float(delta.days)    
        ls.append(delta.days)    

        # "FOAM_S_mean"   : <float>
        all_diff = FOAMdate - np.array(all_dtdates)
        all_diff_days = [d.days for d in all_diff]
        mean = float(statistics.mean(all_diff_days))
        app_data[target]["FOAM_S_mean"] = mean
        means.append(mean)
            
        # "FOAM_S_median" : <float>
        median = float(statistics.median(all_diff_days))
        app_data[target]["FOAM_S_median"] = median
        medians.append(median)

        # OPTIONAL: percent complete print statement
        print(print_cnt/len(targets)*100,"percent complete", end = "\r")
        print_cnt+=1

    if print_cnt == 1:
        print("100.0 percent complete")

    print("", end="\n")
    print("")

    # Step 9: Write data to excel files (one full data file, one target data file)
    full_keys = app_data.keys()
    sub_keys = targets

    # Write to target_app_data.xls
    write_app_data(app_data, sub_keys, targetapp_file, jumper_target, to_add_target)

    # Write to all_app_data.xls
    write_app_data(app_data, full_keys, allapp_file, jumper, to_add_all)

    # OPTIONAL: complete print statement
    print("Step 9")
    print("100.0 percent complete")
    print("")

    # Final Step: record errors to text files
    error_write = open(error_output_file, 'w')
    for error_str in error_output:
        error_write.write("%s\n" % error_str)

if __name__ == "__main__":
    main()


