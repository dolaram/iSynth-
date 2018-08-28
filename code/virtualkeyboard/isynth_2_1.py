THRESHOLD = 20
KEYS=5
# In[1]:
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
import time
from numpy import logical_and as andn
from scipy.spatial import ConvexHull
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
width = (x2 - x1)/3;
hight= (y2-y1)/3
keymap=[]
key=0
for ii in range(0,KEYS):
    xbegin = x1 + (ii) * width
    xend = x1 + (ii+1) * width
    key=key+1
    keymap.append([xbegin,xend,key]);
##############################################################################
# In[3]:
# Detecting the touches in real time
def close(event):
    if event.key == 'q':
        plt.close(event.canvas.figure)
        return(0)
    else:
        return(1)
cid = plt.gcf().canvas.mpl_connect("key_press_event", close)
if 'cap1' in locals():
    print("Camera is Release: Good to GO!")
    cap1.release()
cap1 = cv2.VideoCapture(1)
#ax1 = plt.subplot(1,2,1)
fig=plt.figure(1)
ax1=fig.add_subplot(221)
ax2=fig.add_subplot(222)
ax3=fig.add_subplot(223)
image=cap1.read()[1]
ax2.imshow(image)
#im2 = ax1.imshow(cap1.read()[1].astype('float32'))
ax1.axis('off')
ax2.axis('off')
#plt.ion()
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
#    if(len(ctr_pts)>0):
#        hull = ConvexHull(c)
#        hull_indices = np.unique(hull.simplices.flat)
#        hull_pts = c[hull_indices, :]
    ax1.clear()
    if(len(ctr_pts)>0):
        ax1.plot(c[:,1],c[:,0],'o',markersize=1,color='green')
    tips = []
    for ctr in ctrs:
        tips = tips + contour_to_tips( ctr[::downsample], \
                                             ang_thresh=3.1415/2, step=1 )
    tips =group_tips( tips, radius=20 )
    tips=list(set(tuple(tips)))
    
    tips_m=np.matrix(tips)
    if(len(tips)>0):
        ax1.plot(tips_m[:,1],tips_m[:,0],'g+',markersize=4,color='red')
    ax1.imshow(image)
    ax1.axis('off')
    # Shadow analysis part 
    sm = ct.rgb_to_l( image ) < 0.3
    shadow_mask=sm
    shadow_thresh=0.05*3#works good=0.05*10
    size=10#works good=10*0.5
    ax2.clear()
    #touches=np.matrix(shadow_det(tips,shadow_mask,shadow_thresh,size))
    touches=list(set(tuple(shadow_det(tips,shadow_mask,shadow_thresh,size))))
    touches=np.matrix(touches)
    if(touches.shape[1]>0):
        index=andn(andn(touches[:,0]>10,touches[:,0]<470),\
                   andn(touches[:,1]>10,touches[:,1]<630))
        touches=touches[np.where(index),:][0]
    ax2.imshow(image)
    ax2.axis('off')
    if(touches.shape[1]>0):
        ax2.plot(touches[:,1],touches[:,0],'o',markersize=4,color='red')
        ax2.axis('off')
    plt.pause(0.05)

    if(touches.shape[1]>0):
        for i in range(touches.shape[0]):
            inputkey_coord=np.array([touches[i,1],touches[i,0]])
            keypressed=0
            for i in range(KEYS):
                cond1 = keymap[i][0] <= inputkey_coord[1] < keymap[i][1]
                #cond2 = keymap[i][2] <= inputkey_coord[0] < keymap[i][3]
                #if cond1 and cond2:
                if cond1:
                    print("Key pressed was " + str(keymap[i][4]))
                    var=keymap[i][2]
    else:
        var=0
    ax3.clear()
    ax3.axis('off')
    plt.subplot(223)
    #plt.title('Value Pressed', loc = 'right')
    plt.text(0.8,0.1, str(var), fontsize =100)
    ax3.axis('off')
    plt.show()
