import os, sys
import numpy as np
import matplotlib.pyplot as plt
import cv2
import healpy as hp
from healpy.newvisufunc import projview, newprojplot
import astropy
from astropy import units as u
import glob
sys.path.append(os.path.dirname(os.getcwd()))
from scripts.bin2png import *
from calibration import*
from astropy.coordinates import SkyCoord
from datetime import datetime

thresh_TF = True
thresh = np.ones((120, 160))

def arr2img(arr):
  min = np.min(arr)
  max = np.max(arr)
  return np.uint8(255*scale_arr_nonzero(arr)),min,max


def corner_del_threshold(arrs):
  imgs,min,max=arr2img(arrs)
  t1, thresh1 = cv2.threshold(imgs[0], -1, 1,  cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
  t2, thresh2 = cv2.threshold(imgs[1], -1, 1,  cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
  t3, thresh3 = cv2.threshold(imgs[2], -1, 1,  cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
  t4, thresh4 = cv2.threshold(imgs[3], -1, 1,  cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)

  arrs[0] = arrs[0]*thresh1
  arrs[1] = arrs[1]*thresh2
  arrs[2] = arrs[2]*thresh3
  arrs[3] = arrs[3]*thresh4
  return arrs

def corner_del(arrs):
  global thresh_TF
  global thresh

  if thresh_TF:
    for i in range(0,160):
      for j in range(0,120):
        if(40*i+30*j < 1200):
          thresh[j,i] = 0
    thresh_TF = False

  arrs[0] = arrs[0]*thresh[::-1,::]
  arrs[1] = arrs[1]*thresh[::-1,::-1]
  arrs[2] = arrs[2]*thresh[::-1,::]
  arrs[3] = arrs[3]*thresh[::-1,::-1]
  return arrs


def new_size(arrs,ratio):
  arrs = np.float64(arrs)
  h,w = arrs[0].shape
  new_size = (ratio*w,ratio*h)

  new_arrs=[]
  new_arrs.append(cv2.resize(arrs[0],new_size,interpolation=cv2.INTER_NEAREST))
  new_arrs.append(cv2.resize(arrs[1],new_size,interpolation=cv2.INTER_NEAREST))
  new_arrs.append(cv2.resize(arrs[2],new_size,interpolation=cv2.INTER_NEAREST))
  new_arrs.append(cv2.resize(arrs[3],new_size,interpolation=cv2.INTER_NEAREST))
  return new_arrs



def scale_arr_nonzero(arr):
  arr = np.array(arr)
  shape = arr.shape
  arr = arr.flatten()
  vmax = np.max(arr[np.nonzero(arr)])
  vmin = np.min(arr[np.nonzero(arr)])
  arr = arr-vmin
  arr[arr<0]=0
  arr=arr/(vmax-vmin)
  arr = arr.reshape(shape)
  return arr


def arrs2deg(arrs,z):
  global mat1
  global mat2
  global mat3
  global mat4
  global rot
  h,w=arrs[0].shape
  x,y = np.mgrid[0:h,0:w]
  x=x.flatten()-(h-1)/2
  y=y.flatten()-(w-1)/2
  z = z*np.ones_like(x)

  [x1,y1,z1]=rot@mat1@[x,y,z]
  [x2,y2,z2]=rot@mat2@[x,y,z]
  [x3,y3,z3]=rot@mat3@[x,y,z]
  [x4,y4,z4]=rot@mat4@[x,y,z]
  ang1=hp.vec2ang(np.array([x1,y1,z1]).T,lonlat=True)
  ang2=hp.vec2ang(np.array([x2,y2,z2]).T,lonlat=True)
  ang3=hp.vec2ang(np.array([x3,y3,z3]).T,lonlat=True)
  ang4=hp.vec2ang(np.array([x4,y4,z4]).T,lonlat=True)
  return ang1,ang2,ang3,ang4


def ang2galatic(ang,time):
  time = astropy.time.Time(time,format='isot',scale='utc')
  eloc = astropy.coordinates.EarthLocation.from_geodetic(16.6291, 28.2916)
  hori = astropy.coordinates.AltAz(alt=ang[1]*u.degree,az=ang[0]*u.degree,location=eloc,obstime=time)
  sky = SkyCoord(hori,frame='altaz')
  sky = sky.transform_to(frame='galactic')
  return np.array([sky.l/u.degree,sky.b/u.degree])


def get_time(fnames):
  times=[datetime.utcfromtimestamp(os.path.getmtime(fname)).isoformat() for fname in fnames]
  return times

def make_pix(nside,arrs,times,AltAz=False):
  m = np.zeros(hp.nside2npix(nside))
  b = np.zeros(hp.nside2npix(nside))

  arr1 = arrs[0]
  arr2 = arrs[1]
  arr3 = arrs[2]
  arr4 = arrs[3]
  
  arr1=arr1[::-1,::-1]
  arr2=arr2[::-1,::-1]
  
  farr1=arr1.flatten()
  farr2=arr2.flatten()
  farr3=arr3.flatten()
  farr4=arr4.flatten()
    
  ang1,ang2,ang3,ang4 = arrs2deg(arrs,150)
  if AltAz==False:
    ang1 = ang2galatic(ang1,times[0])
    ang2 = ang2galatic(ang2,times[1])
    ang3 = ang2galatic(ang3,times[2])
    ang4 = ang2galatic(ang4,times[3])

    index1 = hp.ang2pix(nside,ang1[0],ang1[1],lonlat=True)
    index2 = hp.ang2pix(nside,ang2[0],ang2[1],lonlat=True)
    index3 = hp.ang2pix(nside,ang3[0],ang3[1],lonlat=True)
    index4 = hp.ang2pix(nside,ang4[0],ang4[1],lonlat=True)
  
  else:
    index1 = hp.ang2pix(nside,ang1[0],ang1[1],lonlat=True)
    index2 = hp.ang2pix(nside,ang2[0],ang2[1],lonlat=True)
    index3 = hp.ang2pix(nside,ang3[0],ang3[1],lonlat=True)
    index4 = hp.ang2pix(nside,ang4[0],ang4[1],lonlat=True)

  m[index1] += farr1
  m[index2] += farr2
  m[index3] += farr3
  m[index4] += farr4
  
  b[index1] += 1
  b[index2] += 1
  b[index3] += 1
  b[index4] += 1
  b += np.finfo(np.float64).tiny
  return m/b



def main():
  #fnames1 = glob.glob('/content/drive/MyDrive/CMB/2022-05-20/17/2022-05-20T17*-cam1')
  #fnames2 = glob.glob('/content/drive/MyDrive/CMB/2022-05-20/17/2022-05-20T17*-cam2')
  #fnames3 = glob.glob('/content/drive/MyDrive/CMB/2022-05-20/17/2022-05-20T17*-cam3')
  #fnames4 = glob.glob('/content/drive/MyDrive/CMB/2022-05-20/17/2022-05-20T17*-cam4')

  fnames = ['latest_cam1',
            'latest_cam2',
            'latest_cam3',
            'latest_cam4']

  arr1=np.array(load_bin(fnames[0]))
  arr2=np.array(load_bin(fnames[1]))
  arr3=np.array(load_bin(fnames[2]))
  arr4=np.array(load_bin(fnames[3]))
  
  arrs = [arr1,arr2,arr3,arr4]
  arrs = center_cal(arrs)
  arrs = corner_del(arrs)
  arrs = scale_arr_nonzero(arrs)
  arrs = new_size(arrs,1)
  
  times = get_time(fnames)

  nside=64
  m = make_pix(nside,arrs,times)
  projview(m,coord=["G","C"],graticule=True,graticule_labels=True,min=0,max=1,projection_type="mollweide")
  plt.savefig('Moll.png')
  plt.close()
  
  p = make_pix(nside,arrs,times,True)
  #projview(p,graticule=True,graticule_labels=True,min=0,max=1,projection_type="polar")
  #plt.savefig('Polar.png')
  #plt.close
  p[p==0] = hp.UNSEEN
  
  hp.visufunc.orthview(p,half_sky=True,rot=(0,90,0),min=0,max=1)
  hp.visufunc.graticule(30,60)
  for i in [30,60,90]:
    hp.visufunc.projtext(i*np.pi/180,270*np.pi/180,f'${i}^\circ$',rot=(0,90,0))
  for i in [0,60,120,180,240,300]:
    hp.visufunc.projtext(60*np.pi/180,i*np.pi/180,f'${i}^\circ$',rot=(0,90,0))
  plt.savefig('Orth.png')
  plt.close()


if __name__ == "__main__":
  main()
