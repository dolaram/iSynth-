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
# In[2]:
# Reading the imgae 
path='C:\\Users\\DOLA\\Downloads\\Compressed\\vkeyboard\\scripts\\img\\sh1.jpg'
#image=imgg 
#image=cv2.imread(path)#img = cv2.imread(path,0) leads to binary image
#image=cv2.cvtColor(image,cv2.COLOR_BGR2RGB)
plt.figure(1)
#plt.subplot(331)
plt.imshow(image)
plt.axis('off')
plt.show()
# In[3]:
bw = locate_hand_1(image)
#plt.subplot(332)
plt.figure(2)
plt.imshow(bw)
plt.title("Hand Segmentation")
plt.axis('off')
plt.show()
# In[4]:
#plt.subplot(333)
plt.figure(3)
downsample = 15
ctrs = find_contours( bw )
ctr_pts = []
for ctr in ctrs:
    ctr_pts = ctr_pts + ctr[::downsample]
show_points_on_image( image, ctr_pts, shapestr='ro', markersize=3 )
plt.axis('off')
#c=np.matrix(ctr_pts)
#plt.plot(c[:,1],c[:,0],'ro',markersize=5)
#plt.imshow(image)
# In[5]:
plt.figure(3)
#plt.subplot(334)
c=np.matrix(ctr_pts)
plt.plot(c[:,1],c[:,0],'ro',markersize=5)
plt.axis('off')
plt.show()

#plt.imshow(image)
# In[6]:
#plt.subplot(335)
plt.figure(4)
tips = []
for ctr in ctrs:
    tips = tips + contour_to_tips( ctr[::downsample], \
                                         ang_thresh=3.1415/2, step=1 )
plt.imshow(image)
show_points( tips, shapestr='g+' )
plt.axis('off')
plt.show()
#plt.subplot(336)
tips =group_tips( tips, radius=20 )
#tips =find_tips_curvature_based( ctrs )
#tips =contour_to_tips_curvature_based( ctr, curv_thresh=200)#150 )
show_points_on_image( image, tips )
plt.axis('off')
plt.title("Fingertip Estimates")

# In[7]:
plt.figure(5)
#plt.subplot(221)
tips =group_tips( tips, radius=20 )
#tips =find_tips_curvature_based( ctrs )
#tips =contour_to_tips_curvature_based( ctr, curv_thresh=200)#150 )
show_points_on_image( image, tips )
plt.axis('off')
plt.title("Fingertip Estimates")
plt.show()
# In[8]:
#plt.subplot(222)
plt.figure(6)
sm = ct.rgb_to_l( image ) < 0.3
#sb=np.maximum(bw.astype('float32')-sm.astype('float32'),0)
#sm=np.maximum(sm.astype('float32')-sb.astype('float32'),0)
plt.imshow(sm)
plt.title("Shadow Map")
plt.axis('off')
rmax,cmax = sm.shape
# In[9]:
#plt.subplot(223)
plt.figure(6)
shadow_mask=sm
shadow_thresh=0.05*1.5
size=10*0.5
true_tips = []
for tip in tips:
        rstart = int(max(0, tip[0] - size))
        rstop = int(min(rmax, tip[0] + size)+1)
        cstart =int( max(0, tip[1] - size))
        cstop = int(min(cmax, tip[1] + size)+1)
        #print(type(rstart),type(rstop),type(cstart),type(cstop))
        wind = shadow_mask[rstart:rstop,cstart:cstop]
        avg = np.mean( wind )
        if avg < shadow_thresh:
            true_tips.append( tip )
touches=true_tips#filter_tips_shadow( tips, sm, ratio, size )
show_points_on_image( image, touches )
plt.title("Estimated Keyboard Touches")
plt.axis('off')
plt.show()

# In[9]:
import cv2
import numpy as np
cap.release()
cap=cv2.VideoCapture(1)
while True:
    ret,frame = cap.read()
    cv2.imshow('frame',frame)
    if(cv2.waitKey(1)&0xFF==ord('q')):
        break
cap.release()
cv2.destroyAllWindows()

# In[9]:
#cap=cv2.VideoCapture(1)
#ret,frame = cap.read()
#plt.imshow(frame)
#plt.show()
#cap.release()

# In[9]:
#path='C:\\Users\\DOLA\\Downloads\\Compressed\\vkeyboard\\scripts\\img\\sh2.jpg'
#image= cv2.imread(path)#img = cv2.imread(path,0) leads to binary image
#img=frame
#hsv1 = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
#hsv1[:,:,0] = ((255.0/179.0)*hsv1[:,:,0]).astype('uint8')
#hsv2 = cv2.cvtColor(hsv1, cv2.COLOR_RGB2HSV)
#red = hsv2[:,:,0]
#_,out = cv2.threshold(red, 0, 255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
#plt.figure(3)
#plt.imshow(out)
##cv2.imshow('Output', out)
#plt.show()

# In[9]:
#Saving the image
#cv2.imwrite('03.png',imgg)
import cv2
import matplotlib.pyplot as plt

def grab_frame(cap):
    ret,frame = cap.read()
    return cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
cap1.release()
#Initiate the two cameras
cap1 = cv2.VideoCapture(1)
#cap2 = cv2.VideoCapture(1)

#create two subplots
#ax1 = plt.subplot(1,2,1)
ax2 = plt.subplot(1,1,1)

#create two image plots
#im1 = ax1.imshow(grab_frame(cap1))
im2 = ax2.imshow(cap1.read()[1].astype('float32'))

plt.ion()

while True:
    rgb=grab_frame(cap1)
    #im1.set_data(rgb)
    bw = locate_hand_1(cap1.read()[1])
    im2.set_data(rgb)
    plt.pause(0.02)

plt.ioff() # due to infinite loop, this gets never called.
plt.show()
cap1.release()