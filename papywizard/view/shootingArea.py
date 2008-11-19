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

- ShootingArea
- MosaicArea
- PresetArea

@author: Frédéric Mantegazza
@copyright: (C) 2007-2008 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id: shooting.py 327 2008-06-25 14:29:36Z fma $"

import pygtk
pygtk.require("2.0")
import gtk

from papywizard.common.orderedDict import OrderedDict
from papywizard.view.imageArea import ImageArea


class ShootingArea(gtk.DrawingArea):
    """ GTK ShootingArea widget
    """
    def __init__(self):
        """ Init ShootingArea widget.
        """
        #print "ShootingArea.__init__()"
        gtk.DrawingArea.__init__(self)

        # Enable low-level signals
        self.set_events(gtk.gdk.BUTTON_PRESS_MASK)

        self._picts = OrderedDict()
        self.width = 300
        self.height = 150
        self.set_size_request(self.width, self.height)

        self._yawFov = None
        self._pitchFov = None
        self.yawCameraFov = None
        self.pitchCameraFov = None

    # Properties
    def _getScale(self):
        """
        """
        #print "ShootingArea._getScale()"
        yawScale = self.width / self._yawFov
        pitchScale = self.height / self._pitchFov
        scale = min(yawScale, pitchScale)
        #print "yawScale=%f, pitchScale=%f, scale=%f" % (yawScale, pitchScale, scale)
        return scale

    scale = property(_getScale, "Drawing scale")

    # Callbacks
    def _configure_cb(self, widget, event):
        """ Called when the drawing area changes size.

        This callback is also the first called when creating the widget.
        """
        #print "ShootingArea._configure_cb()"
        self._gcBackground = gtk.gdk.GC(self.window)
        self._gcBackground.set_rgb_fg_color(gtk.gdk.color_parse("#d0d0d0"))
        self._gcAxis = gtk.gdk.GC(self.window)
        self._gcAxis.set_rgb_fg_color(gtk.gdk.color_parse("#ff8080"))
        x, y, self.width, self.height = widget.get_allocation()
        #print "_width=%.1f, _height=%.1f" % (self.width, self.height)

        return True

    def _expose_cb(self, widget, event):
        """ Called when the drawing area is exposed.

        This is where to implement all drawing stuff.
        """
        #print "ShootingArea._expose_cb()"
        raise NotImplementedError

    # Helpers

    # Interface
    def init(self, yawFov, pitchFov, yawCameraFov, pitchCameraFov):
        """ Init internal values.

        @param yawFov: yaw fov (°)
        @type yawFov: float

        @param pitchFov: pitch fov (°)
        @type pitchFov: float

        @param yawCameraFov: pict yaw fov (°)
        @type yawCameraFov: float

        @param pitchCameraFov: pict pitch fov (°)
        @type pitchCameraFov: float
        """
        #print "ShootingArea.init()"
        self._picts.clear()
        self._yawFov = yawFov
        self._pitchFov = pitchFov
        self.yawCameraFov = yawCameraFov
        self.pitchCameraFov = pitchCameraFov
        ##print "yawFov=%.1f, pitchFov=%.1f, yawCameraFov=%.1f, pitchCameraFov=%.1f" % (yawFov, pitchFov, yawCameraFov, pitchCameraFov)

        self.connect("configure-event", self._configure_cb)
        self.connect("expose-event", self._expose_cb)

    def refresh(self):
        """ Refresh the shooting area
        """
        #print "ShootingArea.refresh()"
        ##print "refresh()"
        self.queue_draw_area(0, 0, self.width, self.height)

    def add_pict(self, yaw, pitch, status):
        """ Add a pict at yaw/pitch coordinates.

        @param yaw: pict yaw position (°)
        @type yaw: float

        @param pitch: pict pitch position (°)
        @type pitch: float

        @param status: status of the shooting at this position ( 'preview', 'ok', 'error')
        @type status: str
        """
        #print "ShootingArea.add_pict()"
        raise NotImplementedError

    def clear(self):
        """ Clear the shooting area
        """
        #print "ShootingArea.clear()"
        for image in self._picts.itervalues():
            image.status = 'preview'
        self.refresh()

    def get_selected_image_index(self, x, y):
        """
        """
        keys = self._picts.keys()
        keys.reverse()
        for i, key in enumerate(keys):
            index = len(self._picts) - i
            image = self._picts[key]
            if image.isCoordsIn(x, y):
                #print "ShootingArea.get_selected_image(): index=%d, status=%s" % (index , image.status)

                # Click in a shot image
                if image.status != 'sdfpreview':

                    # Change status of images
                    for i, image in enumerate(self._picts.itervalues()):
                        if i + 1 < index:
                            if image.status == 'okReshoot':
                                image.status = 'ok'
                            elif image.status == 'errorReshoot':
                                image.status = 'error'
                            elif image.status == 'preview':
                                image.status = 'skip'
                        else:
                            if image.status == 'ok':
                                image.status = 'okReshoot'
                            elif image.status == 'error':
                                image.status = 'errorReshoot'
                            elif image.status == 'skip':
                                image.status = 'preview'

                else:

                    # Change status of images
                    for i, image in enumerate(self._picts.itervalues()):
                        if image.status == 'okReshoot':
                            image.status = 'ok'
                        elif image.status == 'errorReshoot':
                            image.status = 'error'

                self.refresh()

                return index


