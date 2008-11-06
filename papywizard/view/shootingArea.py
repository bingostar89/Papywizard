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


class ShootingArea(gtk.DrawingArea):
    """ GTK ShootingArea widget
    """
    def __init__(self):
        """ Init ShootingArea widget.
        """
        gtk.DrawingArea.__init__(self)

        self._picts = OrderedDict()
        self._width = 300
        self._height = 150
        self.set_size_request(self._width, self._height)

        self._yawFov = None
        self._pitchFov = None
        self._yawCameraFov = None
        self._pitchCameraFov = None
        self._yawScale = None
        self._pitchScale = None

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
        self._yawFov = yawFov
        self._pitchFov = pitchFov
        self._yawCameraFov = yawCameraFov
        self._pitchCameraFov = pitchCameraFov
        #print "yawFov=%.1f, pitchFov=%.1f, yawCameraFov=%.1f, pitchCameraFov=%.1f" % (yawFov, pitchFov, yawCameraFov, pitchCameraFov)

        self.connect("configure-event", self._configure_cb)
        self.connect("expose-event", self._expose_cb)

    # Callbacks
    def _configure_cb(self, widget, event):
        """ Called when the drawing area changes size.

        This callback is also the first called when creating the widget.
        """
        self._set_colors({'back': "#d0d0d0", 'fg1': "#000000", 'fg2': "#80ff80", 'fg3': "#ff8080"})
        x, y, self._width, self._height = widget.get_allocation()
        #print "_width=%.1f, _height=%.1f" % (self._width, self._height)
        yawScale = self._width / self._yawFov
        pitchScale = self._height / self._pitchFov
        self._scale = min(yawScale, pitchScale)
        #print "yawScale=%f, pitchScale=%f, scale=%f" % (yawScale, pitchScale, self._scale)

        return True

    def _expose_cb(self, widget, event):
        """ Called when the drawing area is exposed.

        This is where to implement all drawing stuff.
        """
        raise NotImplementedError

    def refresh(self):
        """ Refresh the shooting area
        """
        #print "refresh()"
        self.queue_draw_area(0, 0, self._width, self._height)

    def add_pict(self, yawIndex, pitchIndex, status):
        """ Add a pict at yaw/pitch coordinates.

        @param yawIndex: pict yaw position index
        @type yawIndex: int

        @param pitchIndex: pict pitch position index
        @type pitchIndex: int

        @param status: status of the shooting at this position ('ok', 'error')
        @type status: str
        """
        #print "add_pict(yawIndex=%d, pitchIndex=%d)" % (yawIndex, pitchIndex)
        self._picts[(yawIndex, pitchIndex)] = status
        self.refresh()

    def clear(self):
        """ Clear the shooting area
        """
        #print "clear()"
        self._picts.clear()
        self.refresh()

    def _set_colors(self, colors):
        #print "set_colors()"
        for widget, color in colors.iteritems():
            exec "self._%s = gtk.gdk.GC(self.window)" % widget
            exec "self._%s.set_rgb_fg_color(gtk.gdk.color_parse('%s'))" % (widget, color)


