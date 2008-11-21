# -*- coding: utf-8 -*-

""" Panohead remote control.

License
=======

 - B{papywizard} (U{http://trac.gbiloba.org/papywizard}) is Copyright:
  - (C) 2007-2008 Frédéric Mantegazza

This software is governed by the B{CeCILL} license under French law and
abiding by the rules of distribution of free software.  You can  use, 
modify and/or redistribute the software under the terms of the CeCILL
license as circulated by CEA, CNRS and INRIA at the following URL
U{http://www.cecill.info}.

As a counterpart to the access to the source code and  rights to copy,
modify and redistribute granted by the license, users are provided only
with a limited warranty  and the software's author,  the holder of the
economic rights,  and the successive licensors  have only  limited
liability. 

In this respect, the user's attention is drawn to the risks associated
with loading,  using,  modifying and/or developing or reproducing the
software by the user in light of its specific status of free software,
that may mean  that it is complicated to manipulate,  and  that  also
therefore means  that it is reserved for developers  and  experienced
professionals having in-depth computer knowledge. Users are therefore
encouraged to load and test the software's suitability as regards their
requirements in conditions enabling the security of their systems and/or 
data to be ensured and,  more generally, to use and operate it in the 
same conditions as regards security. 

The fact that you are presently reading this means that you have had
knowledge of the CeCILL license and that you accept its terms.

Module purpose
==============

View

Implements
==========

- ImageArea
- MosaicImageArea
- PresetImageArea

@author: Frédéric Mantegazza
@copyright: (C) 2007-2008 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id: shooting.py 327 2008-06-25 14:29:36Z fma $"

import pygtk
pygtk.require("2.0")
import gtk


class ImageArea(object):
    """ ImageArea area object for mosaic.
    """
    def __init__(self, drawable, yaw, pitch, x, y, w, h, status, next=False):
        """  Init the ImageArea object.

        @param drawable: associated drawable
        @type drawable: {gtk.Window}

        @param yaw: yaw of the image (°)
        @type yaw: float

        @param pitch: pitch of the image (°)
        @type pich: float

        @param x: x coordinate of the image
        @type x: int

        @param y: y coordinate of the image
        @type y: int

        @param w: width of the image
        @type w: int

        @param h: height of the image
        @type h: int

        @param status: status of the picture, in
                       ('ok', 'okReshoot', 'error', 'errorReshoot', 'preview', 'skip')
        @type status: str

        @param next: if True, this picture is the next to shoot
        @type next: bool
        """
        #print "ImageArea.__init__()"
        self._drawable = drawable
        self.yaw = yaw
        self.pitch = pitch
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.status = status
        self.next = next

        # Create the GCs
        self._gcBorder = gtk.gdk.GC(drawable)
        self._gcBorder.set_rgb_fg_color(gtk.gdk.color_parse("#000000"))
        self._gcBorderNext = gtk.gdk.GC(drawable)
        self._gcBorderNext.set_rgb_fg_color(gtk.gdk.color_parse("#ffffff"))
        self._gcPreview = gtk.gdk.GC(drawable)
        self._gcPreview.set_rgb_fg_color(gtk.gdk.color_parse("#c0c0c0"))
        self._gcPreviewNoshoot = gtk.gdk.GC(drawable)
        self._gcPreviewNoshoot.set_rgb_fg_color(gtk.gdk.color_parse("#a0a0a0"))
        self._gcOk = gtk.gdk.GC(drawable)
        self._gcOk.set_rgb_fg_color(gtk.gdk.color_parse("#00ff00"))
        self._gcOkReshoot = gtk.gdk.GC(drawable)
        self._gcOkReshoot.set_rgb_fg_color(gtk.gdk.color_parse("#c0ffc0"))
        self._gcError = gtk.gdk.GC(drawable)
        self._gcError.set_rgb_fg_color(gtk.gdk.color_parse("#ff0000"))
        self._gcErrorReshoot = gtk.gdk.GC(drawable)
        self._gcErrorReshoot.set_rgb_fg_color(gtk.gdk.color_parse("#ffc0c0"))
        #self._gcBackground = gtk.gdk.GC(drawable)
        #self._gcBackground.set_rgb_fg_color(gtk.gdk.color_parse("#d0d0d0"))

    # Helpers

    # Interface
    def draw(self):
        """ Draw itself on the drawable.
        """
        #print "ImageArea.draw()"
        raise NotImplementedError

    def isCoordsIn(self, x, y):
        """ Check if given coords are in the pict. area.
        """
        #print "ImageArea.isInPict()"
        raise NotImplementedError


class MosaicImageArea(ImageArea):
    """
    """
    def draw(self):
        #print "MosaicImageArea.draw()"

        # Border
        if self.next:
            gc = self._gcBorderNext
        else:
            gc = self._gcBorder
        self._drawable.draw_rectangle(gc, True, self.x, self.y, self.w, self.h)

        # Inside
        if self.status == 'preview':
            gc = self._gcPreview
        elif self.status == 'skip':
            gc = self._gcPreviewNoshoot
        elif self.status == 'ok':
            gc = self._gcOk
        elif self.status == 'okReshoot':
            gc = self._gcOkReshoot
        elif self.status == 'error':
            gc = self._gcError
        elif self.status == 'errorReshoot':
            gc = self._gcErrorReshoot
        self._drawable.draw_rectangle(gc, True, self.x + 1, self.y + 1, self.w - 2, self.h - 2)

    def isCoordsIn(self, x, y):
        if self.x <= x <= (self.x + self.w) and \
           self.y <= y <= (self.y + self.h):
            return True
        else:
            return False


class PresetImageArea(ImageArea):
    """
    """
    def draw(self):
        #print "PresetImageArea.draw()"

        # Border
        if self.next:
            gc = self._gcBorderNext
        else:
            gc = self._gcBorder
        self._drawable.draw_arc(gc, True, self.x, self.y, self.w, self.h, 0, 360 * 64)

        # Inside
        if self.status == 'preview':
            gc = self._gcPreview
        elif self.status == 'skip':
            gc = self._gcPreviewNoshoot
        elif self.status == 'ok':
            gc = self._gcOk
        elif self.status == 'okReshoot':
            gc = self._gcOkReshoot
        elif self.status == 'error':
            gc = self._gcError
        elif self.status == 'errorReshoot':
            gc = self._gcErrorReshoot
        self._drawable.draw_arc(gc, True, self.x + 1, self.y + 1, self.w - 2, self.h - 2, 0, 360 * 64)

    def isCoordsIn(self, x, y):
        """
        @todo: make circle detection instead of square
        """
        if self.x <= x <= (self.x + self.w) and \
           self.y <= y <= (self.y + self.h):
            return True
        else:
            return False
