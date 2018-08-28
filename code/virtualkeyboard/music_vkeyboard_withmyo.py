# Macros
########
CAMERA_INDEX=1
REFRESH_INTERVAL=0.001
velocity = 127
prevvar = 0
THRESHOLD = 200
MIN_VELOCITY = 80
MAX_VELOCITY = 127

# Keymap
########

keymap = {
    1:66,
    2:67,
    3:68,
    4:69,
    5:70,
    6:71,
    7:72,
    8:73,
    9:74,
    10:91
}

# Import list
#############
# In[1]:
import serial
import time
import fluidsynth
from vkfrontend import *
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.image as mpimage
import numpy as np
import colortools as ct
import numpy as np
import sys, os
import termios, fcntl
import select
import cv2
import math
import scipy.ndimage as ndimage
from myfunctions import *
# In[2]:
from numpy import logical_and as andn

# Functions
###########
def close(event):
    if event.key == 'q':
        plt.close(event.canvas.figure)
        return(0)
    else:
        return(1)

def play_key (fs,key,velocity):
    return_string = ""
    fs.noteon(0, key, velocity)
    return_string = ";Key: " + str(key)
    return return_string

# Main
######

fs = fluidsynth.Synth()
fs.start()
fs.start(driver="alsa")
sfid = fs.sfload("FluidR3_GM.sf2")
#sfid = fs.sfload("Nice-Keys-Ultimate-V2.3.sf2")
fs.program_select(0, sfid, 0, 0)

# Start Myoware sensor serial capture
#####################################

ser = serial.Serial('/dev/ttyACM0')
fd = sys.stdin.fileno()
newattr = termios.tcgetattr(fd)
newattr[3] = newattr[3] & ~termios.ICANON
newattr[3] = newattr[3] & ~termios.ECHO
termios.tcsetattr(fd, termios.TCSANOW, newattr)
oldterm = termios.tcgetattr(fd)
oldflags = fcntl.fcntl(fd, fcntl.F_GETFL)
fcntl.fcntl(fd, fcntl.F_SETFL, oldflags | os.O_NONBLOCK)

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
    final_string = ""
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
    sm = ct.rgb_to_l( image ) < 0.3
    shadow_mask=sm
    shadow_thresh=0.05*10
    size=10*0.5
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
            if touches[i,1]>134 and touches[i,1]<259:
                if touches[i,0]>31 and touches[i,0]<156:
                    var = 1
                    
                elif touches[i,0]>156 and touches[i,0]<295:
                    var =4
                elif touches[i,0]>295 and touches[i,0]<431:
                    var =7
            elif touches[i,1]>259 and touches[i,1]<393:
                if touches[i,0]>31 and touches[i,0]<156:
                    var =2
                elif touches[i,0]>156 and touches[i,0]<295:
                    var =5
                elif touches[i,0]>295 and touches[i,0]<431:
                    var = 8
            elif touches[i,1]>392 and touches[i,1]<523:
                if touches[i,0]>31 and touches[i,0]<156:
                    var = 3
                elif touches[i,0]>156 and touches[i,0]<295:
                    var = 6
                elif touches[i,0]>295 and touches[i,0]<431:
                    var=9
    else:
        var=0
                
    if (var != prevvar and var!= 0):
        ser_bytes = ser.readline()
        try:
            converted_data = int(ser_bytes[0:4],16)
        except:
            print ("FAILED to convert Myoware sensor output to integer")
            converted_date = 100

        if (converted_data >= THRESHOLD):
            final_string = "Sensor value crossed threshold;"+str(converted_data)
            final_string = final_string + play_key(fs,keymap[var],MAX_VELOCITY)
        else:
            final_string = "Boring! Sensor value;" + str(converted_data)
            final_string = final_string + play_key(fs,keymap[var],MIN_VELOCITY)
        print (final_string)
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
