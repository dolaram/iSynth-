#
# cvutils.py
#
# Author: Joseph Thomas (jthomas@math.arizona.edu)
#
# This file contains a number of procedures useful for working with
# the OpenCV computer vision library. Specifically, it contains
# procedures for opening cameras and drawing indicators (like lines
# and boxes) on images.
#

import scipy.misc
import numpy, cv2, sys, optparse
import cv2.cv as cv
import time
import Image # Python Imaging Library module

from vkbackend import GridMapper

WINDOW_SIZE = 10

# init_camera
#
# This procedure initializes an OpenCV camera object, and returns it
# for use by other procedures.
#
def init_camera():
    cam = cv.CaptureFromCAM(0)
    if not cam:
        sys.stdout("Error Initializing Camera! Aborting.")
        sys.exit(1)

    return cam

# draw_guidelines
#
# This procedure is responsible for drawing vertical and horizontal
# lines on an image that will be displayed to the screen, so that the
# user can properly align the camera with the keyboard-mat. The input
# parameters indicate how many horizontal/vertical rectangles should
# appear in the image (ex. vert_count = 2 means 2 regions and 1
# vertical line between them).
#
def draw_guidelines( img, horiz_count=2, vert_count=2, color=(0,0,255) ):
    arr = numpy.array(img[:])
    H,W,D = arr.shape
    for ii in range(1,horiz_count):
        start = (0, ii * H/horiz_count)
        stop  = (W, ii * H/horiz_count )
        cv2.line( arr, start, stop, color )
    for ii in range(1,vert_count):
        start = (ii * W/vert_count , 0 )
        stop = (ii * W/vert_count, H )
        cv2.line( arr, start, stop, color )
        
    return cv.fromarray( arr )

# paint_markers
# 
# Given an input image img and two lists of pixel coordinates, this
# procedure paints boxes of width WINDOW_SIZE onto a copy of the image
# and returns the results.
#
# The first list of pixel coordinates represent places where a likely
# fingertip was identified. These locations are tagged with a red
# box. The second list of pixel coordinates represent places where a
# finger is believed to touch the tabletop. These locations are tagged
# with a green box.
#
def paint_markers( img, tips, touch_pts ):
    # For reasons that don't make much sense, the opencv image needs
    # to be unpacked as a numpy array, written on, then repacked.
    arr = numpy.array( img[:] )

    for point in tips:
        pt1 = (point[1] - WINDOW_SIZE, point[0] - WINDOW_SIZE )
        pt2 = (point[1] + WINDOW_SIZE, point[0] + WINDOW_SIZE )
        cv2.rectangle(arr, pt1, pt2, (0,0,255), thickness=2)
    for point in touch_pts:
        pt1 = (point[1] - WINDOW_SIZE, point[0] - WINDOW_SIZE )
        pt2 = (point[1] + WINDOW_SIZE, point[0] + WINDOW_SIZE )
        cv2.rectangle(arr, pt1, pt2, (0,255,0), thickness=2)

    return cv.fromarray( arr )

# tare
#
# Given an input camera cam, this procedure runs the initalization
# sequence of the program, which determines the location of the
# virtual keyboard. This procedure waits in a loop, displaying output
# from the camera, until the user presses "t". At that point, it
# labels the control points and asks the user whether those points are
# correctly labeled. If so, the procedure initializes the mapping from
# image space to keyboard space, and returns this mapping. Otherwise,
# the program halts.
#
def tare( cam ):   
    keypress = -1
    img = None
    while keypress != 1048692:
        # i.e. keypress != 't'
        keypress = cv.WaitKey(30)
        img = cv.QueryFrame(cam)
        cv.ShowImage("Frame Capture", draw_guidelines(img))

    # The image is captured in BGR format. Convert to the usual
    # RGB using fast C++ code.
    cv.CvtColor( img, img, cv.CV_BGR2RGB )

    sys.stdout.write("Tare image captured. Displaying detected control points.\n")
    sys.stdout.write("Press 't' to accept the control points, or any other key to abort.\n")
    sys.stdout.flush()

    pmap = GridMapper( numpy.array(img[:]))
    
    sys.stdout.write("Located Control Points: [pmap.NW, pmap.SW, pmap.SE, pmap.NE] = %s\n"
                     % str([pmap.NW, pmap.SW, pmap.SE, pmap.NE]))
    sys.stdout.flush()

    im_painted = paint_markers( img, [pmap.NW, pmap.SW, pmap.SE, pmap.NE], [] )
    cv.ShowImage("Frame Capture", im_painted)
    
    keypress = -1
    while keypress == -1:
        keypress = cv.WaitKey(30)
        if keypress == 1048692:
            return pmap
        elif keypress != -1:
            sys.exit(1)

# save_frame
# 
# This helper procedure is responsible for saving the input image to
# the input filename. Note that because OpenCV works with different
# color coordinates, this procedure is responsible for converting
# between BGR and RGB colorspaces.
#
def save_frame( img, filename ):
    cv.CvtColor( img, img, cv.CV_BGR2RGB )
    imarray = numpy.array(img[:])
    scipy.misc.imsave(filename, imarray)
    sys.stdout.write('Wrote %s\n' % filename)
    sys.stdout.flush()
    
