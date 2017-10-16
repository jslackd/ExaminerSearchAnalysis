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

import type7_analysis, type8_analysis, type2_analysis, pdf_to_image, pull_reed_files

app_dir = "app_data"  # read apps from os.path.join(input_dir, <filename>)
input_dir = "input"  # read images from os.path.join(input_dir, <filename>)
output_dir = "output"  # write images to os.path.join(output_dir, <filename>)
error_output_file = "error_output.txt"
error_output = []

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
        "FOAM_FS_diff:":None,"FOAM_LS_diff:":None,"FOAM_S_median":None,"FOAM_S_mean":None,
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
            info_DATE= keys[0][1]
            info_CODE = keys[1][1]
            info_FNAME = keys[5][1]
            info_DESC = keys[2][1]

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

def file_rename(fwarp_fold,our_name):
    file_list = os.listdir(fwarp_fold)
    print(file_list)

    num = our_name[-2]
    old_name = our_name[:-3]
    
def main():
    ### Step 1: Read input excel file containing application numbers & process into application folders
    #err_fb = pull_reed_files.main()
    #error_output.extend(err_fb)

    # Step 2: Compile app_data (application, continuation, file wrapper info)
    app_folders = os.listdir(app_dir)
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
        info_pass = type7_analysis.recognize_and_rip(info_pass,fwrap_path)

        # Type8 form recognition; also pull Type8 search dates
        info_pass = type8_analysis.recognize_and_rip(info_pass,fwrap_path)

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
        
    # Step 6: Extract dates from Type2 forms in target applications
    print_cnt = 1;
    print("Step 6")
    for target in targets:
        info_pass = app_data[target].copy()
        fwrap_path = os.path.join(app_dir, target, target, target + "-image_file_wrapper")

        srnt_cnt = 0
        for srnt in info_pass["SRNT_type"]:

            # OPTIONAL: percent complete print statement
            print(print_cnt/(len(targets)*3)*100,"percent complete", end = "\r")

            if srnt != "Type2": 
                srnt_cnt += 1; print_cnt += 1
                continue
            else:
                # Pull dates from Type2 forms
                filename = info_pass["SRNT_files"][srnt_cnt]
                info_pass = type2_analysis.read(info_pass,fwrap_path,filename)
                srnt_cnt += 1; print_cnt += 1

        # Update the app_data dictionary
        app_data[target] = info_pass

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
        app_data[target]["FOAM_S_mean"] = median
        medians.append(median)

        # OPTIONAL: percent complete print statement
        print(print_cnt/len(targets)*100,"percent complete", end = "\r")
        print_cnt+=1

    print("", end="\n")
    print("")

    # Step 9: Write data to excel files (one full data file, one target data file)
    full_keys = app_data.keys()
    sub_keys = targets

    # Write to target_app_data.xls

    # Write to all_app_data.xls
    

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


