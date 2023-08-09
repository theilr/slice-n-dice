'''composite of multiple images into one by putting seclecting tiles from each'''

## setting ntiles=0 is short-hand for ntiles = nfiles
## using --tiles 0 1, you'll get the usual vertical stripes
## using --tiles 1 0, you'll get horizontal stripes,
## using --tiles 2 0, you'll see plain horizontal stripes
## using --tiles 2 0 --random, you'll see horizontal stripes split into two

import sys
import argparse
import random
from PIL import Image
import verbose as v
from tiles import Tiles
from tangles import trotate,trotate_back
import multifile

def _getargs():
    '''parse options from command line'''
    argparser = argparse.ArgumentParser(description=__doc__)
    multifile.addargs(argparser)
    paa = argparser.add_argument
    paa("--reverse","-r",action="store_true",
        help="Time right-to-left instead")
    paa("--random",action="store_true",
        help="Randomize order of input files")
    paa("--cycle",type=int,default=1,
        help="Cycle through images this many times")
    paa("--tiles","-t",nargs=2,type=int,default=None,
        help="How many tiles (wxh)")
    paa("--output","-o",default='interval.jpg',
        help="Write output interval image to this file")
    paa("--angle",type=float,default=0,
        help="Rotate image by angle (degrees)")
    paa("--verbose","-v",action="count",default=0,
        help="verbose")
    args = argparser.parse_args()
    return args

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
