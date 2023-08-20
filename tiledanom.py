'''composite of multiple images into one by putting seclected tiles from each, where the selection is content-based'''


## setting ntiles=0 is short-hand for ntiles = nfiles
## using --tiles 1 0, you'll get the usual vertical stripes
## using --tiles 0 1, you'll get horizontal stripes,
## using --tiles 0 2, you'll see plain horizontal stripes
## using --tiles 0 2 --random, you'll see horizontal stripes split into two

import sys
import argparse
import random
import numpy as np
from PIL import Image
import verbose as v
from tiles import Tiles
from tangles import trotate,trotate_back
import multifile

def _getargs():
    '''parse options from command line'''
    argparser = argparse.ArgumentParser(description=__doc__)
    paa = argparser.add_argument
    multifile.addargs(argparser)
    paa("--reverse","-r",action="store_true",
        help="Time right-to-left instead")
    paa("--random",action="store_true",
        help="Randomize order of input files")
    paa("--cycle",type=int,default=1,
        help="Cycle through images this many times")
    paa("--tiles","-t",nargs=2,type=int,default=None,
        help="How many tiles (wxh)")
    paa("--mindist",action="store_true",
        help="Use least anomalous (minimum distance) tiles")
    paa("--output","-o",required=True,
        help="Write output interval image to this file")
    paa("--inmean",
        help="Read fle to get mean image")
    paa("--outmean",
        help="Write mean image to this file")
    paa("--angle",type=float,default=0,
        help="Rotate image by angle (degrees)")
    paa("--verbose","-v",action="count",default=0,
        help="verbose")
    args = argparser.parse_args()
    return args

def tile_distance(x,y):
    ''' x and y should be np arrays of the same size'''
    assert x.shape == y.shape
    return np.sqrt(np.mean((x-y)**2))
        
def _main(args):
    '''main'''
    v.vprint(args)

    allfiles = multifile.getfiles(args)

    if args.reverse and args.random:
        v.print("Option --reverse is meaningless when --random is used!")

    if args.reverse:
        allfiles = list(reversed(allfiles))

    if args.random:
        ## not necessary, since randomize again below
        random.shuffle(allfiles)

    if args.cycle > 1:
        allfiles = list(allfiles) * args.cycle

    nfiles = len(allfiles)
    ntiles = (nfiles,nfiles) if not args.tiles else args.tiles
    nwtiles = ntiles[0] if ntiles[0]>0 else nfiles
    nhtiles = ntiles[1] if ntiles[1]>0 else nfiles
    ntiles = (nwtiles,nhtiles)

    alltiles = Tiles(ntiles).setup_sequential(nfiles=nfiles)
    if args.random:
        alltiles.setup_random(nfiles=nfiles)
    
    basefile = allfiles[0]
    with Image.open(basefile) as baseim:
        owidth,oheight = baseim.size
        if args.angle:
            baseim = trotate(baseim,args.angle)
        width,height = baseim.size
        v.vprint(f'({owidth},{oheight}) -> ({width},{height})')

        ## first pass, compute average image
        v.vprint('First pass: compute mean')
        if args.inmean:
            with Image.open(args.inmean) as im:
                immean = im.copy()
        else:
            for n,infile in v.vtqdm(enumerate(allfiles),total=nfiles):
                with Image.open(infile) as im:
                    if n==0:
                        npmean = 0*np.array(im,dtype=float)
                    npim = np.array(im,dtype=float)
                    npmean += npim / nfiles
            npmean = np.asarray(npmean,dtype=np.uint8)
            immean = Image.fromarray(npmean)
        if args.outmean:
            immean.save(args.outmean,quality="high")

        if args.angle:
            immean = trotate(immean,args.angle)
        ## still in first pass, break immean into tiles
        for tile in alltiles.tiles:
            box = tile.box(immean.size,ntiles)
            ## add two new attributes to tile object
            tile.immean = np.asarray(immean.crop(box),dtype=float)
            tile.dist = list()

        ## second pass, tile distance to mean for each infile
        v.vprint('Second pass: compute distances from mean')
        for n,infile in v.vtqdm(enumerate(allfiles),total=nfiles):
            with Image.open(infile) as im:
                if args.angle:
                    im = trotate(im,args.angle)
                for tile in alltiles.tiles:
                    box = tile.box(im.size,ntiles)
                    imtile = np.asarray(im.crop(box),dtype=float)
                    d = tile_distance(tile.immean,imtile)
                    tile.dist.append(d)

        ## Now pass through tiles, finding largest distance
        for tile in alltiles.tiles:
            if args.mindist:
                tile.ndx = tile.dist.index(min(tile.dist))
            else:
                tile.ndx = tile.dist.index(max(tile.dist))
            v.vvprint(f'tile {(tile.iw,tile.ih)}: {tile.ndx} {min(tile.dist):.2f} {max(tile.dist):.2f}')

        v.vprint("Third pass: paste anomalous patches into composite")
        for n,infile in v.vtqdm(enumerate(allfiles),total=nfiles):
            boxes = alltiles.get_boxes_with_ndx(n,(width,height))
            try:
                with Image.open(infile) as im:
                    if args.angle:
                        im = trotate(im,args.angle)
                    for box in boxes:
                        region = im.crop(box)
                        baseim.paste(region,box)
            except OSError:
                v.print('Failed to open file:',infile)
                pass

        if args.angle:
            baseim = trotate_back(baseim,args.angle)
            width,height=baseim.size
            baseim = baseim.crop(((width-owidth)//2,(height-oheight)//2,
                                  (width+owidth)//2,(height+oheight)//2))

        baseim.save(args.output,quality="high",exif=baseim.getexif())

    
if __name__ == "__main__":

    _args = _getargs()
    v.verbosity(_args.verbose)
    _main(_args)
