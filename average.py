'''average a sequence of pictures'''

import sys
import argparse
import random
import numpy as np
from PIL import Image
import verbose as v
from tqdm import tqdm

def _getargs():
    '''parse options from command line'''
    argparser = argparse.ArgumentParser(description=__doc__)
    paa = argparser.add_argument
    paa("files",nargs='*',
        help="Image files to be merged")
    paa("--xpand","-x",nargs=2,type=float,
        help="Percentile clips; eg '-x 1 99'")
    paa("--fcn","-f",default="ave",choices=("ave","min","max"),
        help="how to combine imgages")
    paa("--pnorm","-p",type=float,default=1,
        help="p-norm")
    paa("--output","-o",default='mean.jpg',
        help="Write output interval image to this file")
    paa("--verbose","-v",action="count",default=0,
        help="verbose")
    args = argparser.parse_args()
    return args

def _main(args):
    '''main'''
    v.vprint(args)

    imbase = None
    nfiles = len(args.files)
    for n,infile in v.vtqdm(enumerate(args.files),total=nfiles):
        with Image.open(infile) as im:
            npim = np.array(im,dtype=float)
            if args.pnorm != 1:
                npim = npim ** args.pnorm
            if n==0:
                npmean = npim
                exifbase = im.getexif()
            else:
                if args.fcn=='min':
                    npmean = np.minimum(npmean,npim)
                elif args.fcn=='max':
                    npmean = np.maximum(npmean,npim)
                else:
                    npmean += npim

    if args.fcn == 'ave':
        npmean /= nfiles

    v.vprint('Base image:',npmean.shape,np.min(npmean),np.max(npmean))        
        
    if args.pnorm != 1:
        npmean = npmean ** (1/args.pnorm)
                
    if args.xpand:
        xlo,xhi = np.percentile(npmean,args.xpand)
        v.vprint('Expand:',xlo,xhi,255/(xhi-xlo))
        npmean = 255*(npmean - xlo)/(xhi-xlo)
        npmean = np.clip(npmean,0,255)

    v.vprint('Base image:',npmean.shape,np.min(npmean),np.max(npmean))        
    npmean = np.asarray(npmean,dtype=np.uint8)
    v.vprint('Base image:',npmean.shape,np.min(npmean),np.max(npmean))
    immean = Image.fromarray(npmean)
    if imbase:
        imbase.paste(immean)
        v.vprint('imbase:',imbase.info.keys())
        immean = imbase

    immean.save(args.output,quality="high",exif=exifbase)
        
if __name__ == "__main__":

    _args = _getargs()
    v.verbosity(_args.verbose)
    _main(_args)
