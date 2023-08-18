# Slice-n-dice: standalone routines for making composite images

This collection of libraries and routines began as homegrown software for making "time slices." A time-slice image begins with multiple photographs taken over a range of time. Such photos might for instance be combined to make a time-lapse movie, but instead they are combined to make a single image.  The image area is partitioned into slices, and each photo contributes one slice to the final image, with the resulting image having the property that time "moves" across the slices.  In the example below, time moves from lower left to upper right, and the dark slices in the upper right corner correspond to night having fallen in the scene.

![Time slices](https://live.staticflickr.com/65535/53050276339_37e54af1a2.jpg)

In addition to time slices, the software can do time "dices" (ie, tiles), and the time association can be sequential or random.  It can also do time averages, as well as both pixel-wise and tile-wise composites made from maximum, minimum, and "anomalous" pixels or tiles.  Most of these composites assume multiple input images, but there are also routines (eg, `jitterbox`) that work on single images. 

Some of these routines could (and probably should) be rewritten as [GIMP](https://www.gimp.org/GIMP) plug-ins, but for now all they all stand alone, and are meant to be run directly from a command line.

## List of Routines

### tiled:

Creates a composite image from tiles (which may be slices or dices) that are obtained from multiple input photos.  A typical usage (which gives classical time slices) might be:

	python -m tiled dir/DSC_*.JPG -t 0 1 -o timeslice.jpg
	
Here all the photos in directory `dir` matching the pattern `DSC_*.JPG` are taken as input, the image is tiled into vertical stripes with one stripe per input file, and the resulting output image is written to `timeslice.jpg`. You can also specify directory and files if they are numbered; eg:

	python -m tiled -d dir -n 1000-1020,1022-1050 -t 0 1 -o timeslice.jpg --angle 20 --random -v
	
Here, the directory is specified by `-d dir` and the files are identified with number range specified by `-n`; here, this includes files that are numbered 1000, 1001, 1002,..., 1050 but with 1021 excluded. One should also specify the pattern for the filenames, but here I've used the default: 'DSC_%04d.JPG'.  A few other options shown in this example: `-v` is verbose mode, and provides a tqdm-style progress bar; `--angle 20` puts the stripes at an angle of 20 degrees to the vertical; `--random` scrambles the order of the slices so that time does not move continually across the image.  In general, you can get a list of available options with 

	python -m tiled -h
	
The option `-t M N` specifies that tiles have `M` horizontal components and `N` vertical components.  If either `M=0` or `N=0` then they are replaced with the number of files that are in the input list.  In the example above, with 50 images, `-t 0 1` is equivalent to `-t 50 1`.

### gapify:

![The same creek, time sliced again](https://live.staticflickr.com/65535/53067177219_b0a221e0ed.jpg)

After an image is broken into tiles, the gapify routine can be used to add gaps between the tiles; these are by default black but the user can specify the desired color.  For example:

	python -m gapify timeslices.jpg -t 50 1 -g 10 --frame -o gaptimesices.jpg
	
Here, `-g 10` indicates that the gaps are ten pixels wide; `--frame` indicates that a frame (also ten pixels wide) will be drawn around the whole image. Note that the shorthand `-t 0 1` doesn't work for `gapify` since it doesn't know how many files were used to create `timeslices.jpg`. 

Also note that it is possible to use the `--angle` command with gapify, but beware: the effect of angular gaps is to make the image not preciesly rectangular anymore.  Go ahead and do it, but expect to do some post-processing and/or experimenting to get the boundary the way you like it.

### tiledanom:

Similar to `tiled`, but for each tile in the composite image, use the associated tile from the input images that is most anomalous with respect to the other associated tiles. (As currently implemented, "most anomalous" means maximum Euclidean distance from the mean tile.) 

![At the birdfeeder](https://live.staticflickr.com/65535/53098401288_310a825c6a.jpg)

In this example, based on hundreds of individual photos at a birdfeeder, the anomalous tiles tend to be the tiles that have birds in them.

### average:

Pixel-wise composite that produces an image that is the simple average of the input photographs.  Options are available to produce, instead of averages, min or max images, as well as averaging by the p-th power of the pixel values (to provide adjustable emphasis on bright pixels). Note that the RGB channels are treated independently, so the pixel with minimum red value might be different from the pixel with minimum blue value, but the resulting pixel will use both of those minimal values.

![Cape Flattery Average Water](https://live.staticflickr.com/65535/53017704910_7ac5822049.jpg)

[ToDo: make min/max work more like pixanom so that whole pixels are treated together, instead of having the channels treated separately]

### pixanom:

Pixel-wise composite that uses the most anomalous pixel value for every pixel location.

### jitterbox:

This routine (unlike most of the rest of the routines in this package) works with only a single input image; it breaks it into tiles, and then jitters the tiles to produce a jittered version of the image. Note that the tiles on the edge of an image have to be treated carefully so that the jittering is from a tile that does not extend outside the size of the image. Normally that is not noticeable, but if you try jittering whole stripes, that means no jittering will occur; to enable jittering beyond the edges of the image, use the `--pad` option. 

![too much coffee](https://live.staticflickr.com/65535/53097897181_e5a3b12e6c.jpg)

## Libraries

### tiles:

functions for tiling an image; provides the *Tile* and *Tiles* classes

### tangles:

routines for rotating an image, with help for angles larger than 45 degrees by using transpose to rotate by multiples of 90 degrees.

### multifile:

routines for more conveniently specifying a large set of file names for the input photographs. These support the `-d` (directory), `-n` (file number range), and `--inputpattern` options for specifying mulitple files on the command line.

## REQUIRES

Requires modules *verbose* and *intlist*

## AUTHOR

I am *theilr* and my photographs are available under that name on my [flickr.com/photos/theilr](http://flickr.com/photos/theilr) site.  In particular, the [space-time composites](https://www.flickr.com/photos/theilr/albums/72177720310074792) album illustrates a number of experiments with this software.

### VERSION

This code should be treated as version `0.x` by which I mean that changes may be made not only to implementation, but also to function names, library names, parameter input strings, and main programs.  If I do make any of those changes, I will also (try to remmeber to) update this README file. 

### COPYLEFT

These programs are free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License Version 3 as
published by the Free Software Foundation.

These programs are distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License at http://www.gnu.org/licenses for
more details.
