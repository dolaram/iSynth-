#
# vkbackend.py
#
# Author: Joseph Thomas (jthomas@math.arizona.edu)
#
# The classes defined in this file are responsible for performing the
# transformations necessary to map the touch-points located by the
# frontend to button-presses (basically, either strings naming the
# buttons or integer pairs).
#
# The abstract class TouchMapper is responsible for inverting the
# perspective projection based upon compile-time knowledge of the
# keyboard's geometry. The keyboard is assumed to have four control
# points on it, in the shape of a rectangle of known aspect ratio
# (i.e. the width and height of the keyboard, up to a common scaling
# factor). The mathematics for inverting the perspective
# transformation are described in my report.
# 
# Two classes, GridMapper and PianoMapper, extend TouchMapper. They
# take the euclidean-space coordinates given by TouchMapper
# (indicating the location of a touch-point relative to the
# controlpoints), and convert them into button presses relevant to the
# keyboard in question. For the PianoMapper, that means mapping the
# keyboard coordinates to one of the seven musical notes A-G. For the
# GridMapper, this means mapping the keyboard coordinates to an
# integer pair indicating which button in a 5x5 grid was pressed.
#

import sys
import scipy.ndimage as ndimage
import numpy as np
import math

class TouchMapper(object):
    
    def __init__(self,initial_image, kb_width, kb_height, epsilon):
        self.epsilon = float(epsilon)
        self.kb_width = float(kb_width)
        self.kb_height = float(kb_height)

        self.im_height, self.im_width, d = initial_image.shape

        self.transf = self.__extract_transformation( initial_image )

    # invert_persp_proj
    #
    # Using the parameters determined by __extract_transformation,
    # this procedure takes the input image coordinates and converts
    # them into coordinates relative to the control points on the
    # keyboard template.
    #
    def invert_persp_proj( self, img_coords ):
        # Convert to standard projective coordinates, instead of row/column.
        u,v = ( img_coords[1], (self.im_height - img_coords[0]) )
        u_0,v_0 = ( self.SW[1], (self.im_height - self.SW[0]) )

        h = self.kb_height
        w = self.kb_width

        q_0 = self.q_front # q_0 = z_0 / -d
        q_3 = self.q_back  # q_1 = z_3 / -d
        
        # Ideal Equations
        s = q_0 * ( v - v_0 ) / ( h - v * (q_3 - q_0) )
        t = (1.0 / w) * ( u * ( q_0 + s * (q_3 - q_0) ) - q_0 * u_0 )
                
        return (t,s)

    # __extract_transformation
    #
    # Given a reference image of the keyboard-template's position,
    # this private method is responsible for locating the control
    # points and determining the parameters needed to invert the
    # perspective transformation.
    #
    def __extract_transformation( self, ref_img, bthresh=100 ):
        B = ref_img[...,2].astype('float')

        self.kb_mask = (B < 195)

        control_im = (B < bthresh)
        strel = np.ones((3,3))
        control_im = ndimage.binary_opening(control_im, strel)             
        label_im, labels = ndimage.label( control_im )

        if labels != 4:
            sys.stderr.write("Error: Could not locate four control points. Aborting.\n")
            sys.exit(1)

        pts = []
        
        # These record the approximate center of mass of all of the
        # points.
        com_row = com_col = 0.0 

        for label in range(1,labels+1):
            center = ndimage.center_of_mass( (label_im == label) )
            pts.append( (int(center[0]),int(center[1])) )            
            com_row += center[0]
            com_col += center[1]

        com_row = com_row / 4.0
        com_col = com_col / 4.0

        # Recall that any point here has coordinates
        # (y,x)=(row,column)
        S = set( pt for pt in pts if pt[0] > com_row )
        if len(S) != 2:
            sys.stderr.write("Error: Could not identify two southward control points. Aborting.\n")
            sys.exit(1)

        W = set( pt for pt in pts if pt[1] < com_col )
        if len(W) != 2:
            sys.stderr.write("Error: Could not identify two westward control points. Aborting.\n")
            sys.exit(1)

        self.SW = self.NW = self.SE = self.NE = None
        for pt in pts:
            if pt in S:
                if pt in W:
                    self.SW = pt
                elif self.SE is None:
                    self.SE = pt
                else:
                    sys.stderr.write("Error: Unidentified control point. Aborting.\n")
                    sys.exit(1)
            else:
                if pt in W:
                    self.NW = pt
                elif self.NE is None:
                    self.NE = pt
                else:
                    sys.stderr.write("Error: Unidentified control point. Aborting.\n")
                    sys.exit(1)

        # Making these assignments of variables puts us in our usual
        # perspective coordinates (from xyz Euclidean coordinates).
        
        v_0,u_0 = self.SW
        v_1,u_1 = self.SE
        v_2,u_2 = self.NE 
        v_3,u_3 = self.NW
        
        if abs(v_1 - v_0) > self.epsilon or abs( v_2 - v_3 ) > self.epsilon:
            sys.stderr.write("Warning: Optical axis is not properly aligned with the viewing plane.\n");
            sys.stderr.write("Error Amounts: |v_1 - v_0| = %d, |v_2 - v_3| = %d.\n" \
                                 % (abs(v_1-v_0),abs(v_2-v_3)))

        self.q_front = self.kb_width / (u_1 - u_0)
        self.q_back  = self.kb_width / (u_2 - u_3)

        t_0,s_0 = self.c0 = self.invert_persp_proj( self.SW )
        t_1,s_1 = self.c1 = self.invert_persp_proj( self.SE )
        # Not needed, but written for completeness
        # t_2,s_2 = self.c2 = self.invert_persp_proj(self.NE )
        t_3,s_3 = self.c3 = self.invert_persp_proj( self.NW )

        # If the camera is sufficiently well aligned, the error in our
        # system manifests itself as a linear transformation that
        # skews the coordinates above. We compute the inverse of that
        # transformation and use it to correct the error.
        mat = [ [(t_1-t_0),(t_3-t_0)],\
                              [(s_1-s_0),(s_3-s_0)] ]
        
        det = mat[0][0] * mat[1][1] - mat[0][1] * mat[1][0]

        self.inv = [ [ mat[1][1]/det, -mat[0][1]/det],\
                         [ -mat[1][0]/det, mat[0][0]/det] ]

    # kb_coordinates
    #
    # Given input image coordinates of a point on the keyboard mat,
    # this procedure returns our best estimate of the coordinates of
    # that point relative to the control points. This is the procedure
    # subclasses should use when they are mapping touch-points to
    # button presses.
    def kb_coordinates( self, img_coords ):
        t_raw,s_raw = self.invert_persp_proj( img_coords )

        mat = self.inv
        t = t_raw * mat[0][0] + s_raw * mat[0][1]
        s = t_raw * mat[1][0] + s_raw * mat[1][1]

        return (t,s)

