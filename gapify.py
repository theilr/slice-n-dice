'''add gaps to a timeslice image (or to any image)'''

import sys
import argparse
import random
from PIL import Image
import verbose as v
from tqdm import tqdm

def _getargs():
    '''parse options from command line'''
    argparser = argparse.ArgumentParser(description=__doc__)
    paa = argparser.add_argument
    paa("file",
        help="Image file to be gapped")
    paa("-N","-n",type=int,required=True,
        help="Number of stripes (will be N-1 gaps)")
    paa("--gap","-g",type=int,
        help="Number of pixels in each gap")
    paa("--frame",action="store_true",
        help="Include a frame around the whole image")
    paa("--color",
        help="Color for frame/gaps")
    paa("--output","-o",default='gapped.jpg',
        help="Write output gapped image to this file")
    paa("--angle",type=float,default=0,
        help="Rotate image by angle (degrees)")
    paa("--verbose","-v",action="count",default=0,
        help="verbose")
    args = argparser.parse_args()
    return args

def _main(args):
    '''main'''
    v.vprint(args)

    nstripes = args.N
    basefile = args.file
    framegap = args.gap if args.frame else 0
    with Image.open(basefile) as baseim:
        owidth,oheight = baseim.size 
        if args.angle:
            baseim = baseim.rotate(args.angle,expand=True)
        width,height = baseim.size

        gwidth = width + (nstripes-1)*args.gap + 2*framegap
        gheight = height + 2*framegap
        gapim = Image.new('RGB',(gwidth,gheight),
                          color=args.color)

        for n in range(nstripes):
            wlo = n*width//nstripes
            whi = (1+n)*width//nstripes
            box = (wlo,0,whi,height)
                          
            gwlo = wlo + n*args.gap + framegap
            gwhi = gwlo + (whi-wlo)
            ghlo = framegap
            ghhi = ghlo + height
            gbox = (gwlo,ghlo,gwhi,ghhi)

            region = baseim.crop(box)
            gapim.paste(region,gbox)

        if args.angle:
            ## fixme!
            gapim = gapim.rotate(-args.angle,expand=False)
            if False:
                gapim = gapim.crop(((width-owidth)//2,(height-oheight)//2,
                                    (width+owidth)//2,(height+oheight)//2))
        gapim.save(args.output,quality="high",exif=baseim.getexif())
    
if __name__ == "__main__":

    _args = _getargs()
    v.verbosity(_args.verbose)
    _main(_args)
