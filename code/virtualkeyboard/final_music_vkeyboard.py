#!/bin/env python3.6

# Macros
########
THRESHOLD = 30
KEYS=5
CAMERA_INDEX=1
REFRESH_INTERVAL=0.01
velocity = 127
prevvar = 0
XBEGIN = 73
XEND = 573

XBEGIN = 55
XEND = 580

SHADOW_MASS_THRESHOLD = 0.3
#SHADOW_THRESHOLD = 10
SHADOW_THRESHOLD = 3
#SHADOW_MASK_THRESHOLD = 0.5
SHADOW_MASK_THRESHOLD = 1

# Keymap
########

musickeymap = {
    1:66,
    2:68,
    3:70,
    4:71,
    5:73,
    6:75,
    7:77,
    8:78,
    9:80,
    10:82
}

# Import list
#############
# In[1]:
import time
import fluidsynth
from vkfrontend import *
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.image as mpimage
import numpy as np
import colortools as ct
import numpy as np
import cv2
import math
import scipy.ndimage as ndimage
from myfunctions import *
# In[2]:
from numpy import logical_and as andn
#################################################################
# In[2]:
# For detecting thr reference points in the keyword mesh
if 'cap1' in locals():
    print("Camera is Release: Good to GO!")
    cap1.release()
cap1 = cv2.VideoCapture(1)
for i in range(10):
    image=cap1.read()[1]
    time.sleep(0.01)
gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
plt.figure(11)
plt.imshow(gray_image)
plt.show()
plt.figure(12)
a=gray_image<THRESHOLD
plt.imshow(a)
plt.show()
arr=np.argwhere(a)
p0=arr[0,:]
c1=[]
c2=[]
c3=[]
c4=[]
for i in range(arr.shape[0]):
    if(arr[i,0]<240 and arr[i,1]<320):
        c1.append([arr[i,0],arr[i,1]])
    if(arr[i,0]>240 and arr[i,1]>320):
        c2.append(arr[i,:])
    if(arr[i,0]<240 and arr[i,1]>320):
        c3.append(arr[i,:])
    if(arr[i,0]>240 and arr[i,1]<320):
        c4.append(arr[i,:])
p1=np.sum(np.matrix(c1),axis=0)/len(c1)
p2=np.sum(np.matrix(c2),axis=0)/len(c2)
p3=np.sum(np.matrix(c3),axis=0)/len(c3)
p4=np.sum(np.matrix(c4),axis=0)/len(c4)
print("p1 is " + str(p1))
print("p2 is " + str(p2))
print("p3 is " + str(p3))
print("p4 is " + str(p4))
plt.plot(p1[0,1],p1[0,0],'o',markersize=6,color='red')# first points
plt.plot(p2[0,1],p2[0,0],'o',markersize=6,color='red') # third points
plt.plot(p3[:,1],p3[:,0],'o',markersize=6,color='red') # second points
plt.plot(p4[0,1],p4[0,0],'o',markersize=6,color='red') # forth points
#############################################################################
x1 = p1[0,0]
x2 = p3[0,0]
y1 = p1[0,1]
y2 = p4[0,1]
#width = (x2 - x1)/3;
width = (XEND -XBEGIN)/KEYS;
keymap=[]
key=KEYS
print("Printing the keymap")
print("###################")
for ii in range(0,KEYS):
    xbegin = x1 + (ii) * width
    xend = x1 + (ii+1) * width
    keymap.append([xbegin,xend,key]);
    key=key-1
    print ([xbegin,xend,key])
################################################################
# Functions
###########
def close(event):
    if event.key == 'q':
        plt.close(event.canvas.figure)
        return(0)
    else:
        return(1)

# Main
######

