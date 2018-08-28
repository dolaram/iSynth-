import numpy as np
import cv2
from vkfrontend import *
def rgb_to_ycrcb( rgb_img ):
    """
    This procedure converts the input RGB image into a YCbCr
    colorspace image.
    """
    ycbcr = np.empty( rgb_img.shape, dtype='float' )
    rgb_img = rgb_img.astype('float')
    R,G,B = rgb_img[...,0], rgb_img[...,1], rgb_img[...,2]
    Y = 0.299 * R + 0.587 * G + 0.114 * B
    Cb = 0.564 * ( B - Y ) + 128
    Cr = 0.713 * ( R - Y ) + 128

    ycbcr[...,0] = Y
    ycbcr[...,1] = Cr
    ycbcr[...,2] = Cb
    return ycbcr
path='C:\\Users\\DOLA\\Downloads\\Compressed\\vkeyboard\\scripts\\a.jpg'
img = cv2.imread(path)#img = cv2.imread(path,0) leads to binary image
plt.figure(0)
plt.imshow(img)
yimg=rgb_to_ycrcb(img)
plt.figure(1)
plt.imshow(yimg)
skin=locate_hand(yimg, size_thresh=500, is_ycrcb=True )
skin[0:10,0:10]
plt.figure(2)
plt.imshow(skin)

__str_el = make_disk( 1 )
__str_el_7 = make_disk(7)
findtips=find_tips_morph( skin, downsample=15,ang_thresh=math.pi/2, strel_size=7 )
tips=find_tips( skin, downsample=15, ang_thresh=math.pi/2 )
bw_image=skin
contours=find_contours( bw_image, max_steps=None )
find_finger_touches(skin, shadow_thresh=0.2, size=5 )

