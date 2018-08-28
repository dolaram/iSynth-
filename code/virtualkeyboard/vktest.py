#
# vktest.py
#
# This file contains the procedures used to test the performance of
# the virtual keyboard application using ipython.
#

from pylab import *
import math
import scipy.ndimage
import datetime

import vkfrontend as front
from pointtest import *
import vkutil
import colortools
from vkbackend import GridMapper

def find_tips_curvature_based( img, bitmask ):
    hand = front.locate_hand( img )
    ctrs = front.find_contours( hand )
    tips = []
    for ctr in ctrs:
        subctr = ctr[::10] # Go to a subsequence by choosing every
                           # 10th element.
        tips += front.contour_to_tips_curvature_based( subctr, 5 )
        
    tips = front.group_tips( tips, radius=35, allow_singletons=True )
    tips = front.filter_tips_mask( tips, bitmask )
    return set(tips)

def find_tips_angular( img, bitmask ):
    hand = front.locate_hand( img )
    ctrs = front.find_contours( hand )
    tips = []
    for ctr in ctrs:
        subctr = ctr[::10]
        tips += front.contour_to_tips( subctr, ang_thresh=math.pi/2, step=1 )
    tips = front.group_tips( tips, radius=20 )
    tips = front.filter_tips_mask( tips, bitmask )
    return set(tips)

# run_test_clean_data
#
# This procedure runs a batch of experiments for fingertip detection
# on human-labeled data that is known to be relatively free of
# "pathological" images.
#
# The input tip_finder procedure has the signature
# [ Image ] X [ Bitmask ] --> [ Fingertips ]
#
# The path argument is the path to the folder of data and fingertip
# log information. We assume that within this folder, there is an
# image named img00.bmp that provides the scene without any hands in
# it, and a file named tip_data.txt that provides the correct
# locations of the fingertips.

def run_tip_test(path, tip_finder, threshold, log_filename=None ):
    base_img = scipy.ndimage.imread( path + 'img00.bmp')
    bitmask = ((base_img[...,2]) < 175);
    finder = lambda img : tip_finder( img, bitmask )

    lines = open(path + '/tip_data.txt').read().split('\n')
    lines = [ line for line in lines if len( line ) > 5 ]

    tests = []
    log = None
    if log_filename is not None:
        log = open(log_filename, 'w')

    for line in lines:
        pt = PointTest( line, finder, path, comment="Date: %s" % datetime.datetime.now())
        tests.append( pt )
        pt.run(dist_cutoff=threshold)
        if log is not None:
            log.write(line +"\n")
            log.write(str(pt))

    if log is not None:
        log.close()
    return tests

def find_touches( img, bitmask, base_img, shadow_thresh=0.15, window_size=10 ):
    gmap = GridMapper( base_img )
    tips = find_tips_angular(img,bitmask)

    lightness = colortools.rgb_to_l( img )
    shadow_mask = (lightness < 0.30 )

    touch_pts = front.filter_tips_shadow( tips, shadow_mask,
                                          shadow_thresh=shadow_thresh, size=window_size )

    keystrokes = gmap.pts_to_keystrokes( touch_pts )
    return keystrokes
        
def run_touch_test(path, shadow_thresh, window_size, log_filename=None):
    base_img = scipy.ndimage.imread( path + 'a.jpg' )
    bitmask = ((base_img[...,2]) < 190);
    finder = lambda img : find_touches( img, bitmask, base_img, 
                                        shadow_thresh, window_size )

    lines = open(path + 'data.txt').read().split('\n')
    lines = [ line for line in lines if len( line ) > 5 ]

    tests = []
    log = None
    if log_filename is not None:
        log = open(log_filename, 'w')

    for line in lines:
        pt = TouchTest( line, finder, path, comment="Date: %s" % datetime.datetime.now())
        tests.append( pt )
        pt.run()
        if log is not None:
            log.write(line +"\n")
            log.write(str(pt))

    if log is not None:
        log.close()
    return tests

path_clean = './data/tip_tests/clean/'
path_dark = './data/tip_tests/darkening/'
path_occ = './data/tip_tests/occlusion/'
path_merge = './data/tip_tests/merging/'
path_touch = './data/smallkb/'
