'''transfer exif info from one image to another'''
## many packages (eg focus-stack) process imagery and produce an output image
## that has no exif information; this way you can take the input image's
## exif info, and place it into the processed image
## I suppose it could be used in nefarious ways, as well...

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
    paa("--output","-o",
        help="Output file (over-write input if not specified")
    paa("--exiffile","-e",required=True,
        help="Input file that has EXIF info")
    paa("--input","-i",required=True,
        help="Input file into which you want EXIF info placed")
    paa("--verbose","-v",action="count",default=0,
        help="verbose")
    args = argparser.parse_args()
    return args

def _main(args):
    '''main'''
    v.vprint(args)

    outfile = args.output or args.input

    exif = None
    with Image.open(args.exiffile) as img_exif:
        exif = img_exif.getexif()
    if exif is None:
        raise RuntimeError("No EXIF is available")
    v.vprint('EXIF:\n',exif)
    for n in exif:
        if isinstance(exif[n],str):
            exif[n] = exif[n].strip().strip('\x00')
    v.vprint('EXIF:\n',exif)
    img = Image.open(args.input)
    v.vprint('Wriging image to: ',outfile)
    img.save(outfile,quality="high",exif=exif)
        
if __name__ == "__main__":

    _args = _getargs()
    v.verbosity(_args.verbose)
    _main(_args)
