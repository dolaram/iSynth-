#
# vkfrontend.py
#
# Author: Joseph Thomas (jthomas@math.arizona.edu)
#
# This file describes the "frontend" of a virtual keyboard system ---
# that is, the collection of procedures that convert an input picture
# of a hand to a list of pixel locations (i,j) where the system
# estimates that the hand's fingertips are in contact with the
# keyboard.
#
# This file provides a library of useful procedures for implementing a
# virtual keyboard. By choosing different procedures from this
# library, a programmer can exercise more or less control over the
# details of his virtual keyboard program. (We needed to be able to
# implement a virtual keyboard in many different ways in order to
# compare the performance of various schemes described in the
# literature.)
#

import math
import numpy as np
import scipy.ndimage as ndimage
import colortools as ct

#
# make_disk
#
# This procedure constructs a structuring element that is roughly a
# Euclidean disk with the input radius.
#
def make_disk( size ):
    disk = np.ones( (2*size+1,2*size+1) )

    for ii in range(0, 2*size+1):
        for jj in range(0,2*size +1 ):
            if (ii-size)**2 + (jj-size)**2  > size**2:
                disk[ii,jj] = 0

    return disk

# Rather than reallocating the same structuring element many times,
# save a copy here.
__str_el = make_disk( 1 )
                   
#
# locate_hand
#
# Given an input image I, locate_hand is responsible for performing a
# skin segmentation on I in order to find the hand(s) in the scene,
# producing a binary image that is returned to the user (true pixels
# indicate the hand regions). The procedure also applies a
# morphological opening to smooth the boundaries on the resulting
# binary image, and removes any connected component of size smaller
# than the optional input size_thresh.
#
def locate_hand( img, size_thresh=500, is_ycrcb=False ):
    if is_ycrcb:
        ycrcb = img
    else:
        ycrcb = ct.rgb_to_ycrcb( img )

    skin = ct.color_thresh( ycrcb, (128, 153, 102), (200,25,30) )

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

#
# find_tips_*
#
# These procedures (intended for testing location of fingertips), all
# take as input a binary image and produce as output a list of
# estimated fingertip (pixel) locations in the scene. Typically, these
# procedures process the output of locate_hand(...).
#
# find_tips_morph uses morphological techniques to try to find the
# fingertips, first eroding the hand region to sharpen the angle at
# the fingertips, and then using the angle-based detector to find the
# tips.
#
# find_tips implements the basic angle-based fingertip detector
# described in my report.
#

__str_el_7 = make_disk(7)
def find_tips_morph( bw_img, downsample=15, 
                     ang_thresh=math.pi/2, strel_size=7 ):
    if strel_size != 7:
        strel = make_disk( strel_size )
    else:
        strel = __str_el_7

    eroded = ndimage.binary_erosion( bw_img, strel )
    return find_tips( eroded, downsample=downsample, ang_thresh=ang_thresh )

def find_tips( bw_img, downsample=15, ang_thresh=math.pi/2 ):
    contours = find_contours( bw_img )
    tips = []
    for cont in contours:
        tips += contour_to_tips( cont[::downsample], ang_thresh=ang_thresh, step=1)
    return tips

#
# find_contours
#
# Given a binary image as input (representing the hand regions in the
# scene), this procedure determines the boundary contours around all
# of the hand regions (lists of neighboring pixel locations) and
# returns them.
#
def find_contours( bw_image, max_steps=None ):
    label_im, labels = ndimage.label( bw_image )
    contours = []
    for label in range(1,labels+1):
        ctd_comp = (label_im == label)
        ind = np.where( ctd_comp == True )
        start = (ind[0][0],ind[1][0])
        contours.append( find_contour( ctd_comp, start, max_steps=max_steps ) )
    return contours