fs = fluidsynth.Synth()
fs.start()
fs.start(driver="alsa")
#sfid = fs.sfload("FluidR3_GM.sf2")
sfid = fs.sfload("Nice-Keys-Ultimate-V2.3.sf2")
#sfid = fs.sfload("styvell-saxoaltovib.sf2")
#fs.program_select(0, sfid, 1, 65)  # styvell-saxoaltovib.sf2 : Sax
#fs.program_select(0, sfid, 0, 23)  # Nice-Keys-Ultimate-V2.3.sf2 : Slow Strings
#fs.program_select(0, sfid, 0, 20)  # Nice-Keys-Ultimate-V2.3.sf2 : SoftPad
fs.program_select(0, sfid, 0, 38)  # Nice-Keys-Ultimate-V2.3.sf2 : SoftPad
#fs.program_select(0, sfid, 0, 0)

#fs.noteon(0, keymap[6], velocity)
#time.sleep(0.500)

cid = plt.gcf().canvas.mpl_connect("key_press_event", close)
if 'cap1' in locals():
    print("Camera is Release: Good to GO!")
    cap1.release()
cap1 = cv2.VideoCapture(CAMERA_INDEX)
fig=plt.figure(1)
ax1=fig.add_subplot(221)
ax2=fig.add_subplot(222)
ax3=fig.add_subplot(223)
image=cap1.read()[1]
ax2.imshow(image)
ax1.axis('off')
ax2.axis('off')
plt.ion()
step =0
touches = 0
var = 0
while True:
    touch = touches
    cid = plt.gcf().canvas.mpl_connect("key_press_event", close)
    if(cid==7):
        break
    image=cap1.read()[1]
    bw = locate_hand_1(image)
    downsample = 15
    ctrs = find_contours( bw )
    ctr_pts = []
    for ctr in ctrs:
        ctr_pts = ctr_pts + ctr[::downsample]
    c = np.matrix(ctr_pts)
    ax1.clear()
    if(len(ctr_pts)>0):
        ax1.plot(c[:,1],c[:,0],'o',markersize=1,color='green')
    tips = []
    for ctr in ctrs:
        tips = tips + contour_to_tips( ctr[::downsample], \
                                             ang_thresh=3.1415/2, step=1 )
    tips =group_tips( tips, radius=20 )
    tips_m=np.matrix(tips)
    if(len(tips)>0):
        ax1.plot(tips_m[:,1],tips_m[:,0],'g+',markersize=6,color='red')
    ax1.imshow(image)
    ax1.axis('off')
    # Shadow analysis part 
    sm = ct.rgb_to_l( image ) < SHADOW_MASS_THRESHOLD
    shadow_mask=sm
    shadow_thresh=0.05*SHADOW_THRESHOLD
    size=10*SHADOW_MASK_THRESHOLD
    ax2.clear()
    touches=np.matrix(shadow_det(tips,shadow_mask,shadow_thresh,size))
    if(touches.shape[1]>0):
        index=andn(andn(touches[:,0]>10,touches[:,0]<470),\
                   andn(touches[:,1]>10,touches[:,1]<630))
        touches=touches[np.where(index),:][0]
    ax2.imshow(image)
    ax2.axis('off')
    if(touches.shape[1]>0):
        ax2.plot(touches[:,1],touches[:,0],'o',markersize=6,color='red')
        ax2.axis('off')
    plt.pause(REFRESH_INTERVAL)
    if(touches.shape[1]>0):
        for i in range(touches.shape[0]):
            inputkey_coord=np.array([touches[i,0],touches[i,1]])
            keypressed=0
            for i in range(KEYS):
                cond1 = keymap[i][0] <= inputkey_coord[1] < keymap[i][1]
                #cond2 = keymap[i][2] <= inputkey_coord[0] < keymap[i][3]
                #if cond1 and cond2:
                if cond1:
                    print("Key pressed was " + str(keymap[i][2]))
                    var=keymap[i][2]
    else:
        var=0
                
    if (var != prevvar):
        if (var != 0):
            fs.noteon(0, musickeymap[var], velocity)
        if (prevvar != 0):
            fs.noteoff(0, musickeymap[prevvar])
        #time.sleep(0.500)

    prevvar = var

    ax3.clear()
    ax3.axis('off')
    plt.subplot(223)
    plt.text(0.8,0.1, str(var), fontsize =100)
    ax3.axis('off')
    plt.show()
plt.ioff() # due to infinite loop, this gets never called.
cap1.release()
