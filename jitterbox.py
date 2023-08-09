'''single image broken into tiles that are jittered in origin'''

## Because rbox (reference box, box in composite image) is in a
## standard position, we cannot obtain jitter along the lines of
##
##   XXXABCDEFGHIJXXX
##   XXABCDEFGHIJXXXX
##   XXXXXABCDEFGHIJX
##   XABCDEFGHIJXXXXX
##
## with full rows (misalgined to each other)
## We can approximate eht effect iwth "-j 4 0 -t 100 1"
## but half the time, we'll lack black on one edge or the other.


import sys
import argparse
import random
from PIL import Image,ImageOps
import verbose as v
from tiles import Tiles
from tangles import trotate,trotate_back

def _getargs():
    '''parse options from command line'''
    argparser = argparse.ArgumentParser(description=__doc__)
    paa = argparser.add_argument
    paa("file",
        help="Image files to be jittered")
    paa("--tiles","-t",nargs=2,type=int,default=None,
        help="How many tiles (wxh)")
    paa("--jitter","-j",nargs='+',type=int,default=(0,),
        help="Amount of jitter")
    paa("--pad","-p",nargs="?",type=int,const=None,default=0,
        help="Pad base image to enable jitter at edges")
    paa("--picasso",action="store_true",
        help="Picasso mode: randomize tiles")
    paa("--output","-o",default='interval.jpg',
        help="Write output interval image to this file")
    paa("--angle",type=float,default=0,
        help="Rotate image by angle (degrees)")
    paa("--verbose","-v",action="count",default=0,
        help="verbose")
    args = argparser.parse_args()
    return args

def fitbox(box,npixels):
    '''keep box the same size, but make sure it fits in image 
    whose size is given by npixels'''
    (wlo,hlo,whi,hhi) = box
    
    xwlo = max(0,wlo)
    xwhi = xwlo + (whi-wlo)
    xhlo = max(0,hlo)
    xhhi = xhlo + (hhi-hlo)
    if npixels is not None:
        xwhi = min(xwhi,npixels[0])
        xwlo = xwhi - (whi-wlo)
        xhhi = min(xhhi,npixels[1])
        xhlo = xhhi - (hhi-hlo)
    return (xwlo,xhlo,xwhi,xhhi)

def matchbox(box,refbox):
    (wlo,hlo,whi,hhi) = box
    (rwlo,rhlo,rwhi,rhhi) = refbox
    whi = wlo + (rwhi-rwlo)
    hhi = hlo + (rhhi-rhlo)
    return (wlo,hlo,whi,hhi)

def jitterbox(box,jit):
    (wlo,hlo,whi,hhi) = box
    wjit = random.randint(-jit[0],jit[0])
    hjit = random.randint(-jit[1],jit[1])
    wlo += wjit
    whi += wjit
    hlo += hjit
    hhi += hjit
    return (wlo,hlo,whi,hhi)

def _main(args):
    '''main'''
    v.vprint(args)

    ntiles = (10,10) if not args.tiles else args.tiles

    alltiles = Tiles(ntiles)

    wjitter = args.jitter[0]
    hjitter = args.jitter[1] if len(args.jitter)>1 else wjitter

    if args.pad is None:
        args.pad = max(args.jitter)
    
    basefile = args.file
    with Image.open(basefile) as baseim:
        owidth,oheight = baseim.size
        if args.angle:
            baseim = trotate(baseim,args.angle)
        width,height = baseim.size
        v.vprint(f'({owidth},{oheight}) -> ({width},{height})')
        
        if args.pad:
            baseim = ImageOps.pad(baseim,(width+2*args.pad,
                                          height+2*args.pad),
                                  color='black',
                                  centering=(0.5, 0.5))
            width,height = baseim.size
        im = baseim.copy() #Image.new('RGB',baseim.size,"red")

        rtiles = [tile for tile in alltiles.tiles]
        if args.picasso:
            random.shuffle(rtiles)
        
        for tile,rtile in zip(alltiles.tiles,rtiles):
            rbox = rtile.box((width,height),ntiles)
            box = tile.box((width,height),ntiles)
            jbox = jitterbox(box,(wjitter,hjitter))
            jbox = matchbox(jbox,rbox)
            if args.pad:
                #rbox = tuple(rbox[i]+args.pad for i in range(4))
                #jbox = tuple(jbox[i]+args.pad for i in range(4))
                pass
            else:
                jbox = fitbox(jbox,npixels=(width,height))
            v.vvprint(f'box={box}, jbox={jbox}, rbox={rbox}')
            region = baseim.crop(jbox)
            im.paste(region,rbox)

        if args.angle:
            im = trotate_back(im,args.angle)
            width,height=im.size
            im = im.crop(((width-owidth)//2,(height-oheight)//2,
                                  (width+owidth)//2,(height+oheight)//2))

        im.save(args.output,quality="high",exif=baseim.getexif())
    
if __name__ == "__main__":

    _args = _getargs()
    v.verbosity(_args.verbose)
    _main(_args)
