"""Converting pages of pdf to png"""
# Jonathan Slack
# jslackd@gmail.com

from wand.image import Image
import os
import numpy as np
import PyPDF2
from multiprocessing.dummy import Pool as ThreadPool
import itertools

input_dir = "app_data" # backup pull folder
output_dir = "input"   # backup push folder

def main(filenames, extent="first", fwrap = input_dir, res = 600):

    for filer in filenames:
        # Create a directory if it doesn't already exist
        folder_name = os.path.join(fwrap, filer)
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)          

        # Converting first page into png
        if extent == "first":
            file = fwrap + "\\" + filer + ".pdf" + "[0]"
            with Image(filename = file, resolution=res) as imgs:
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

            with Image(filename = file1, resolution=res) as imgs:
                imgs.compression_quality = 99
                end_path = os.path.join(folder_name, "0" + ".png")
                Image(imgs.sequence[0]).save(filename = end_path)
            with Image(filename = file2, resolution=res) as imgs:
                imgs.compression_quality = 99
                end_path = os.path.join(folder_name, lastpage + ".png")
                Image(imgs.sequence[0]).save(filename = end_path)
  
        # Converting all pages to png
        else:
            file = fwrap + "\\" + filer + ".pdf"
            with Image(filename= file, resolution=res) as imgs:
                imgs.compression_quality = 99
                pagelen = len(imgs.sequence)
                for cnt in range(0,pagelen-1):
                    end_path = os.path.join(folder_name,str(cnt) + ".png")
                    Image(imgs.sequence[cnt]).save(filename = end_path)

        ## Converting all pages to png
        #else:
        #    file = fwrap + "\\" + filer + ".pdf"
        #    with Image(filename= file, resolution=res) as imgs:
        #        imgs.compression_quality = 99
        #        # Creat list of img sequence objects
        #        imgages = []; name_list = []; cnt = 0
        #        for imgframe in imgs.sequence:
        #            imgages.append(imgframe)
        #            name_list.append(cnt)
        #            cnt += 1

        #        pool = ThreadPool(3)
        #        pool.map(all_pages_thread, zip(imgages,name_list,list(itertools.repeat(folder_name))))
        #        pool.close()
        #        pool.join()

def all_pages_thread(img_in,count,folder_name):
    end_path = os.path.join(folder_name,str(count) + ".png")
    Image(img_in).save(filename = end_path)   

if __name__ == "__main__":
    main()