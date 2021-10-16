import os
import sys

import numpy as np
import pylab as plt

from PIL import Image, ImageDraw
from matplotlib import cm


def load_bin_org(fname):
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

   
def parse_header(header):
    hdrl = header.decode('ascii')
    hdrl = hdrl.split('\n')
    if hdrl[-1][0] == '\x00':
        hdrl = hdrl[:-1]

    header_dict = {}
    for hdrc in hdrl:
        hdrt = hdrc.split(' : ') 
        hdrt[0] = hdrt[0].strip().replace('#', '')
        hdrt[1] = hdrt[1].strip()
        try:
            hdrt[1] = int(hdrt[1])
        except ValueError:
            pass 
        header_dict[hdrt[0]] = hdrt[1]
    
    return header_dict


def load_bin(fname, read_header=False):
    f = open(fname, 'rb')
    
    arr = []
    tmp = []

    data = f.read()

    header = {}
    if data[:7] == b'#hdrlen':
        hdrlen = int(data[12:100].split(b'\n')[0])
        header = parse_header(data[:hdrlen])
        data = data[hdrlen:]

    try:
        if header['status'] != "online":
            data = b'\x00'*38400
    except KeyError:
        pass
        

    for i in range(len(data)//2):
        d = data[2*i:2*(i+1)]
        val = int.from_bytes(d, byteorder='little')

        tmp.append(val)
        
        if len(tmp) == 19200:
            #arr.append(np.array(tmp).reshape((120, 160)))
            arr = np.array(tmp).reshape((120, 160))
            tmp = []
            break

    f.close()

    if read_header:
        return arr, header
    else:
        return arr


def scale_arr(arr, minmax=None):
    imt = (np.array(arr) - 27315) / 100 
    if minmax is None:
        try:
            vmin = np.min(imt)
            vmax = np.max(imt)
        except:
            vmin = 0;
            vmax = 1;
    else:
        vmin, vmax = minmax

    imt[imt<vmin] = vmin
    imt[imt>vmax] = vmax
    vdiff = vmax - vmin

    if vdiff == 0:
        vdiff = 1

    arr_scaled = (imt - vmin) / vdiff

    return arr_scaled


def writepng_pil(img, fname, outpath='./'):
    #ofname = f'{outpath}/{fname[-4:]}-overwrite.png'
    ofname = f'{outpath}/{fname}'
    if ofname[-4:] !='.png':
        ofname += '.png'

    img.save(ofname)


def arr2png_org(arr, fname, outpath='./'):
    for i, im in enumerate(arr):
        #ofname = f'{outpath}/{fname[-4:]}-overwrite.png'
        ofname = f'{outpath}/{fname}'
        if ofname[-4:] !='.png':
            ofname += '.png'

        writepng_pil(im, ofname)


def arr2png(arr):
    #tmp = cm.rainbow(imt)[:,:,:3] * 255
    tmp = cm.plasma(arr)[:,:,:3] * 255
    tmp = np.array(tmp, dtype=np.uint8)
    img = Image.fromarray(tmp, 'RGB')
    #img = Image.fromarray(np.uint8(imt*255), 'L')

    return img


def blankimg(img, text=None):
    arr = np.array(img)
    arr[:] = 0
    img = Image.fromarray(arr, 'RGB')

    if text != None:
        img_draw = ImageDraw.Draw(img)
        img_draw.text((10, 10), text, fill='white')
        
    return img


def convert_dir(path):
    flist = os.listdir(path)
    flist.sort()
    for fname in flist:
        infile = os.path.join(path, fname)
        print (infile)
        convert_bin(infile)


def convert_bin(fname):
    arr, header = load_bin(fname, read_header=True)
    if len(arr) == 0:
        return 
    arr = scale_arr(arr)
    img = arr2png(arr)

    ofname = fname.split('/')[-1] 
    writepng_pil(img, ofname, './')


def main():
    arg = sys.argv[1]

    if os.path.isdir(arg):
        path = arg
        convert_dir(path)
    else:
        fname = arg
        convert_bin(fname)


if __name__=='__main__':
    main()

