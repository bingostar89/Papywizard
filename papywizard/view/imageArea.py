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
    def __init__(self, shootingArea, yaw, pitch, status):
        """  Init the ImageArea object.

        @param shootingArea: associated shooting area
        @type drawable: {ShootingArea}

        @param yaw: yaw coordinate of the image (°)
        @type yaw: float

        @param pitch: pitch coordinate of the image (°)
        @type pitch: float

        @param status: status of the picture,
                       in ('ok', 'okReshoot', 'error', 'errorReshoot', 'preview', 'skip')
        @type status: str
        """
        #print "ImageArea.__init__()"
        self._shootingArea = shootingArea
        self._yaw = yaw
        self._pitch = pitch
        self.status = status

        # Create the GCs
        drawable = self._shootingArea.window
        self._gcBorder = gtk.gdk.GC(drawable)
        self._gcBorder.set_rgb_fg_color(gtk.gdk.color_parse("#000000"))
        self._gcBorderSelected = gtk.gdk.GC(drawable)
        self._gcBorderSelected.set_rgb_fg_color(gtk.gdk.color_parse("#8080ff"))
        self._gcPreview = gtk.gdk.GC(drawable)
        self._gcPreview.set_rgb_fg_color(gtk.gdk.color_parse("#c0c0c0"))
        self._gcPreviewNoshoot = gtk.gdk.GC(drawable)
        self._gcPreviewNoshoot.set_rgb_fg_color(gtk.gdk.color_parse("#a0a0a0"))
        self._gcOk = gtk.gdk.GC(drawable)
        self._gcOk.set_rgb_fg_color(gtk.gdk.color_parse("#80ff80"))
        self._gcOkReshoot = gtk.gdk.GC(drawable)
        self._gcOkReshoot.set_rgb_fg_color(gtk.gdk.color_parse("#c0ffc0"))
        self._gcError = gtk.gdk.GC(drawable)
        self._gcError.set_rgb_fg_color(gtk.gdk.color_parse("#ff8080"))
        self._gcErrorReshoot = gtk.gdk.GC(drawable)
        self._gcErrorReshoot.set_rgb_fg_color(gtk.gdk.color_parse("#ffc0c0"))
        #self._gcBackground = gtk.gdk.GC(drawable)
        #self._gcBackground.set_rgb_fg_color(gtk.gdk.color_parse("#d0d0d0"))

    # Helpers
    def _computeCoords(self, yaw, pitch):
        """ Compute the image coordinates.

        @param yaw: yaw position of the image (°)
        @type yaw: float

        @param pitch: pitch position of the image (°)
        @type pitch: float

        @return x, y, w, h: coordinates of the image
        @rtype: tuple of int
        """
        raise NotImplementedError

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
    def _computeCoords(self):
        if cmp(self._shootingArea.yawEnd, self._shootingArea.yawStart) > 0:
            yaw = self._yaw - self._shootingArea.yawStart
        else:
            yaw = self._yaw - self._shootingArea.yawEnd
        if cmp(self._shootingArea.pitchEnd, self._shootingArea.pitchStart) > 0:
            pitch = self._pitch - self._shootingArea.pitchStart
        else:
            pitch = self._pitch - self._shootingArea.pitchEnd
        x = int(round(yaw * self._shootingArea.scale + self._shootingArea.yawOffset))
        y = int(round(pitch * self._shootingArea.scale + self._shootingArea.pitchOffset))
        w = int(round(self._shootingArea.yawCameraFov * self._shootingArea.scale))
        h = int(round(self._shootingArea.pitchCameraFov * self._shootingArea.scale))
        y = self._shootingArea.height - y - h
        #print "MosaicImageArea._computeCoords(): x=%.1f, y=%.1f, w=%.1f, h=%.1f" % (x, y, w, h)

        return x, y, w, h

    def draw(self):
        #print "MosaicImageArea.draw()"
        drawable = self._shootingArea.window
        x, y, w, h = self._computeCoords()

        # Border
        drawable.draw_rectangle(self._gcBorder, True, x, y, w, h)

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
        drawable.draw_rectangle(gc, True, x + 1, y + 1, w - 2, h - 2)

    def isCoordsIn(self, x, y):
        _x, _y, _w, _h = self._computeCoords()
        if _x <= x <= (_x + _w) and \
           _y <= y <= (_y + _h):
            return True
        else:
            return False


class PresetImageArea(ImageArea):
    """
    """
    def _computeCoords(self):
        scale = self._shootingArea.scale
        pitch = 180 / 2. - self._pitch
        x = int(round(self._yaw * scale - self._shootingArea.yawCameraFov * scale / 2.)) + self._shootingArea.yawMargin
        y = int(round(pitch * scale - self._shootingArea.pitchCameraFov * scale / 2.)) + self._shootingArea.pitchMargin
        w = int(round(self._shootingArea.yawCameraFov * scale))
        h = int(round(self._shootingArea.pitchCameraFov * scale))
        #print "PresetImageArea._computeCoords(): x=%.1f, y=%.1f, w=%.1f, h=%.1f" % (x, y, w, h)

        return x, y, w, h

    def draw(self):
        #print "PresetImageArea.draw()"
        drawable = self._shootingArea.window
        x, y, w, h = self._computeCoords()

        # Border
        drawable.draw_arc(self._gcBorder, True, x, y, w, h, 0, 360 * 64)

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
        drawable.draw_arc(gc, True, x + 1, y + 1, w - 2, h - 2, 0, 360 * 64)

    def isCoordsIn(self, x, y):
        """
        @todo: make circle detection instead of square
        """
        _x, _y, _w, _h = self._computeCoords()
        if _x <= x <= (_x + _w) and \
           _y <= y <= (_y + _h):
            return True
        else:
            return False
