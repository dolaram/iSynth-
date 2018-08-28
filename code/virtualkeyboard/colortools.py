# 
# colortools.py
#
# This library of tools is designed to help convert images between
# different color spaces, particularly RGB, HSV, HSL, and YCBCR. 
# 
# It also provides some basic procedures for analyzing the colors in
# images, namely calculating the mean color of an image and
# thresholding an image based on color data.
#

import numpy as np
import colorsys

def color_thresh( img, color, delta ):
    """
    Given an input image and color C = (X,Y,Z), and delta vector D =
    (d1,d2,d3), this procedure produces a boolean image by applying
    the following thresholding inequality to each pixel:

    Pixel[ii,jj] = (|P - C| < D)
    
    Here, the inequality on the right hand side of the equation is
    understood component-wise. In other words, the inequality really
    represents three inequalities --- one for each component of the
    vectors. For the whole vector inequality to be true, all three
    scalar inequalities must be satisfied.
    """
    c0 = img[...,0]
    c1 = img[...,1]
    c2 = img[...,2]

    b0 = np.logical_and( (c0 < color[0] + delta[0]), (c0 > color[0] - delta[0]) )
    b1 = np.logical_and( (c1 < color[1] + delta[1]), (c1 > color[1] - delta[1]) )
    b2 = np.logical_and( (c2 < color[2] + delta[2]), (c2 > color[2] - delta[2]) )

    return np.logical_and( b0, np.logical_and(b1,b2) )

def mask( image, bool_mask ):
    """
    Given a color image and a boolean mask of the same dimensions,
    this procedure uses the mask to crop the color image. If a pixel
    in the mask is set to "true", that color value is copied to the
    corresponding pixel in the output image. Otherwise, the
    corresponding pixel of the output image is set to have color
    (0,0,0).
    """
    retval = np.empty(image.shape, dtype='uint8')
    for ii in range(0,3):
        retval[...,ii] = bool_mask.astype('uint8') * image[...,ii]
    return retval

def mean_color( img ):
    """
    Given an input color image, this procedure calculates the average
    color of the image.
    """
    P,Q,R = img.shape
    avg_r = (img[...,0]).flatten().sum()
    avg_g = (img[...,1]).flatten().sum()
    avg_b = (img[...,2]).flatten().sum()

    return (avg_r / (P*Q), avg_g / (P*Q), avg_b / (P*Q) )

def bgr_to_rgb( bgr_img ):
    """
    This procedure converts a BGR image to an RGB image, where both
    images are represented by 3D arrays.
    """
    rgb = np.empty( bgr_img.shape, dtype=bgr_img.dtype )
    rgb[...,0] = bgr_img[...,2]
    rgb[...,2] = bgr_img[...,0]
    rgb[...,1] = bgr_img[...,1]

    return rgb
    
def rgb_to_hsv( rgb_img ):
    """
    This procedure provides a wrapper for the colorsys procedure for
    converting from RGB to HSV.

    Warning: This procedure is very slow.
    """
    hsv = np.empty( rgb_img.shape, dtype='float')

    M,N,d = rgb_img.shape
    for ii in range(0,M):
        for jj in range(0,N):
            h,s,v = colorsys.rgb_to_hsv( rgb_img[ii,jj,0]/255.0, 
                                              rgb_img[ii,jj,1]/255.0, 
                                              rgb_img[ii,jj,2]/255.0 )
            hsv[ii,jj,0] = h
            hsv[ii,jj,1] = s
            hsv[ii,jj,2] = v

    return hsv

def rgb_to_hsl( rgb_img ):
    """
    This procedure provides a wrapper for the colorsys procedure for
    converting from RGB to HSL.

    Warning: This procedure is very slow.
    """
    hsv = np.empty( rgb_img.shape, dtype='float')

    M,N,d = rgb_img.shape
    for ii in range(0,M):
        for jj in range(0,N):
            h,s,l = colorsys.rgb_to_hsv( rgb_img[ii,jj,0]/255.0, 
                                              rgb_img[ii,jj,1]/255.0, 
                                              rgb_img[ii,jj,2]/255.0 )
            hsv[ii,jj,0] = h
            hsv[ii,jj,1] = s
            hsv[ii,jj,2] = l

    return hsv

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
    
def rgb_to_l( rgb_img ):
    """
    This procedure takes as input an RGB image and produces as output
    the L (lightness) component of that image in HSL colorspace
    coordinates.
    """
    rr = rgb_img[...,0] / 255.0
    gg = rgb_img[...,1] / 255.0 
    bb = rgb_img[...,2] / 255.0

    MM = np.maximum( np.maximum( rr, gg ), bb )
    mm = np.minimum( np.minimum( rr, gg ), bb )
    return (MM + mm) / 2
