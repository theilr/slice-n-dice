'''add gaps to a timeslice image (or to any image)'''

import sys
import argparse
import random
from PIL import Image
import verbose as v

def _getargs():
    '''parse options from command line'''
    argparser = argparse.ArgumentParser(description=__doc__)
    paa = argparser.add_argument
    paa("file",
        help="Image file to be gapped")
    paa("--tiles","-t",nargs=2,type=int,required=True,
        help="Tuple with number of horizontal,vertical stripes (will be T-1 gaps)")
    paa("--gap","-g",type=int,default=0,
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

    nwstripes,nhstripes = args.tiles
    basefile = args.file
    framegap = args.gap if args.frame else 0
    with Image.open(basefile) as baseim:
        owidth,oheight = baseim.size 
        if args.angle:
            baseim = baseim.rotate(args.angle,expand=True)
        width,height = baseim.size

        gwidth = width + (nwstripes-1)*args.gap + 2*framegap
        gheight = height + (nhstripes-1)*args.gap + 2*framegap
        v.vprint(f'G: {gwidth}x{gheight}')
        gapim = Image.new('RGB',(gwidth,gheight),
                          color=args.color)

        for nw in range(nwstripes):
            for nh in range(nhstripes):
                wlo = nw*width//nwstripes
                whi = (1+nw)*width//nwstripes
                hlo = nh*height//nhstripes
                hhi = (1+nh)*height//nhstripes
                box = (wlo,hlo,whi,hhi)
                          
                gwlo = wlo + nw*args.gap + framegap
                gwhi = gwlo + (whi-wlo)
                ghlo = hlo + nh*args.gap + framegap
                ghhi = ghlo + (hhi-hlo)
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
