# -*- coding: utf-8 -*-
"""
Created on Sat Oct 17 09:46:36 2020

@author: Jerry
"""

import cv2
import numpy as np
from matplotlib import pyplot as plt
import pandas as pd

import vphoto as vp


#%%
# this was written prior to this project - but useful for easy display of images

def showImg(img,FigTitle = '', Extent=None,XY_lables=['',''],Grid=False,Title=''):
    fig,axx = plt.subplots(1,1)
    if img.dtype == np.float32 :
        img1 = (255.0*img).astype("uint8")
    else:
        img1 = img
    img1 = cv2.cvtColor(img1,cv2.COLOR_BGR2RGB)
    axx.imshow(img1,extent=Extent)  # extent :  (left, right, bottom, top)
    axx.set_xlabel(XY_lables[0])
    axx.set_ylabel(XY_lables[1])
    axx.set_title(Title)
    axx.grid(Grid)
    fig.show()


#%%  Example

# four test images - assumed to be in the same folder as the python code
#   os.path.realpath('')

imgfiles = [  'IMG014b.jpg',   'IMG_258.jpg', 'Manarola.JPG' ,  'H13a.jpg']

image = vp.readImage(imgfiles[1])
showImg(image)

box = (0.2,0.3, 0.7, 0.6)

covars = vp.imgCoVar(image, box)
medians = vp.imgMedian(image, box)

imghsv = vp.img2HSV(image)
hsvmeds= vp.imgMedian(imghsv, box)




#%%  inpute a csv file with 12 URLs of images and the four imgfiles
#            the four image files are duplicated as an absolute path and a relative path
#            The vess.csv file should change  C:/Users/Jerry/Pictures/
#                to a folder on the users machine

inputdf = pd.read_csv('vess.csv',  quotechar='"')

# process the image to generate an results data frame
dfpr = vp.procesImages2DataFrame(inputdf)


