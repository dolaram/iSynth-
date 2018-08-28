
# coding: utf-8

# In[1]:
import matplotlib.image as mpimage
import matplotlib.pyplot as plt
import numpy as np
import math
import scipy.ndimage as ndimage
import cv2
# In[5]:
def make_disk( size ):
    disk = np.ones( (2*size+1,2*size+1) )

    for ii in range(0, 2*size+1):
        for jj in range(0,2*size +1 ):
            if (ii-size)**2 + (jj-size)**2  > size**2:
                disk[ii,jj] = 0

    return disk

def make_disk( size ):
    disk = np.ones( (2*size+1,2*size+1) )

    for ii in range(0, 2*size+1):
        for jj in range(0,2*size +1 ):
            if (ii-size)**2 + (jj-size)**2  > size**2:
                disk[ii,jj] = 0

    return disk

def locate_hand_1( img, size_thresh=500, is_ycrcb=False ):
    import scipy.ndimage as ndimage
#     if is_ycrcb:
#         ycrcb = img
#     else:
#         ycrcb = ct.rgb_to_ycrcb( img )
    ycrcb = cv2.cvtColor(img, cv2.COLOR_BGR2YCR_CB)
    skin_ycrcb_mint = np.array((0, 133, 77))
    skin_ycrcb_maxt = np.array((255, 173, 127))
    skin = cv2.inRange(ycrcb, skin_ycrcb_mint, skin_ycrcb_maxt)
    #skin = ct.color_thresh( ycrcb, (128, 153, 102), (200,25,30) )
    __str_el = make_disk( 1 )
    # Smooth the boundaries of the image and denoise.
    skin = ndimage.binary_erosion( skin, __str_el );
    skin = ndimage.binary_dilation( skin, __str_el );

    # Remove small connected components.
    label_im, labels = ndimage.label( skin, structure=np.ones((3,3)) )
    for label in range(1,labels+1):
        ctd_comp = (label_im == label)
        ctd_comp_size = ctd_comp.sum()
        if ctd_comp_size < size_thresh:
            skin = np.logical_xor( skin, ctd_comp )

    return skin

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
# In[6]:


def plot_contour( image, contour, color=(200,0,0) ):
    if len(image.shape) == 2:
        # The image is black and white and needs to be padded.
        temp = np.empty( [image.shape[0], image.shape[1], 3], 'uint8' )
        temp[...,0] = image.astype(np.uint8)
        temp[...,1] = image.astype(np.uint8)
        temp[...,2] = image.astype(np.uint8)
        if image.dtype == np.bool:
            temp = 255 * temp
        image = temp
    else:
        image = np.copy( image )

    color = np.array( list(color) )

    for (ii,jj) in contour:
        image[ ii, jj ] = color

    return image

def show_points( pts, shapestr='ro', markersize=5, index=-1 ):
    if len(pts) > 0:
        y,x = zip(*pts) # Split the points into x and y data.
        plt.plot(x,y, shapestr, markersize=markersize)
        plt.axis('off')

    if index > 0:
        counter = 0
        for pt in pts[::index]:            
            y,x = pt
            plt.annotate('%d' % counter, xy=(x,y), color="white")
            counter += index
    plt.show()#--rember to comment off it
def show_points_on_image( image, pts, **kwargs ):
    show_points( pts, **kwargs )
    plt.axis('off')
    plt.imshow(image)#--rember to comment off it
    plt.axis('off')
    plt.show()#rember to comment off it

def shadow_det(tips,shadow_mask,shadow_thresh,size):
    rmax,cmax = shadow_mask.shape
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
    return true_tips

