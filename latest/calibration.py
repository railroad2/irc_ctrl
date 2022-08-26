import os
import sys

import numpy as np
import pylab as plt
import glob

from PIL import Image, ImageDraw
from matplotlib import cm
import cv2
import numpy as np

sys.path.append(os.path.dirname(os.getcwd()))
from scripts.bin2png import *

pts = None

ang=22/180*np.pi
tan=np.tan(ang)
vec2=np.array([0,1,-tan])
vec3=np.array([tan,tan,1])
vec1=np.cross(vec2,vec3)
vec1=vec1/np.linalg.norm(vec1)
vec2=vec2/np.linalg.norm(vec2)
vec3=vec3/np.linalg.norm(vec3)
mat4=[vec1,vec2,vec3]
mat4=np.transpose(mat4)


vec2=np.array([0,1,-tan])
vec3=np.array([-tan,tan,1])
vec1=np.cross(vec2,vec3)
vec1=vec1/np.linalg.norm(vec1)
vec2=vec2/np.linalg.norm(vec2)
vec3=vec3/np.linalg.norm(vec3)
mat1=[vec1,vec2,vec3]
mat1=np.transpose(mat1)


vec2=np.array([0,1,tan])
vec3=np.array([-tan,-tan,1])
vec1=np.cross(vec2,vec3)
vec1=vec1/np.linalg.norm(vec1)
vec2=vec2/np.linalg.norm(vec2)
vec3=vec3/np.linalg.norm(vec3)
mat2=[vec1,vec2,vec3]
mat2=np.transpose(mat2)


vec2=np.array([0,1,tan])
vec3=np.array([tan,-tan,1])
vec1=np.cross(vec2,vec3)
vec1=vec1/np.linalg.norm(vec1)
vec2=vec2/np.linalg.norm(vec2)
vec3=vec3/np.linalg.norm(vec3)
mat3=[vec1,vec2,vec3]
mat3=np.transpose(mat3)




theta = 0
sin = np.sin(theta*180/np.pi)
cos = np.cos(theta*180/np.pi)
rot = np.array([[cos,sin,0],
                [-sin,cos,0],
                [0,0,1]])


def show_img(arr1,arr2,arr3,arr4,z=150,delta=0):
  
  global mat1
  global mat2
  global mat3
  global mat4

  (h,w) = np.shape(arr1)[:2]

  z1=z
  z2=z
  newbox=[0,0,0,0]

  pts11=np.float32([[0,0],[h,0],[0,w],[h,w]])
  pts12 = []

  for i in pts11:
      i = i-[h/2,w/2]
      tmp=np.array([i[0],i[1],z1])
      tmp=mat1@tmp
      tmp = tmp*z2/tmp[2]
      pts12.append(tmp[:2])
  pts12=np.float32(pts12)

  newbox[2]=pts12[2]



  pts21=np.float32([[0,0],[h,0],[0,w],[h,w]])
  pts22 = []

  for i in pts21:
     i = i-[h/2,w/2]
     tmp=np.array([i[0],i[1],z1])
     tmp=mat2@tmp
     tmp = tmp*z2/tmp[2]
     pts22.append(tmp[:2])
  pts22=np.float32(pts22)


  newbox[0]=pts22[0]


  pts31=np.float32([[0,0],[h,0],[0,w],[h,w]])
  pts32 = []

  for i in pts31:
     i = i-[h/2,w/2]
     tmp=np.array([i[0],i[1],z1])
     tmp=mat3@tmp
     tmp = tmp*z2/tmp[2]
     pts32.append(tmp[:2])
  pts32=np.float32(pts32)


  newbox[1]=pts32[1]

  pts41=np.float32([[0,0],[h,0],[0,w],[h,w]])
  pts42 = []

  for i in pts41:
     i = i-[h/2,w/2]
     tmp=np.array([i[0],i[1],z1])
     tmp=mat4@tmp
     tmp = tmp*z2/tmp[2]
     pts42.append(tmp[:2])
  pts42=np.float32(pts42)

  newbox[3]=pts42[3]

  nh,nw=newbox[3]-newbox[0]



  pts12=pts12+np.float32([nh/2,nw/2])
  pts22=pts22+np.float32([nh/2,nw/2])
  pts32=pts32+np.float32([nh/2-delta,nw/2])
  pts42=pts42+np.float32([nh/2-delta,nw/2])

  nh=np.float32(nh-delta)


  pts11=pts11[:,::-1]
  pts21=pts21[:,::-1]
  pts31=pts31[:,::-1]
  pts41=pts41[:,::-1]

  pts12=pts12[:,::-1]
  pts22=pts22[:,::-1]
  pts32=pts32[:,::-1]
  pts42=pts42[:,::-1]





  M1 = cv2.getPerspectiveTransform(pts11, pts12)
  M2 = cv2.getPerspectiveTransform(pts21, pts22)
  M3 = cv2.getPerspectiveTransform(pts31, pts32)
  M4 = cv2.getPerspectiveTransform(pts41, pts42)

  dst1 = cv2.warpPerspective(arr1, M1, (nw,nh))

  dst2 = cv2.warpPerspective(arr2, M2, (nw,nh))

  dst3 = cv2.warpPerspective(arr3, M3, (nw,nh))

  dst4 = cv2.warpPerspective(arr4, M4, (nw,nh))

  ones=np.ones_like(arr1)

  back1 = cv2.warpPerspective(ones, M1, (nw,nh))

  back2 = cv2.warpPerspective(ones, M2, (nw,nh))

  back3 = cv2.warpPerspective(ones, M3, (nw,nh))

  back4 = cv2.warpPerspective(ones, M4, (nw,nh))

  #back1 = np.ceil(back1)

  #back2 = np.ceil(back2)

  #back3 = np.ceil(back3)

  #back4 = np.ceil(back4)

  back = back1+back2+back3+back4

  dst=(dst1+dst2+dst3+dst4)/back


  img=arr2png(dst)
  img = np.array(img)
  img=cv2.cvtColor(img,cv2.COLOR_RGB2BGR)
  #cv2_imshow(img)
  return(img)




