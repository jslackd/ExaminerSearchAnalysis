"""Scripts for pulling files from Reed Tech"""
# Jonathan Slack
# jslackd@gmail.com

import os
import urllib.request
import zipfile
import pandas as pd
from pandas import ExcelWriter
from pandas import ExcelFile
import zipfile
import time

input_file = "apps_intake.xlsx"
output_dir = "app_data"

def unzip_folder(file_name, app_num):
    zip_ref = zipfile.ZipFile(file_name, 'r')
    out_folder = os.path.join(output_dir,app_num)
    os.mkdir(out_folder)
    zip_ref.extractall(out_folder)
    zip_ref.close()

def main():
    # Read apps from input file
    df = pd.read_excel(input_file, sheetname='Sheet1')
    app_list = df["Applications"].tolist()

    # Define error output for downloading
    error_output_down = []

    # Loop through app list and download apps
    print_cnt = 0
    for app_num_int in app_list:
        print(print_cnt/len(app_list)*100,"percent complete", end = "\r")
        print_cnt+=1

        app_num = str(app_num_int)
        app_num.replace(" ","")
        url = "http://storage.googleapis.com/uspto-pair/applications/" + app_num + ".zip"
        file_name = os.path.join(output_dir,app_num + ".zip")

        # If folder for app exists, then skip this application number
        if os.path.isdir(os.path.join(output_dir,app_num)) == True:
            continue

        # Only the zip file exists, so extract it and skip application number
        elif os.path.isfile(file_name) == True:
            # Unzip the file and delete the original zip file
            unzip_folder(file_name, app_num)
            time.sleep(0.02)
            os.remove(file_name)
            continue

        # Download the file from `url` and save it locally under `file_name`:
        else:
            try:
                with urllib.request.urlopen(url) as response, open(file_name, 'wb') as out_file:
                    data = response.read() # a `bytes` object
                    out_file.write(data)
                    out_file.close()
                #response = requests.get(url, stream = True)
                #with open(file_name,'wb') as out_file:
                #    for chunk in response.iter_content(chunk_size=1024):
                #        if chunk:
                #            out_file.write(chunk)                    
            except TimeoutError:
                error_output_down.append(app_num)
                if os.path.isfile(file_name) == True:
                    os.remove(file_name)                    
                continue
            except urllib.error.HTTPError:
                error_output_down.append(app_num) 
                if os.path.isfile(file_name) == True:
                    os.remove(file_name) 
                continue

            # Unzip the file and delete the original zip file
            unzip_folder(file_name, app_num)
            time.sleep(0.02)
            os.remove(file_name)

    return error_output_down

if __name__ == "__main__":
    main()