class MosaicArea(ShootingArea):
    """ GTK MosaicArea widget
    """
    def __init__(self):
        """ Init MosaicArea widget.
        """
        #print "MosaicArea.__init__()"
        ShootingArea.__init__(self)

        self.yawStart = None
        self.yawEnd = None
        self.pitchStart = None
        self.pitchEnd = None
        self.__yawOverlap = None
        self.__pitchOverlap = None

    # Helpers
    def __getYawOffset(self):
        """
        """
        yawOffset = (self.width - self._yawFov * self.scale) / 2.
        #print "yawOffset=%f" % yawOffset
        return yawOffset

    yawOffset = property(__getYawOffset, "Yaw drawing offset")

    def __getPitchOffset(self):
        """
        """
        pitchOffset = (self.height - self._pitchFov * self.scale) / 2.
        #print "pitchOffset=%f" % pitchOffset
        return pitchOffset

    pitchOffset = property(__getPitchOffset, "Pitch drawing offset")

    # Callbacks
    #def _configure_cb(self, widget, event):
        ##print "MosaicArea._configure_cb()"

        #ShootingArea._configure_cb(self, widget, event)

        #return True

    def _expose_cb(self, widget, event):
        #print "MosaicArea._expose_cb()"

        # Draw background
        xBack = int(round(self.yawOffset))
        yBack = int(round(self.pitchOffset))
        wBack = self.width - int(round(2 * self.yawOffset))
        hBack = self.height - int(round(2 * self.pitchOffset))
        self.window.draw_rectangle(self._gcBackground, True, xBack, yBack, wBack, hBack)
        #print "xBack=%d, yBack=%d, wBack=%d, hBack=%d" % (xBack, yBack, wBack, hBack)

        # Draw picts
        for image in self._picts.itervalues():
            image.draw()

        return False

    # Helpers

    # Interface
    def init(self, yawStart, yawEnd, pitchStart, pitchEnd, yawFov, pitchFov, yawCameraFov, pitchCameraFov, yawOverlap, pitchOverlap):
        """ Init internal values.

        @param yawStart: yaw start position (°)
        @type yawStart: float

        @param yawEnd: yaw end position (°)
        @type yawEnd: float

        @param pitchStart: pitch start position (°)
        @type pitchStart: float

        @param pitchEnd: pitch end position (°)
        @type pitchEnd: float

        @param yawFov: yaw fov (°)
        @type yawFov: float

        @param pitchFov: pitch fov (°)
        @type pitchFov: float

        @param yawCameraFov: pict yaw fov (°)
        @type yawCameraFov: float

        @param pitchCameraFov: pict pitch fov (°)
        @type pitchCameraFov: float

        @param yawOverlap: yaw real overlap (ratio)
        @type yawOverlap: float

        @param pitchOverlap: pitch overlap (ratio)
        @type pitchOverlap: float
        """
        #print "MosaicArea.init()"
        ShootingArea.init(self, yawFov, pitchFov, yawCameraFov, pitchCameraFov)
        self.yawStart = yawStart
        self.yawEnd = yawEnd
        self.pitchStart = pitchStart
        self.pitchEnd = pitchEnd
        self.__yawOverlap = yawOverlap
        self.__pitchOverlap = pitchOverlap

    def add_pict(self, yaw, pitch, status):
        #print "MosaicArea.add_pict(%.1f, %.1f)" % (yaw, pitch)

        # Check if image aready in list
        try:
            image = self._picts["%.1f, %.1f" % (yaw, pitch)]
            image.status = status

        except KeyError:
            image = MosaicImageArea(self, yaw, pitch, status)
            self._picts["%.1f, %.1f" % (yaw, pitch)] = image

        self.refresh()


