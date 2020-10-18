# -*- coding: utf-8 -*-
"""
Created on Sat Oct 17 09:46:36 2020

@author: Jerry
"""


import os
import numpy as np
import urllib.request as req
import cv2
import pandas as pd


#%%
# computed the transformation from BGR (or RBG) to HSV
# the use of the mode='cv2' is much faster
#  this was written prior to this project

def img2HSV (img,mode='cv2',output='t', incolor = 'BGR' ):
    if img.dtype == 'uint8':  img = img.astype('float32')/255.
    if incolor == 'RGB':  img = img[:,:,::-1]
    if mode=='cv2':
        hsv = cv2.cvtColor(img,cv2.COLOR_HSV2BGR)
        if output == 's':  return cv2.split(hsv)
        return hsv
    B,G,R = cv2.split(img)
    cmax = np.maximum.reduce([R,G,B])
    cmin = np.minimum.reduce([R,G,B])
    dc = cmax - cmin
    hue = np.zeros(cmax.shape,dtype='float32')
    hx = np.zeros(cmax.shape,dtype='float32')
    hx[dc!=0] = ((G[dc!=0]-B[dc!=0])/dc[dc!=0]) % 6.0
    hue[cmax==R] = hx[cmax==R]

    hx[:,:] = 0.0
    hx[dc!=0] = ((B[dc!=0]-R[dc!=0])/dc[dc!=0]) + 2.0
    hue[cmax==G] = hx[cmax==G]

    hx[:,:] = 0.0
    hx[dc!=0] = ((R[dc!=0]-G[dc!=0])/dc[dc!=0]) + 4.0
    hue[cmax==B] = hx[cmax==B]
    hue[dc==0] = 0.0
    hue = 60*hue
    satu = np.zeros(cmax.shape,dtype='float32')
    satu[cmax!=0] = dc[cmax!=0]/cmax[cmax!=0]
    V = cmax
    if output == 's':     return hue,satu,V
    return(cv2.merge((hue,satu,V)))


# splits file to path, name and extension

def fileSplit(file):
    fldr = os.path.dirname(file)
    [fname, fext] = os.path.splitext(os.path.basename(file))
    return [fldr,fname,fext]


# gets image from a URL (assuming that hte URL points to a jpg image)

def getImgFromURL(url):
    apiopen = req.build_opener()
    try:
        response = apiopen.open(url)
    except:
        print('Failed to get URL')
        return None
    upage = response.read()
    info = response.info()
    apiopen.close()
    if len(info.defects) > 0:
        print('error processing URL')
        return None
    array = np.asarray(bytearray(upage) )
    image = cv2.imdecode(array, cv2.IMREAD_COLOR)
    return image

# reads image from either URL or a file with relative or absolute paths

def readImage(imgLink):
    if imgLink[:8] == 'https://' or imgLink[:7] == 'http://':
        image = getImgFromURL(imgLink)
        return image
    if os.path.isfile(imgLink):
        image = cv2.imread(imgLink)
        if not image is None:  return image
    fpt,fnm,fex = fileSplit(imgLink)
    file = os.path.join(os.path.realpath(''), fpt, fnm+fex)
    if os.path.isfile(file):
        image = cv2.imread(file)
        if not image is None:  return image
    print('cannot find file or URL')
    return None

#%%

# indexRel  - returns an index as an integer basically path through if the initial
#             index is an integer
#             IF the intial indx is a float it is assumed that this is a relative
#             index to be scaled with the maximum dimnsion nn
#             The return is an integer

def indexRel(indx, nn):
    ty = type(indx)
    if any([ty==float, ty==np.float32, ty==np.float64]):
        return min(round(indx*nn),nn-1)
    return indx

# inputs to the following two function can be in BGR - the OpenCV standard
#        or in RGB incolor='RGB'

# calculates the coef of variance for each channel typically BRR

def imgCoVar(img, box, incolor = 'BGR'):
    ht,wd = img.shape[:2]
    lft = indexRel(box[0],wd)
    rgt = indexRel(box[2],wd)
    top = indexRel(box[1],ht)
    btm = indexRel(box[3],ht)
    imgbx = img[top:(btm-1), lft:(rgt-1), :]
    if incolor=='RGB':  imgbx = imgbx[:,:,::-1]
    blu,grn,red = cv2.split(imgbx)
    blcv = np.std(blu)/np.mean(blu)
    grcv = np.std(grn)/np.mean(grn)
    rdcv = np.std(red)/np.mean(red)
    return (rdcv,grcv,blcv)

# calculates the median for each channel typically BRR


def imgMedian(img, box, incolor = 'BGR'):
    ht,wd = img.shape[:2]
    lft = indexRel(box[0],wd)
    rgt = indexRel(box[2],wd)
    top = indexRel(box[1],ht)
    btm = indexRel(box[3],ht)
    imgbx = img[top:(btm-1), lft:(rgt-1), :]
    if incolor=='RGB':  imgbx = imgbx[:,:,::-1]
    blu,grn,red = cv2.split(imgbx)
    blmd = np.median(blu)
    grmd = np.median(grn)
    rdmd = np.median(red)
    return (rdmd,grmd,blmd)


#%%  Takes input frame with the keys 'image_id', 'image_source' and 'region'
#          and performs calcuations on the images linked by 'imagte_source'
#              'imagte_source' can be an absolute or relative path on
#               the local machine or an URL to a jpg image
#  returns a data frame with computed values from the images
#  these values are the medians of each color, and medians of the HSV color space
#   also returned are the coef of variance for each oolor

def procesImages2DataFrame(indataframe):
    keys = list(indataframe.keys())
    nokey = False
    if not 'image_id' in keys: nokey = True
    if not 'image_source' in keys: nokey = True
    if not 'region' in keys: nokey = True
    if len(indataframe) <1: nokey = True
    if nokey:
        print('Wrong Input Data Frame')
        return None

    paDataFrame = pd.DataFrame({'image_id':[], 'image_source':[],
                 'med_r':[], 'med_g':[], 'med_b':[] ,
                 'med_h':[], 'med_s':[], 'med_v':[] ,
                 'cv_r':[],  'cv_g':[],  'cv_b':[] } )

    for ix in range(len(indataframe)):
        imgID = indataframe.iloc[ix]['image_id']
        region = indataframe.iloc[ix]['region']
        if type(region) is str: region = eval(region)
        imgLink = indataframe.iloc[ix]['image_source']
        image = readImage(imgLink)
        if image is None:
            med_r, med_g, med_b = None, None, None
            cv_r,  cv_g,  cv_b  = None, None, None
            med_h, med_s, med_v = None, None, None
        else:
            (med_r, med_g, med_b) = imgMedian( image,  region, incolor = 'BGR')
            (cv_r, cv_g, cv_b) =  imgCoVar( image, region, incolor = 'BGR')
            imghsv = img2HSV( image )
            (med_h, med_s, med_v) = imgMedian(imghsv, region)
#            print((med_r, med_g, med_b),  (cv_r, cv_g, cv_b), (med_h, med_s, med_v) )
        DataDict = {'image_id':imgID, 'image_source':imgLink,
                    'med_r':med_r, 'med_g':med_g, 'med_b':med_b,
                    'med_h':med_h, 'med_s':med_s, 'med_v':med_v,
                    'cv_r':cv_r, 'cv_g':cv_g, 'cv_b':cv_b}
        paDataFrame = paDataFrame.append(DataDict,ignore_index=True)
        del DataDict

    return paDataFrame

