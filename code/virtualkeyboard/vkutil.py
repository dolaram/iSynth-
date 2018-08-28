from vkfrontend import *
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.image as mpimage
import numpy as np


import colortools as ct

def multi_imread( pattern, stop, start=0 ):
    return [ mpimage.imread( pattern % ii ) for ii in range(start,stop) ]
    
def contour_curvature( image, downsample, step, length ):
    bw = locate_hand( image )
    ctrs = find_contours( bw )
    ctrs = [ ctr for ctr in find_contours( bw ) if len( ctr ) > length ]
    M = 2*len(ctrs)+1

    plt.figure()    
    plt.subplot(M,1,1)

    ctr_pts = []
    for ctr in ctrs:
        ctr_pts = ctr_pts + ctr[::downsample]
    show_points_on_image( image, ctr_pts, shapestr='ro', markersize=2, index=10 )

    count = 1
    for ctr in ctrs:        
        sampled = ctr[::downsample]
        am = contour_to_acc_mag( sampled )
        angles = contour_to_angles( sampled, step )

        count+=1
        plt.subplot(M,1,count)
        plt.plot( am )
        plt.xticks(range(0,len(am),10))

        count+=1
        plt.subplot(M,1,count)
        plt.plot( angles )
        plt.xticks(range(0,len(angles),10))

def compare_contour_strategies( image, downsample, curv_thresh, ang_thresh, stepsize ):
    binary = locate_hand( image )
    ctrs = find_contours( binary )

    L = max( len(ctr) for ctr in ctrs )
    ctr = ([ ctr for ctr in ctrs if len(ctr) == L ])[ 0 ]    
    ctr = ctr[::downsample]

    plt.figure()
    plt.subplot(2,3,1)
    show_points_on_image( image, ctr, shapestr='r+', markersize=3, index=20 )
    plt.title("Original Contour\n")
    plt.xticks([])
    plt.yticks([])
    plt.xlabel("(Contour points are labeled by the contour parameter t.)")

    plt.subplot(2,3,2)
    curvature, veloc, acc = contour_to_curvatures( ctr )
    curv_tips = contour_to_tips_curvature_based( ctr, curv_thresh )
    curv_tips = group_tips( curv_tips, radius=35, allow_singletons=True )
    plt.plot( curvature )
    plt.title("Curvature Values")
    plt.xlabel("Contour Parameter (t)")
    plt.ylabel("Curvature (K)")
    
    plt.subplot(2,3,3)
    angles = contour_to_angles( ctr, stepsize )
    ang_tips = contour_to_tips(ctr, curv_thresh)
    plt.plot([ abs( theta ) for theta in angles ])
    plt.title("Contour Angles")
    plt.xlabel("Contour Parameter (t)")
    plt.ylabel("Contour Angle (Radians)")

    plt.subplot(2,3,5)
    show_points_on_image( image, curv_tips, shapestr='ro', markersize=5 )
    plt.title("Curvature Tip Estimates")
    plt.xticks([])
    plt.yticks([])

    plt.subplot(2,3,6)
    ang_tips = contour_to_tips(ctr, ang_thresh, stepsize)
    #show_points_on_image( image, ang_tips, shapestr='y+', markersize=2 )
    ang_tips = group_tips( ang_tips, radius=20 )
    show_points_on_image( image, ang_tips, shapestr='go', markersize=5 )
    plt.title("Angular Tip Estimates")
    plt.xticks([])
    plt.yticks([])
    