class PresetArea(ShootingArea):
    """ GTK PresetArea widget
    """
    def __init__(self):
        ShootingArea.__init__(self)

    # Properties
    def __getYawMargin(self):
        """
        """
        yawMargin = int(round((self.width - 360. * self.scale) / 2.))
        #print "yawMargin=%d" % yawMargin
        return yawMargin

    yawMargin = property(__getYawMargin)

    def __getPitchMargin(self):
        """
        """
        pitchMargin = int(round((self.height - 180. * self.scale) / 2.))
        #print "pitchMargin=%d" % pitchMargin
        return pitchMargin

    pitchMargin = property(__getPitchMargin)

    # Callbacks
    #def _configure_cb(self, widget, event):
        #ShootingArea._configure_cb(self, widget, event)

        #self.__yawMargin = int(round((self._width - 360. * self._scale) / 2.))
        #self.__pitchMargin = int(round((self._height - 180. * self._scale) / 2.))
        ##print "yawMargin=%d, pitchMargin=%d" % (self.__yawMargin, self.__pitchMargin)

        #return True

    def _expose_cb(self, widget, event):

        # Draw background
        self.window.draw_rectangle(self._gcBackground, True, 0, 0, self.width, self.height)

        # Draw 360°x180° area and axis
        xFull = int(round(self.width / 2. - 180 * self.scale))
        yFull = int(round(self.height / 2. - 90 * self.scale))
        wFull = int(round(360 * self.scale)) - 1
        hFull = int(round(180 * self.scale)) - 1
        ##print "xFull=%.1f, yFull=%.1f, wFull=%.1f, hFull=%.1f" % (xFull, yFull, wFull, hFull)
        self.window.draw_rectangle(self._gcAxis, False, xFull, yFull, wFull, hFull)
        x1 = 0
        y1 = int(round(self.height / 2.)) + 1
        x2 = self.width
        y2 = y1
        self.window.draw_line(self._gcAxis, x1, y1, x2, y2)
        x1 = self.yawMargin
        y1 = 0
        x2 = x1
        y2 = self.height
        self.window.draw_line(self._gcAxis, x1, y1, x2, y2)

        # Draw picts
        for image in self._picts.itervalues():
            image.draw()

        return False

    # Helpers

    # Interface
    def add_pict(self, yaw, pitch, status):
        #print "PresetArea.add_pict(%.1f, %.1f)" % (yaw, pitch)

        # Check if image aready in list
        try:
            image = self._picts["%.1f, %.1f" % (yaw, pitch)]
            image.status = status

        except KeyError:
            image = PresetImageArea(self, yaw, pitch, status)
            self._picts["%.1f, %.1f" % (yaw, pitch)] = image

        self.refresh()
