import os
import sys
import time
import shutil
from datetime import datetime

import numpy as np
import pylab as plt

from PIL import Image
from matplotlib import cm

imgpath = '/home/gb/irc_ctrl/latest/'

def load_bin(fname):
    f = open(fname, 'rb')
    
    arr = []
    tmp = []

    while True:
        data = f.read(2)

        if data == b'':
            break

        val = int.from_bytes(data, byteorder='little')

        tmp.append(val)
        if len(tmp) == 19200:
            arr.append(np.array(tmp).reshape((120, 160)))
            tmp = []

    f.close()

    return arr
   

def writepng_pil(im, ofname):
    vmin = np.min(im)
    vmax = np.max(im)
    im = np.array((im - 27315) / 3000 * 255, dtype=np.uint8)
    arr = cm.rainbow(im)[:,:,:3]*255
    arr = np.array(arr, dtype=np.uint8)
    img = Image.fromarray(arr, 'RGB')
    img.save(ofname)


def arr2png(arr, fname, outpath='./png'):
    for i, im in enumerate(arr):
        ofname = f'{outpath}/{fname}'
        writepng_pil(im, ofname)


def convert_dir(path):
    flist = os.listdir(path)
    flist.sort()
    for fname in flist:
        infile = os.path.join(path, fname)
        print (infile)
        convert_bin(infile)


def convert_bin(fname):
    arr = load_bin(fname)
    ofname = fname.split('/')[-1] 
    arr2png(arr, ofname)


def convert_latest():
    fnames = ['latest_cam1', 
              'latest_cam2', 
              'latest_cam3', 
              'latest_cam4' ]
    arr = []
    ftimes = []
    for fname in fnames:
        arr.append(load_bin(imgpath+fname))
        ftimes.append(datetime.utcfromtimestamp(os.path.getmtime(fname)).isoformat())
    
    arr = np.array(arr)
    arr = np.array(arr)
    arr[0] = arr[0][:, ::-1, ::-1]
    arr[1] = arr[1][:, ::-1, ::-1]
    arr1 = np.concatenate((arr[1], arr[0]), axis=2)
    arr2 = np.concatenate((arr[2], arr[3]), axis=2)
    arr = np.concatenate((arr1, arr2), axis=1)
    arr2png(arr, 'image.png', imgpath)

    with open(imgpath+'imagetime.txt', 'w') as f:
        for i, ftime in enumerate(ftimes):
            if i == 0:
                tmp = ftime + " Cam 1 TR (OFF)"
            elif i == 3:
                tmp = ftime + " Cam 4 BR"
            elif i  == 1:
                tmp = ftime + " Cam 2 TL"
            elif i == 2:
                tmp = ftime + " Cam 3 BL"
            f.write("%s\n" % tmp);

def main():
    print ('bin2png_latest.py is running')
    while 1:
        try:
            try:
                convert_latest()
            except TypeError:
                continue
            shutil.copy2(imgpath+'image.png', '/var/www/html/image')
            shutil.copy2(imgpath+'imagetime.txt', '/var/www/html/image')
            time.sleep(9)
        except KeyboardInterrupt:
            print ('done')
            exit(0)

if __name__=='__main__':
    main()

