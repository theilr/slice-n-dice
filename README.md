# Standalone image processing routines for making composite images

This is a collection of libraries and routines for image processing, but separate from *GIMP*.  Most of these involve creating composites from multple input photographs (which is part of why they stand alone from *GIMP*).  

It is possible that they will at some point be incorporated into the gimp-frastructure package.

## Routines

## iminfo:

Provides basic information about an input image (eg, size; also basic EXIF info for JPEG images)

### average:

Pixel-wise composite that produces a composite that is the simple average of the input photographs.  Options are available to produce, instead of averages, min or max images, as well as averaging by the p-th power of the pixel values.  Note that the RGB channels are treated independently, so the pixel with minimum red value might be different from the pixel with minimum blue value, but the resulting pixel will use both of those minimal values.

[ToDo: make min/max work more like pixanom so that whole pixels are treated together, instead of having the channels treated separately (perhaps this works better in the pixanom routine?)]

### pixanom:

Pixel-wise composite that uses the most anomalous pixel value for every pixel location.

### tiled:

Used for making time slices (and time "dices") from mulitple images, time can be sequential order (in order as the individual photo files are read in), or in random order. The image area is broken into MxN tiles, and the composite image is created by pasting the tile from the appropriate input photo into each tile location.  

Specifying M=0 (or N=0) is shorthand for the total number fof input files

### tiledanom:

Similar to tiled, but for each tile produces the most anomalous from the stack of tiles associated with that tile position.  Most anomalous is defined as largest Euclidean distance (in RGB space) from the mean tile.

### jitterbox:

This routine (unlike most of the rest of the routines in this package) works with only a single input image; it breaks it into tiles, and then jitters the tiles to produce a jittered version of the image. Kind of like pixel spread, but 1/ for tiles and 2/ the jitter is at the pixel and not the tile level.

### gapify/gapify2d:

After an image is broken into tiles, the gapify routines can be used to add gaps between the tiles; these are by default black but the user can specify the desired color.

## Libraries

### tiles.py:

functions for tiling an image; provides the *Tile* and *Tiles* classes

### tangles.py:

routines for rotating an image, with help for angles larger than 45 degrees by using transpose to rotate by multiples of 90 degrees.

### multifile.py

routines for more conveniently specifying a large set of file names for the input photographs.

## REQUIRES

Requires modules *verbose* and *intlist*
