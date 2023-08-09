'''specify a "range" of files'''
from util.intlist import str_intgen

def files_fromstring(str_intrange,**kw):
    intrange = str_intgen(str_intrange)
    return files_fromintlist(intrange,**kw)    

def files_fromintlist(intlist,dir='.',pattern='DSC_%04d.JPG'):
    return [dir + '/' + pattern % n
            for n in intlist]

def addargs(ap):
    '''add argparse arguments for: files, directory, numbers, and pattern'''
    paa = ap.add_argument
    paa("files",nargs='*',
        help="Image files to be merged")
    paa("--inputdir","-d",
        help="Directory for image files")
    paa("--inputnum","-n",
        help="Range of numbers for input files, eg 9700-9737")
    paa("--inputpattern",default="DSC_%04d.JPG",
        help="filename pattern; eg DSC_%04d.JPG")

def getfiles(args):
    if args.files:
        allfiles = args.files
    else:
        allfiles = files_fromstring(args.inputnum,
                                    dir=args.inputdir,
                                    pattern=args.inputpattern)
    return allfiles

if __name__ == "__main__":

    f = files('9700-9736',dir='2023_06_06a')
    print(f)
    