def find_pts(z=150,delta=0):
  global mat1
  global mat2
  global mat3
  global mat4

  h,w=120,160

  z1=z
  z2=z
  newbox=[0,0,0,0]

  pts11=np.float32([[0,0],[h,0],[0,w],[h,w]])
  pts12 = []

  for i in pts11:
      i = i-[h/2,w/2]
      tmp=np.array([i[0],i[1],z1])
      tmp=mat1@tmp
      tmp = tmp*z2/tmp[2]
      pts12.append(tmp[:2])
  pts12=np.float32(pts12)

  newbox[2]=pts12[2]



  pts21=np.float32([[0,0],[h,0],[0,w],[h,w]])
  pts22 = []

  for i in pts21:
     i = i-[h/2,w/2]
     tmp=np.array([i[0],i[1],z1])
     tmp=mat2@tmp
     tmp = tmp*z2/tmp[2]
     pts22.append(tmp[:2])
  pts22=np.float32(pts22)


  newbox[0]=pts22[0]


  pts31=np.float32([[0,0],[h,0],[0,w],[h,w]])
  pts32 = []

  for i in pts31:
     i = i-[h/2,w/2]
     tmp=np.array([i[0],i[1],z1])
     tmp=mat3@tmp
     tmp = tmp*z2/tmp[2]
     pts32.append(tmp[:2])
  pts32=np.float32(pts32)


  newbox[1]=pts32[1]

  pts41=np.float32([[0,0],[h,0],[0,w],[h,w]])
  pts42 = []

  for i in pts41:
     i = i-[h/2,w/2]
     tmp=np.array([i[0],i[1],z1])
     tmp=mat4@tmp
     tmp = tmp*z2/tmp[2]
     pts42.append(tmp[:2])
  pts42=np.float32(pts42)

  newbox[3]=pts42[3]

  nh,nw=newbox[3]-newbox[0]



  pts12=pts12+np.float32([nh/2,nw/2])
  pts22=pts22+np.float32([nh/2,nw/2])
  pts32=pts32+np.float32([nh/2-delta,nw/2])
  pts42=pts42+np.float32([nh/2-delta,nw/2])

  nh=np.float32(nh-delta)


  pts11=pts11[:,::-1]
  pts21=pts21[:,::-1]
  pts31=pts31[:,::-1]
  pts41=pts41[:,::-1]

  pts12=pts12[:,::-1]
  pts22=pts22[:,::-1]
  pts32=pts32[:,::-1]
  pts42=pts42[:,::-1]




  I1 = cv2.getPerspectiveTransform(pts12, pts11)
  M1 = cv2.getPerspectiveTransform(pts11, pts12)
  I2 = cv2.getPerspectiveTransform(pts22, pts21)
  M2 = cv2.getPerspectiveTransform(pts21, pts22)
  I3 = cv2.getPerspectiveTransform(pts32, pts31)
  M3 = cv2.getPerspectiveTransform(pts31, pts32)
  I4 = cv2.getPerspectiveTransform(pts42, pts41)
  M4 = cv2.getPerspectiveTransform(pts41, pts42)


  ones=np.ones((h,w))

  back1 = cv2.warpPerspective(ones, M1, (nw,nh))
  
  back2 = cv2.warpPerspective(ones, M2, (nw,nh))

  back3 = cv2.warpPerspective(ones, M3, (nw,nh))



  back1 = np.ceil(back1)

  back2 = np.ceil(back2)

  back3 = np.ceil(back3)

  back = back1+back2+back3


  back = (back==3).astype('int0')

  back = np.float32(back)




  arr = cv2.warpPerspective(back, I2, (160,120))

  arr = np.ceil(arr)
  return(arr)



def center_cal(arrs,z=150):
  global pts
  if pts == None:
    arr = find_pts(z)
    val1 = np.mean(arrs[0][::-1,::][arr==1])
    val2 = np.mean(arrs[1][::-1,::-1][arr==1])
    val3 = np.mean(arrs[2][::-1,::][arr==1])
    val4 = np.mean(arrs[3][::-1,::-1][arr==1])
    
    mean = (val1+val2+val3+val4)/4
    

    dev1=val1-mean
    dev2=val2-mean
    dev3=val3-mean
    dev4=val4-mean

    return([arrs[0]-dev1,arrs[1]-dev2,arrs[2]-dev3,arrs[3]-dev4])





def corner_cal(arrs):
    h, w = arrs[0].shape
    corner1=arrs[0][h-1][0]
    corner2=arrs[1][h-1][w-1]
    corner3=arrs[2][h-1][0]
    corner4=arrs[3][h-1][w-1]

    corner_avg=np.average([corner1,corner2,corner3,corner4])

    arrs[0]=arrs[0]-corner1
    arrs[1]=arrs[1]-corner2
    arrs[2]=arrs[2]-corner3
    arrs[3]=arrs[3]-corner4

    arrs = arrs + corner_avg
    return arrs
