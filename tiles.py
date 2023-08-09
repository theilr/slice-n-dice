import random

class Tile:
    def __init__(self,iw=0,ih=0,ndx=0):
        self.iw = iw
        self.ih = ih
        self.ndx = ndx

    def box(self,npixels,ntiles):
        nwpix,nhpix = npixels
        nwtil,nhtil = ntiles
        wlo = (0+self.iw) * nwpix // nwtil
        whi = (1+self.iw) * nwpix // nwtil
        hlo = (0+self.ih) * nhpix // nhtil
        hhi = (1+self.ih) * nhpix // nhtil
        return (wlo,hlo,whi,hhi)
        
class Tiles:
    def __init__(self,ntiles=(1,1)):
        self.ntiles=ntiles
        self.tiles = []
        for ih in range(self.ntiles[1]):
            for iw in range(self.ntiles[0]):
                self.tiles.append(Tile(iw,ih))
        self.setup=False
        
    def setup_sequential(self,nfiles=1):
        ## everybody gets a turn
        for ndx,tile in enumerate(self.tiles):
            tile.ndx = ndx%nfiles
        self.setup=True
        return self

    def setup_brick(self,nfiles=1,nblocks=5):
        ## tiles are like bricks, 1xnblocks
        ## with staggered starting at each row
        ndx = 0
        for tile in self.tiles:
            ndx = ndx+1
            if tile.iw == 0:
                ndx = nblocks*(ndx//nblocks)
                ndx += ((nblocks//2)*tile.ih) % nblocks
            tile.ndx = (ndx//nblocks)%nfiles
        self.setup=True
        return self
        
    def setup_random(self,nfiles=1):
        ## iid random (ie, with replacement)
        ## (could end up leaving some out)
        for tile in self.tiles:
            tile.ndx = random.randrange(nfiles)
        self.setup=True
        return self

    def setup_shuffle(self,nfiles=1):
        ## like _random but makes sure everybody gets their turn
        if not self.setup:
            self.setup_sequential(nfiles=nfiles)
        ndxlist = [tile.ndx for tile in self.tiles]
        random.shuffle(ndxlist)
        for ndx,tile in zip(ndxlist,self.tiles):
            tile.ndx = ndx
        return self

    def reshuffle(self):
        ## equivalent to random ordering of input files
        ## respects, for instance, "brick" structure
        assert self.setup
        ndxlist = [tile.ndx for tile in self.tiles]
        nfiles = max(ndxlist)+1
        newndx = list(range(nfiles))
        random.shuffle(newndx)
        for tile in self.tiles:
            tile.ndx = newndx[tile.ndx]
        return self            

    def get_boxes_with_ndx(self,ndx,npixels):
        '''use ndx=None to get all boxes'''
        if not self.setup:
            v.vprint('Need to setup tiles')
        boxlist = []
        for tile in self.tiles:
            if ndx is None or tile.ndx == ndx:
                boxlist.append( tile.box(npixels,self.ntiles) )
        return boxlist

    def get_boxes(self,npixels):
        '''get all boxes'''
        return get_boxes_with_ndx(self,None,npixels)