class GridMapper(TouchMapper):
    # Because we know the geometry of the grid keyboard template, we
    # pass this information on to the superclass.
    def __init__( self, initial_image, epsilon=5 ):
        super(GridMapper,self).__init__( initial_image, 1.0, 1.0, epsilon )

    def pts_to_keystrokes( self, points ):
        pts = [ self.kb_coordinates(pt) for pt in points ]
        
        retvals = []
        for pt in pts:
            if pt is None: continue
            x = int( np.floor( 7 * pt[0] ) )
            y = int( np.floor( 7 * pt[1] ) )            

            if 1 <= x <= 5 and 1 <= y <= 5:
                retvals.append((x,y))

        return set(retvals)

class PianoMapper(TouchMapper):

    # Because we know the geometry of the piano keyboard template, we
    # pass this information on to the superclass.
    def __init__( self, initial_image, epsilon=5 ):
        super(PianoMapper,self).__init__( initial_image, 9.0, 4.0, epsilon )

    def pts_to_keystrokes( self, points ):
        pts = [ self.kb_coordinates(pt) for pt in points ]
        
        keystrokes = [ "B", "A", "G", "F", "E", "D", "C" ]
    
        retvals = []
        for pt in pts:
            if pt is None: continue
            N = int(np.floor( 9 * pt[0] ) - 1)
            if 0 <= N < 7 :
                retvals.append( keystrokes[ N ] )

        return retvals
