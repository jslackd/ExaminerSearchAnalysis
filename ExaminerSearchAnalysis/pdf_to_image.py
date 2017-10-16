"""Converting pages of pdf to png"""
# Jonathan Slack
# jslackd@gmail.com

from wand.image import Image
import os
import numpy as np
import PyPDF2

input_dir = "app_data" # backup pull folder
output_dir = "input"   # backup push folder

def main(filenames, extent="first", fwrap = input_dir):

    for filer in filenames:
        # Create a directory if it doesn't already exist
        folder_name = os.path.join(fwrap, filer)
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)          

        # Converting first page into png
        if extent == "first":
            file = fwrap + "\\" + filer + ".pdf" + "[0]"
            with Image(filename = file, resolution=600) as imgs:
                imgs.compression_quality = 99
                img = imgs.sequence
                end_path = os.path.join(folder_name,"0.png")
                Image(img[0]).save(filename = end_path)

        # Converting first and last page into png
        elif extent == "first and last":
            file1 = fwrap + "\\" + filer + ".pdf" + "[0]"
            file_base = fwrap + "\\" + filer + ".pdf"
            file_base = file_base.replace("\\","/")
            file = open(file_base,'rb')
            reader = PyPDF2.PdfFileReader(file)
            lastpage = str(reader.getNumPages() - 1)
            file2 = fwrap + "\\" + filer + ".pdf" + "[" + lastpage + "]"

            with Image(filename = file1, resolution=600) as imgs:
                imgs.compression_quality = 99
                end_path = os.path.join(folder_name, "0" + ".png")
                Image(imgs.sequence[0]).save(filename = end_path)
            with Image(filename = file2, resolution=600) as imgs:
                imgs.compression_quality = 99
                end_path = os.path.join(folder_name, lastpage + ".png")
                Image(imgs.sequence[0]).save(filename = end_path)

        # Converting all pages to png
        else:
            file = fwrap + "\\" + filer + ".pdf"
            with Image(filename= file, resolution=600) as imgs:
                imgs.compression_quality = 99
                pagelen = len(imgs.sequence)
                for cnt in range(0,pagelen-1):
                    end_path = os.path.join(folder_name,str(cnt) + ".png")
                    Image(imgs.sequence[cnt]).save(filename = end_path)

if __name__ == "__main__":
    main()