# find_contour
#
# Given an input binary image bin_img and a starting pixel location
# start (in row-column coordinates), this procedure determines the
# boundary of the simply connected component containing start. It
# returns a sequential list of pixel locations representing a contour
# that parameterizes the boundary.
#
def find_contour( bin_img, start, max_steps=None ):
    rmax,cmax = bin_img.shape
    
    def add( listA, listB ): 
        return (listA[0] + listB[0], listA[1] + listB[1])

    def rot90( list ): 
        return [-list[1], list[0]]

    def psn_ok( list ):
        return (0 <= list[0] < rmax and 0 <= list[1] < cmax) 

    psn = list(start)
    while (psn[1] > 0) and (bin_img[psn[0],psn[1]-1]):
        psn[1] = psn[1] - 1

    forward = [1,0]
    start = [ psn[0], psn[1] ]
    contour = []
    while True:
        if max_steps != None and len(contour) > max_steps: break

        contour.append( psn )
        for jj in range(0,4):
            next = add(psn, forward);
            if psn_ok(next) and bin_img[ next[0], next[1] ]:
                # Found an opening! Move ahead.
                psn = next                                      
                break
            else:
                # Hit a wall! Turn 90 degrees counterclockwise!
                forward = rot90(forward)
    
        if psn[0] == start[0] and psn[1] == start[1]: break
        
        # Check the "going around a corner" case:
        right = add(psn, rot90( [-forward[0], -forward[1]] ))
        if psn_ok(right) and bin_img[ right[0], right[1] ] :
            # There is an opening to the right. This must be because we
            # moved past a corner. Regain contact by moving around the
            # corner.
            contour.append( psn )
            psn = right
            forward = rot90( [-forward[0],-forward[1]] )            
            if psn[0] == start[0] and psn[1] == start[1]: break

    return [ tuple( pt ) for pt in contour ]

#
# contour_to_angles
# 
# This procedure takes as input a contour (a list of pixel
# coordinates) and produces as output a list of angles representing
# how the contour bends. The formula describing how the angle is
# calculated is described in my report. The output of this procedure
# is used in the angle-based fingertip detector.
#
def contour_to_angles( contour, step ):
    N = len(contour)

    angles = np.empty(N,dtype='float64')

    for ii in range(0, N):
        px,py = contour[ii-step]
        qx,qy = contour[ii]
        rx,ry = contour[(ii+step) % N]

        vx = px - qx
        vy = py - qy
        wx = rx - qx
        wy = ry - qy

        xcoord = wx * vx + wy * wy
        ycoord = wx * vy + wy * (-vx)

        angles[ ii ] = math.atan2( ycoord, xcoord )
    
    return angles

#
# contour_to_tips
#
# This procedure implements angle-based fingertip detection. Given an
# input contour, the procedure calculates the corresponding sequence
# of angles for that contour, and applies a threshold to those angles
# to locate the contour points that are likely fingertips.
#
def contour_to_tips( contour, ang_thresh=math.pi/2, step=3 ):
    N = len(contour)

    if N <= step: return []
    angles = contour_to_angles( contour, step )
    tips = []
    for ii in range(0, N):
        if (0 < angles[ii] < ang_thresh):
            tips.append( contour[ii] )
        
    return tips

#
# contour_to_curvatures
#
# This procedure is responsible for calculating a sequence of
# velocity, acceleration and curvature estimates for an input
# contour. The formulas for these quantities are outlined in my
# report. The output of this procedure is used by the curvature-based
# fingertip detector.
#
__kernel = np.transpose( np.array([[-1,0,1]],'float') )
def contour_to_curvatures( contour ):
    N = len(contour)
    
    psn = np.array( contour, 'float' )    
    vel = ndimage.convolve(psn,__kernel,mode='wrap')
    acc = ndimage.convolve(vel,__kernel,mode='wrap')

    curv = [ 0 for ii in range(0,N) ]
    for ii in range(0,N):
        num = (vel[ii][0] * acc[ii][1] - vel[ii][1] * acc[ii][0])**2
        denom = (vel[ii][0]**2 + vel[ii][1]**2) ** (1.5)
        curv[ii] = num / denom
    
    return curv,vel,acc

#
# contour_to_tips_curvature_based
#
# This procedure implements curvature-based fingertip detection.
# Given an input contour, it calculates a corresponding list of
# curvature values for that contour. It applies nonmaximum suppression
# (with the input curvature threshold) to locate those points where
# the curvature is maximal and the accelleration vector points into
# the hand. Those locations are estimated to be the fingertips in the
# scene --- these points in the contour are returned in a list as
# output.
#
def contour_to_tips_curvature_based( contour, curv_thresh ):
    N = len(contour)
    curv, vel, acc = contour_to_curvatures( contour )
    tips = []
    for ii in range(0,N):
        if curv[ii] < curv_thresh \
        or curv[ii] < curv[ (ii+1) % N ] \
        or curv[ii] < curv[ii-1] \
        or (vel[ii][0] * acc[ii][1] - vel[ii][1] * acc[ii][0] > 0): continue
        tips.append( contour[ii] )

    return tips
    
