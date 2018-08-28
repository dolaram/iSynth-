import sys
import scipy.ndimage as ndimage
import numpy as np
from vkbackend import *

class GridMapper(TouchMapper):
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