#plt.ioff() # due to infinite loop, this gets never called.
cap1.release()
#################      
'''
    if(touches.shape[1]>0):
        for i in range(touches.shape[0]):
            if touches[i,1]>134 and touches[i,1]<259:
                #print(touches[i,1])
                if touches[i,0]>31 and touches[i,0]<156:
                    #print('1')
                    var = 1
                    
                elif touches[i,0]>156 and touches[i,0]<295:
                    var =4
                    #print('4')
                elif touches[i,0]>295 and touches[i,0]<431:
                    var =7
                    #print('7')
            elif touches[i,1]>259 and touches[i,1]<393:
                #print(touches[i,1])
                if touches[i,0]>31 and touches[i,0]<156:
                    var =2
                    #print('2')
                elif touches[i,0]>156 and touches[i,0]<295:
                    var =5
                    #print('5')
                elif touches[i,0]>295 and touches[i,0]<431:
                    var = 8
                    #print('8')
            elif touches[i,1]>392 and touches[i,1]<523:
                #print(touches[i,1])
                if touches[i,0]>31 and touches[i,0]<156:
                    var = 3
                    #print('3')
                elif touches[i,0]>156 and touches[i,0]<295:
                    var = 6
                    #print('6')
                elif touches[i,0]>295 and touches[i,0]<431:
                    var=9
                    #print('9')
    else:
        var=0
    ax3.clear()
    ax3.axis('off')
    plt.subplot(223)
    #plt.title('Value Pressed', loc = 'right')
    plt.text(0.8,0.1, str(var), fontsize =100)
    ax3.axis('off')
    plt.show()
#plt.ioff() # due to infinite loop, this gets never called.
cap1.release()
'''                


# In[2]:
## For detecting thr reference points in the keyword mesh
#gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#plt.figure(1)
#plt.imshow(gray_image)
#plt.show()
#plt.figure(2)
#a=gray_image<10
#plt.imshow(a)
#plt.show()
#arr=np.argwhere(gray_image<5)
#p0=arr[0,:]
#c1=[]
#c2=[]
#c3=[]
#c4=[]
#for i in range(arr.shape[0]):
#    if(arr[i,0]<240 and arr[i,1]<320):
#        c1.append([arr[i,0],arr[i,1]])
#    if(arr[i,0]>240 and arr[i,1]>320):
#        c2.append(arr[i,:])
#    if(arr[i,0]<240 and arr[i,1]>320):
#        c3.append(arr[i,:])
#    if(arr[i,0]>240 and arr[i,1]<320):
#        c4.append(arr[i,:])
#p1=np.sum(np.matrix(c1),axis=0)/len(c1)
#p2=np.sum(np.matrix(c2),axis=0)/len(c2)
#p3=np.sum(np.matrix(c3),axis=0)/len(c3)
#p4=np.sum(np.matrix(c4),axis=0)/len(c4)
#print(p1,p2,p4,p3)
#plt.plot(p1[:,1],p1[:,0],'o',markersize=6,color='red')# first points
#plt.plot(p2[:,1],p2[:,0],'o',markersize=6,color='red') # third points
##plt.plot(p3[:,1],p3[:,0],'o',markersize=6,color='red') # second points
#plt.plot(p4[:,1],p4[:,0],'o',markersize=6,color='red') # forth points
##############################################################################
#x1 = p1[0,1]
#x2 = p3[0,1]
#y1 = p1[0,0]
#y2 = p4[0,0]
#width = (x2 - x1)/3;
#hight= (y2-y1)/3
#keymap=[]
#key=0
#for jj in range(0,3):
#    for ii in range(0,3):
#        xbegin = x1 + (ii) * width
#        xend = x1 + (ii+1) * width
#        ybegin = y1 + (jj) * hight  
#        yend = y1 + (jj+1) * hight
#        key=key+1
#        keymap.append([xbegin,xend,ybegin,yend,key]);
###############################################################################
#inputkey_coord=np.array([220,200])
#keypressed=0
#for i in range(9):
#    cond1 = keymap[i][0] <= inputkey_coord[1] < keymap[i][1]
#    cond2 = keymap[i][2] <= inputkey_coord[0] < keymap[i][3]
#    if cond1 and cond2:
#        print("Key pressed was " + str(keymap[i][4]))

#keymap = []
#for i in range(0,3):
#    xbegin = x1 + (i) * width;
#    xend = x1 + (i+1) * width;
#    keymap.append([xbegin,xend,i+1]);
#
#inputkey_coord = 400;
#
#for i in range(0,3) :
#    if keymap[i][0] <= inputkey_coord < keymap[i][1] :
#        print("Key pressed was " + str(keymap[i][2]))