def tip_img_sequence( image, size=10, ratio=0.175 ):
    M = 2
    N = 3
    plt.subplot(M,N,1)    
    plt.title("Hand Segmentation")
    bw = locate_hand( image )
    plt.imshow( bw )

    plt.subplot(M,N,2)
    plt.title("Hand Contour")

    downsample = 15
    ctrs = find_contours( bw )
    ctr_pts = []
    for ctr in ctrs:
        ctr_pts = ctr_pts + ctr[::downsample]
    show_points_on_image( image, ctr_pts, shapestr='ro', markersize=3 )
    
    tips = []
    for ctr in ctrs:
        tips = tips + contour_to_tips( ctr[::downsample], \
                                           ang_thresh=3.1415/2, step=1 )
    plt.subplot(M,N,3)
    show_points( tips, shapestr='g+' )    
    tips = group_tips( tips, radius=20 )
    show_points_on_image( image, tips )
    plt.title("Fingertip Estimates")

    plt.subplot(M,N,4)
    sm = ct.rgb_to_l( image ) < 0.3
    plt.imshow(sm)
    plt.title("Shadow Map")
    
    rmax,cmax = sm.shape
    for tip in tips:
        rstart = max(0, tip[0] - size)
        rstop = min(rmax, tip[0] + size)+1
        cstart = max(0, tip[1] - size)
        cstop = min(cmax, tip[1] + size)+1

        wind = sm[rstart:rstop,cstart:cstop]
        avg = np.mean( wind )
        print("(%d, %d) : %.03f" % (tip[0], tip[1], avg))
        gca = plt.gca()
        gca.add_patch( patches.Rectangle((tip[1]-size, tip[0]-size), 
                                         2*size+1, 2*size+1, 
                                         alpha="0.2", color='green') )
        plt.annotate('%.03f' % avg, xy=(tip[1],tip[0]), color='white')

    plt.subplot(M,N,5)
    touches = filter_tips_shadow( tips, sm, ratio, size )
    show_points_on_image( image, touches )
    plt.title("Estimated Keyboard Touches")

def img_map( imgs, operation ):
    """ Given a sequence of images and an operation that takes an
    image as input and plots something, apply the operation to each
    imagexo and display the outputs in a nice array.
    """
    count = len( imgs )
    if count > 4 :
        N = np.ceil( np.sqrt(count) )
        M = N + 1
    else:
        N = count
        M = 1
    
    for ii in range(0,count):
        plt.subplot(N,M,ii+1)
        plt.title( "Item %d" % ii )
        operation( imgs[ii] )

def test_find_tips( imgs, radius=20, ang_thresh=math.pi*3.0/8.0 ):
    def op(img):
        tips = find_tips( img, ang_thresh=ang_thresh )
        show_points( tips, shapestr='g+' )
        tips = group_tips( tips, radius=radius )        
        show_points_on_image(img, tips)

    plt.figure()
    img_map( imgs, op )

def test_find_finger_touches( imgs ):
    def op(img):
        tips = find_tips( img )
        show_points( tips, shapestr='g+')

        tips = group_tips( tips, radius=30 )        
        show_points(tips, shapestr='bo')
        
        shadow_map = (ct.rgb_to_l( img ) < 0.15);
        touches = filter_tips_shadow( tips, shadow_map, size=10, shadow_thresh=0.05 )

        show_points_on_image(img, touches)

    plt.figure()
    img_map(imgs, op)

def imhist( img, bins=32, minmax=None, titles=[] ):
    plt.figure()
    colors = ['red','green','blue'];
    images = []
    N = len(img.shape);
    if N == 3:
        images = [ img[..., ii] for ii in range(0,3) ]
    else:
        images = [ img ]

    if len(titles) == 0:
        titles = [ ("Channel %d" % ii) for ii in range(0,len(images)) ]

    counter = 1
    N = len(images)
    for elt,title,color in zip(images,titles,colors):
        plt.subplot(1,N,counter)
        plt.hist( elt.flatten(), bins=bins, range=minmax )
        plt.title(title)
        plt.xlabel('Value')
        plt.ylabel('Frequency')
        counter += 1

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

    if index > 0:
        counter = 0
        for pt in pts[::index]:            
            y,x = pt
            plt.annotate('%d' % counter, xy=(x,y), color="white")
            counter += index

def show_points_on_image( image, pts, **kwargs ):
    show_points( pts, **kwargs )
    plt.imshow(image)
