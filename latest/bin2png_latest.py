import os
import sys
import time
import shutil
import atexit
from datetime import datetime

import numpy as np
import pylab as plt

from PIL import Image
from matplotlib import cm

sys.path.append(os.path.dirname(os.getcwd()))
from scripts.bin2png import *

#imgpath = '/home/gb/irc_ctrl/latest'
imgpath = './'


def convert_latest():
    fnames = ['latest_cam1', 
              'latest_cam2', 
              'latest_cam3', 
              'latest_cam4' ]
    arrs = []
    ftimes = []
    for fname in fnames:
        arrtmp = load_bin(imgpath + fname)
        arrtmp = scale_arr(arrtmp)
        if len(arrtmp) == 0:
            arrtmp = np.zeros((120,160))
        arrs.append(arrtmp)
        ftimes.append(datetime.utcfromtimestamp(os.path.getmtime(fname)).isoformat())
    
    arrs = np.array(arrs)
    arrs[0] = arrs[0][::-1, ::-1]
    arrs[1] = arrs[1][::-1, ::-1]
    imgs = []
    for arr in arrs:
        imgtmp = arr2png(arr)
        if np.min(arr) == np.max(arr):
            imgtmp = blankimg(imgtmp, 'offline')
        imgs.append(np.array(imgtmp))
        
    #arr1 = np.concatenate((arr[1], arr[0]), axis=2)
    #arr2 = np.concatenate((arr[2], arr[3]), axis=2)
    #arr = np.concatenate((arr1, arr2), axis=1)
    #arr2png(arr, 'image.png', imgpath)
    img1 = np.concatenate((imgs[1], imgs[0]), axis=1)
    img2 = np.concatenate((imgs[2], imgs[3]), axis=1)
    img = np.concatenate((img1, img2), axis=0)
    img = Image.fromarray(img, 'RGB')

    writepng_pil(img, 'image.png' , outpath='./')
    

    with open(imgpath+'imagetime.txt', 'w') as f:
        for i, ftime in enumerate(ftimes):
            if i == 0:
                tmp = ftime + " Cam 1 TR"
            elif i == 3:
                tmp = ftime + " Cam 4 BR"
            elif i  == 1:
                tmp = ftime + " Cam 2 TL"
            elif i == 2:
                tmp = ftime + " Cam 3 BL"
            f.write("%s\n" % tmp);


def convert_latest_custom_scaling():
    fnames = ['latest_cam1', 
              'latest_cam2', 
              'latest_cam3', 
              'latest_cam4' ]
    arrs = []
    ftimes = []
    for fname in fnames:
        arrtmp = load_bin(imgpath + fname)
        if len(arrtmp) == 0:
            arrtmp = np.zeros((120,160))
        arrs.append(arrtmp)
        ftimes.append(datetime.utcfromtimestamp(os.path.getmtime(fname)).isoformat())

    vmin = np.min(arrs[3])
    vmax = np.max(arrs[3])
    for i, arr in enumerate(arrs):
        arrs[i] = scale_arr(arr)
        #arrs[i] = scale_arr(arr, [0, 25])
    
    arrs = np.array(arrs)
    arrs[0] = arrs[0][::-1, ::-1]
    arrs[1] = arrs[1][::-1, ::-1]
    imgs = []
    for arr in arrs:
        imgtmp = arr2png(arr)
        if np.min(arr) == np.max(arr):
            imgtmp = blankimg(imgtmp, 'offline')
        imgs.append(np.array(imgtmp))
        
    #arr1 = np.concatenate((arr[1], arr[0]), axis=2)
    #arr2 = np.concatenate((arr[2], arr[3]), axis=2)
    #arr = np.concatenate((arr1, arr2), axis=1)
    #arr2png(arr, 'image.png', imgpath)
    img1 = np.concatenate((imgs[1], imgs[0]), axis=1)
    img2 = np.concatenate((imgs[2], imgs[3]), axis=1)
    img = np.concatenate((img1, img2), axis=0)
    img = Image.fromarray(img, 'RGB')

    writepng_pil(img, 'image.png' , outpath='./')
    

    with open(imgpath+'imagetime.txt', 'w') as f:
        for i, ftime in enumerate(ftimes):
            if i == 0:
                tmp = ftime + " Cam 1 TR"
            elif i == 3:
                tmp = ftime + " Cam 4 BR"
            elif i  == 1:
                tmp = ftime + " Cam 2 TL"
            elif i == 2:
                tmp = ftime + " Cam 3 BL"
            f.write("%s\n" % tmp);

@atexit.register
def goodbye():
    print ('bin2png_latest.py is stopped.')


def main():
    print ('bin2png_latest.py is started.')
    while 1:
        try:
            try:
                #convert_latest()
                convert_latest_custom_scaling()
            except TypeError:
                continue

            try:
                shutil.copy2(imgpath+'image.png', '/var/www/html/image')
                shutil.copy2(imgpath+'imagetime.txt', '/var/www/html/image')
            except PermissionError:
                print ("Cannot copy the files due to the permission error...")
                continue
                

            time.sleep(1)
        except KeyboardInterrupt:
            exit(0)


if __name__=='__main__':
    main()