class MosaicArea(ShootingArea):
    """ GTK MosaicArea widget
    """
    def __init__(self):
        """ Init MosaicArea widget.
        """
        ShootingArea.__init__(self)

        self.__yawOffset = None
        self.__pitchOffset = None
        self.__yawStart = None
        self.__yawEnd = None
        self.__pitchStart = None
        self.__pitchEnd = None
        self.__yawOverlap = None
        self.__pitchOverlap = None

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
        self.__yawStart = yawStart
        self.__yawEnd = yawEnd
        self.__pitchStart = pitchStart
        self.__pitchEnd = pitchEnd
        self.__yawOverlap = yawOverlap
        self.__pitchOverlap = pitchOverlap

        ShootingArea.init(self, yawFov, pitchFov, yawCameraFov, pitchCameraFov)

    # Callbacks
    def _configure_cb(self, widget, event):
        ShootingArea._configure_cb(self, widget, event)

        self.__yawOffset = (self._width - self._yawFov * self._scale) / 2.
        self.__pitchOffset = (self._height - self._pitchFov * self._scale) / 2.
        #print "yawOffset=%f, pitchOffset=%f" % (self.__yawOffset, self.__pitchOffset)

        return True

    def _expose_cb(self, widget, event):

        # Draw background
        xBack = int(round(self.__yawOffset))
        yBack = int(round(self.__pitchOffset))
        wBack = self._width - int(round(2 * self.__yawOffset))
        hBack = self._height - int(round(2 * self.__pitchOffset))
        self.window.draw_rectangle(self._back, True, xBack, yBack, wBack, hBack)
        #print "xBack=%d, yBack=%d, wBack=%d, hBack=%d" % (xBack, yBack, wBack, hBack)

        ## Draw 360°x180° area
        #xFull = int(round(self._width / 2. - 180 * self._scale))
        #yFull = int(round(self._height / 2. - 90 * self._scale))
        #wFull = int(round(360 * self._scale))
        #hFull = int(round(180 * self._scale))
        ##print "xFull=%.1f, yFull=%.1f, wFull=%.1f, hFull=%.1f" % (xFull, yFull, wFull, hFull)
        #self.window.draw_rectangle(self._fg3, False, xFull, yFull, wFull, hFull)

        # Draw picts
        for i, ((yaw, pitch), status) in enumerate(self._picts.iteritems()):
            if cmp(self.__yawEnd, self.__yawStart) > 0:
                yaw -= self.__yawStart
            else:
                yaw -= self.__yawEnd
            if cmp(self.__pitchEnd, self.__pitchStart) > 0:
                pitch -= self.__pitchStart
            else:
                pitch -= self.__pitchEnd
            x = int(round(yaw * self._scale + self.__yawOffset))
            y = int(round(pitch * self._scale + self.__pitchOffset))
            w = int(round(self._yawCameraFov * self._scale))
            h = int(round(self._pitchCameraFov * self._scale))
            y = self._height - y - h
            #print "pict=%d, yaw=%.1f, pitch=%.1f, x=%.1f, y=%.1f, w=%.1f, h=%.1f" % (i + 1, yaw, pitch, x, y, w, h)
            self.window.draw_rectangle(self._fg1, True, x, y, w, h)
            if status != 'preview2':
                x += 1
                y += 1
                w -= 2
                h -= 2
                if status == 'ok':
                    gc = self._fg2
                elif status == 'preview':
                    gc = self._back
                else:
                    gc = self._fg3
                self.window.draw_rectangle(gc, True, x, y, w, h)

        return False


class PresetArea(ShootingArea):
    """ GTK PresetArea widget
    """
    def __init__(self):
        ShootingArea.__init__(self)

        self.__yawMargin = None
        self.__pitchMargin = None

    # Callbacks
    def _configure_cb(self, widget, event):
        ShootingArea._configure_cb(self, widget, event)

        self.__yawMargin = int(round((self._width - 360. * self._scale) / 2.))
        self.__pitchMargin = int(round((self._height - 180. * self._scale) / 2.))
        #print "yawMargin=%d, pitchMargin=%d" % (self.__yawMargin, self.__pitchMargin)

        return True

    def _expose_cb(self, widget, event):

        # Draw background
        self.window.draw_rectangle(self._back, True, 0, 0, self._width, self._height)

        # Draw 360°x180° area and axis
        xFull = int(round(self._width / 2. - 180 * self._scale))
        yFull = int(round(self._height / 2. - 90 * self._scale))
        wFull = int(round(360 * self._scale)) - 1
        hFull = int(round(180 * self._scale)) - 1
        #print "xFull=%.1f, yFull=%.1f, wFull=%.1f, hFull=%.1f" % (xFull, yFull, wFull, hFull)
        self.window.draw_rectangle(self._fg3, False, xFull, yFull, wFull, hFull)
        x1 = 0
        y1 = int(round(self._height / 2.)) + 1
        x2 = self._width
        y2 = y1
        self.window.draw_line(self._fg3, x1, y1, x2, y2)
        x1 = self.__yawMargin
        y1 = 0
        x2 = x1
        y2 = self._height
        self.window.draw_line(self._fg3, x1, y1, x2, y2)

        # Draw picts
        for i, ((yaw, pitch), status) in enumerate(self._picts.iteritems()):
            pitch = 180 / 2. - pitch
            x = int(round(yaw * self._scale - self._yawCameraFov * self._scale / 2.)) + self.__yawMargin
            y = int(round(pitch * self._scale - self._pitchCameraFov * self._scale / 2.)) + self.__pitchMargin
            w = int(round(self._yawCameraFov * self._scale))
            h = int(round(self._pitchCameraFov * self._scale))
            #print "pict=%d, yaw=%.1f, pitch=%.1f, x=%.1f, y=%.1f, w=%.1f, h=%.1f" % (i + 1, yaw, pitch, x, y, w, h)
            #self.window.draw_rectangle(self._fg1, True, x, y, w, h)
            self.window.draw_arc(self._fg1, True, x, y, w, h, 0, 360 * 64)
            if status != 'preview2':
                x += 1
                y += 1
                w -= 2
                h -= 2
                if status == 'ok':
                    gc = self._fg2
                elif status == 'preview':
                    gc = self._back
                else:
                    gc = self._fg3
                #self.window.draw_rectangle(gc, True, x, y, w, h)
                self.window.draw_arc(gc, True, x, y, w, h, 0, 360 * 64)

        return False