# 
# find_tips_curvature_based
#
# This helper method takes as input several contours and locates all
# of the fingertips in those contours using the curvature-based
# method.
#
def find_tips_curvature_based( ctrs ):
    tips = []
    for ctr in ctrs:
        subctr = ctr[::10] # Go to a subsequence by choosing every
                           # 10th element.
        tips += contour_to_tips_curvature_based( subctr, 4 )        
    tips = group_tips( tips, radius=35, allow_singletons=True )
    return set(tips)

#
# filter_tips_mask
# 
# Given a list of fingertips (variable tips) this procedure returns
# only those fingertips (pixel locations) that also appear in the
# input binary image as "True" pixels.
#
# A typical application is: We have a list of fingertip candidates,
# but are only interested in those that appear in a certain subimage
# of our input image --- say a 100 by 100 window W of a certain
# point. By constructing the appropriate "mask" binary image,
# filter_tips_mask lets us filter out just those tips in W.
# 
def filter_tips_mask( tips, bool_mask ):
    return [ (ii,jj) for (ii,jj) in tips if bool_mask[ii,jj] ]


# 
# group_tips
#    
# Given a sequence of proposed finger tips (still in the order
# that they appeared in the original contour, this procedure applies
# a sequence of tests to filter down to form a more likely
# collection of finger tip positions.
#
# For certain users with more square-shaped fingertips, our system may
# detect the corners of the fingers (rather than the centers of the
# fingertips) as fingertips. To remedy this, group_tips searches for
# fingertip points that are very near one another, and then replaces
# them with a single fingertip point whose position is the average of
# the points grouped together.
#
def group_tips(tips, radius=20, allow_singletons=False):
    groups = {}
    for ii in range(0,len(tips)-1):
        if tips[ii] in groups:
            grp = groups[ tips[ii] ]
        else:
            grp = [ tips[ii] ]
            groups[ tips[ii] ] = grp

        (x,y) = tips[ii]
        for jj in range(ii+1,len(tips)):
            (u,v) = tips[jj]            
            if (abs(x-u) + abs(y-v) < radius):
                grp.append( (u,v) )
                groups[ (u,v) ] = grp

    avgtips = []
    for grp in groups.values():
        if len( grp ) == 1 and not allow_singletons: continue
        p = sum( [ x for (x,y) in grp ] ) / len( grp )
        q = sum( [ y for (x,y) in grp ] ) / len( grp )
        avgtips.append( (p,q) )
                    
    return avgtips

#
# filter_tips_shadow
#
# This procedure takes as input a list of fingertips and a binary
# image "shadow_mask" indicating the shadows that appear in the scene
# with the input fingertips.
#
# Each fingertip is a pixel-location (i,j). This procedure inspects a
# square neighborhood N in the image shadow_mask, centered at (i,j). N
# has width 2 * size. The procedure calculates the proportion p of
# shadow pixels in N. If p is greater than shadow_thresh, the
# fingertip is ruled to not be in contact with the tabletop, and is
# not returned. Otherwise, p is ruled to be a touch point, and is
# returned from the procedure.
#
def filter_tips_shadow( tips, shadow_mask, shadow_thresh=0.05, size=10 ):
    rmax,cmax = shadow_mask.shape    
    true_tips = []
    for tip in tips:
        rstart = int(max(0, tip[0] - size))
        rstop = int(min(rmax, tip[0] + size)+1)
        cstart =int( max(0, tip[1] - size))
        cstop = int(min(cmax, tip[1] + size)+1)
        print(rstart,rstop,cstart,cstop)
        wind = shadow_mask[rstart:rstop,cstart:cstop]
        avg = np.mean( wind )
        if avg < shadow_thresh:
            true_tips.append( tip )

    return true_tips
 
#
# find_finger_touches
# 
# This procedure is a helper procedure for interactive testing
# purposes. Given an input RGB image (rgb_img), shadow-threshold and
# window size, this procedure performs a full shadow-analysis on the
# image (using the input shadow-analysis parameters) to determine
# whether there are any fingertips in the image that are in contact
# with the tabletop in the scene. It returns those estimated touch
# points.
#
# This procedure uses angle-based fingertip detection to locate the
# fingertips in the scene.
# 
def find_finger_touches( rgb_img, shadow_thresh=0.2, size=5 ):
    tips = find_tips( rgb_img )    
    tips = group_tips( tips, radius=10 )

    shadow_mask = ( ct.rgb_to_l( rgb_img ) < 0.15)
    touch_pts = filter_tips_shadow( tips, shadow_mask, \
                                        shadow_thresh=shadow_thresh, size=size )

    return touch_pts
