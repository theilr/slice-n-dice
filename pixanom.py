'''anomalous pixels (most unlike mean) from a sequence of pictures'''

import sys
import argparse
import random
import numpy as np
from PIL import Image
import verbose as v
from tqdm import tqdm
import multifile

def _getargs():
    '''parse options from command line'''
    argparser = argparse.ArgumentParser(description=__doc__)
    multifile.addargs(argparser)
    paa = argparser.add_argument
    paa("--mindist",action="store_true",
        help="Use least anomalous (minimum distance) tiles")
    paa("--xpand","-x",nargs=2,type=float,
        help="Percentile clips; eg '-x 1 99'")
    paa("--output","-o",default='mean.jpg',
        help="Write output interval image to this file")
    paa("--inmean",
        help="Read fle to get mean image")
    paa("--outmean",
        help="Write mean image to this file")
    paa("--verbose","-v",action="count",default=0,
        help="verbose")
    args = argparser.parse_args()
    return args

def _main(args):
    '''main'''
    v.vprint(args)

    imbase = None
    allfiles = multifile.getfiles(args)
    nfiles = len(allfiles)

    v.vprint('First pass: get mean')
    if args.inmean:
        with Image.open(args.inmean) as im:
            exifbase = im.getexif()
            npmean = np.array(im,dtype=float)
    else:
        npmean=0
        for n,infile in v.vtqdm(enumerate(allfiles),total=nfiles):
            with Image.open(infile) as im:
                if n==0:
                    exifbase = im.getexif()
                npim = np.array(im,dtype=float)
                npmean = npmean + npim
        npmean /= nfiles
    if args.outmean:
        immean = Image.fromarray(np.asarray(npmean,dtype=np.uint8))
        immean.save(args.outmean,quality="high",exif=exifbase)

    v.vprint('Second pass: get distances')
    distances = list()
    for n,infile in v.vtqdm(enumerate(allfiles),total=nfiles):
        with Image.open(infile) as im:
            npim = np.array(im,dtype=float)
            d = np.mean((npim - npmean)**2,axis=2)
            distances.append(d)

    distances = np.array(distances,dtype=float)
    v.vvprint('distances:',distances.shape)

    argfcn = np.argmin if args.mindist else np.argmax
    ndx = argfcn(distances,axis=0)
    ndx = ndx.reshape(*ndx.shape,1)
    v.vvprint('ndx:',ndx.shape)

    ndxset = set(np.ravel(ndx))
    v.vprint('ndxset:',len(ndxset),'/',nfiles,ndxset)

    npanom = 0*npmean
    v.vprint('Third pass: build image from anomalies')
    for n,infile in v.vtqdm(enumerate(allfiles),total=nfiles):
        if n in ndxset:
            with Image.open(infile) as im:
                npim = np.array(im,dtype=float)
                npanom += (ndx == n)*npim

    if args.xpand:
        xlo,xhi = np.percentile(npanom,args.xpand)
        v.vprint('Expand:',xlo,xhi,255/(xhi-xlo))
        npanom = 255*(npanom - xlo)/(xhi-xlo)
        npanom = np.clip(npanom,0,255)

    v.vprint('Base image:',npanom.shape,np.min(npanom),np.max(npanom))        
    npanom = np.asarray(npanom,dtype=np.uint8)
    v.vprint('Base image:',npanom.shape,np.min(npanom),np.max(npanom))
    imanom = Image.fromarray(npanom)

    imanom.save(args.output,quality="high",exif=exifbase)
        
if __name__ == "__main__":

    _args = _getargs()
    v.verbosity(_args.verbose)
    _main(_args)
