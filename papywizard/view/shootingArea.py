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

from papywizard.common import config
from papywizard.common.configManager import ConfigManager
from papywizard.common.orderedDict import OrderedDict
from papywizard.view.imageArea import MosaicImageArea, PresetImageArea


class ShootingArea(gtk.DrawingArea):
    """ GTK ShootingArea widget
    """
    def __init__(self):
        """ Init ShootingArea widget.
        """
        #print "ShootingArea.__init__()"
        gtk.DrawingArea.__init__(self)

        # Enable low-level signals
        self.set_events(gtk.gdk.BUTTON_PRESS_MASK |
                        gtk.gdk.POINTER_MOTION_MASK |
                        gtk.gdk.POINTER_MOTION_HINT_MASK)

        self._pictures = OrderedDict()
        self._width = 450
        self._height = 200
        self.set_size_request(self._width, self._height)

        self._yawFov = None
        self._pitchFov = None
        self._yawCameraFov = None
        self._pitchCameraFov = None
        self._scale = None
        self._yawHead = None
        self._pitchHead = None

        self.gc = {}

    # Callbacks
    def _configure_cb(self, widget, event):
        """ Called when the drawing area changes size.

        This callback is also the first called when creating the widget.
        """
        #print "ShootingArea._configure_cb()"
        if not self.gc:

            # Shooting area GC
            for key in ('background', 'axis', 'head', 'border', 'border-next', 'preview',
                        'skip', 'ok', 'ok-reshoot', 'error', 'error-reshoot'):
                self.gc[key] = gtk.gdk.GC(self.window)
                schemeName = ConfigManager().get('Preferences', 'SHOOTING_AREA_COLOR_SCHEME')
                colorStr = config.SHOOTING_COLOR_SCHEME[schemeName][key]
                self.gc[key].set_rgb_fg_color(gtk.gdk.color_parse(colorStr))

        x, y, self._width, self._height = widget.get_allocation()
        self._compute_scale()
        #print "ShootingArea._configure_cb(): _width=%.1f, _height=%.1f" % (self._width, self._height)

        return True

    def _expose_cb(self, widget, event):
        """ Called when the drawing area is exposed.

        This is where to implement all drawing stuff.
        """
        raise NotImplementedError

    # Helpers
    def _compute_scale(self):
        """ Compute drawing scale
        """
        yawScale = self._width / self._yawFov
        pitchScale = self._height / self._pitchFov
        self._scale = min(yawScale, pitchScale)
        #print "ShootingArea._compute_scale(): yawScale=%f, pitchScale=%f, scale=%f" % (yawScale, pitchScale, scale)

    def _compute_image_coordinates(self, yaw, pitch):
        """
        """
        raise NotImplementedError

    def _compute_head_coordinates(self, yaw, pitch):
        """
        """
        raise NotImplementedError

    def _change_images_status(self, index):
        """ Set the status of image.

        @param index: index of next image to shoot
        @type index: int
        """
        for i, image in enumerate(self._pictures.itervalues()):
            if i + 1 == index:
                image.next = True
            else:
                image.next = False
            if i + 1 < index:
                if image.status == 'ok-reshoot':
                    image.status = 'ok'
                elif image.status == 'error-reshoot':
                    image.status = 'error'
                elif image.status == 'preview':
                    image.status = 'skip'
            else:
                if image.status == 'ok':
                    image.status = 'ok-reshoot'
                elif image.status == 'error':
                    image.status = 'error-reshoot'
                elif image.status == 'skip':
                    image.status = 'preview'

        self.refresh()

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
        self._pictures.clear()
        self._yawFov = yawFov
        self._pitchFov = pitchFov
        self._yawCameraFov = yawCameraFov
        self._pitchCameraFov = pitchCameraFov
        #print "ShootingArea.init(): yawFov=%.1f, pitchFov=%.1f, yawCameraFov=%.1f, pitchCameraFov=%.1f" % (yawFov, pitchFov, yawCameraFov, pitchCameraFov)

        self.connect("configure-event", self._configure_cb)
        self.connect("expose-event", self._expose_cb)

    def refresh(self):
        """ Refresh the shooting area
        """
        #print "ShootingArea.refresh()"
        self.queue_draw_area(0, 0, self._width, self._height)

    def add_pict(self, yaw, pitch, status=None, next=False):
        """ Add a pict at yaw/pitch coordinates.

        @param yaw: yaw pict position (°)
        @type yaw: float

        @param pitch: pitch pict position (°)
        @type pitch: float

        @param status: status of the shooting at this position
        @type status: str

        @param next: if True, this picture is the next to shoot
        @type next: bool
        """
        #print "ShootingArea.add_pict()"
        raise NotImplementedError

    def clear(self):
        """ Clear the shooting area
        """
        #print "ShootingArea.clear()"
        for image in self._pictures.itervalues():
            image.status = 'preview'
            image.next = False
        self.refresh()

    def get_selected_image_index(self, x, y):
        """
        """
        keys = self._pictures.keys()
        keys.reverse()
        for i, key in enumerate(keys):
            index = len(self._pictures) - i
            image = self._pictures[key]

            # Click in image
            if image.isCoordsIn(x, y):
                #print "ShootingArea.get_selected_image(): index=%d, status=%s" % (index , image.status)
                self._change_images_status(index)

                return index

    def set_selected_image_index(self, index):
        """
        """
        self._change_images_status(index)

    def set_current_head_position(self, yaw, pitch):
        """ Set the current head position.
        """
        self._yawHead = yaw
        self._pitchHead = pitch


class MosaicArea(ShootingArea):
    """ GTK MosaicArea widget
    """
    def __init__(self):
        """ Init MosaicArea widget.
        """
        #print "MosaicArea.__init__()"
        ShootingArea.__init__(self)
        self.__yawOffset = None
        self.__pitchOffset = None
        self.__yawStart = None
        self.__yawEnd = None
        self.__pitchStart = None
        self.__pitchEnd = None
        self.__yawOverlap = None
        self.__pitchOverlap = None

    # Callbacks
    def _configure_cb(self, widget, event):
        #print "MosaicArea._configure_cb()"
        ShootingArea._configure_cb(self, widget, event)
        yawOffset = self.__yawOffset
        pitchOffset = self.__pitchOffset
        self._compute_offsets()
        if self.__yawOffset != yawOffset or self.__pitchOffset != pitchOffset:
            for image in self._pictures.itervalues():
                yaw = image.yaw
                pitch = image.pitch
                x, y, w, h = self._compute_image_coordinates(yaw, pitch)
                image.x = x
                image.y = y
                image.w = w
                image.h = h

        return True

    def _expose_cb(self, widget, event):
        #print "MosaicArea._expose_cb()"

        # Draw background
        self.window.draw_rectangle(self.gc['background'], True, 0, 0, self._width, self._height)

        # Draw picts
        for image in self._pictures.itervalues():
            image.draw()

        # Draw head position
        x, y, w, h = self._compute_head_coordinates(self._yawHead, self._pitchHead)
        self.window.draw_line(self.gc['head'], 0, y, self._width, y)
        self.window.draw_line(self.gc['head'], x, 0, x, self._height)

        return False

    # Helpers
    def _compute_offsets(self):
        """ Recompute drawing offset.
        """
        self.__yawOffset = (self._width - self._yawFov * self._scale) / 2.
        self.__pitchOffset = (self._height - self._pitchFov * self._scale) / 2.
        #print "MosaicArea._compute_offsets(): yawOffset=%f, pitchOffset=%f" % (self.__yawOffset, self.__pitchOffset)

    def _compute_image_coordinates(self, yaw, pitch):
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
        #print "MosaicImageArea._compute_image_coordinates(): x=%.1f, y=%.1f, w=%.1f, h=%.1f" % (x, y, w, h)

        return x, y, w, h

    def _compute_head_coordinates(self, yaw, pitch):
        if cmp(self.__yawEnd, self.__yawStart) > 0:
            yaw = self._yawHead - self.__yawStart
        else:
            yaw = self._yawHead - self.__yawEnd
        if cmp(self.__pitchEnd, self.__pitchStart) > 0:
            pitch = self._pitchHead - self.__pitchStart
        else:
            pitch = self._pitchHead - self.__pitchEnd
        x = int(round((yaw + self._yawCameraFov / 2.) * self._scale + self.__yawOffset))
        y = int(round((pitch + self._pitchCameraFov / 2.) * self._scale + self.__pitchOffset))
        w = 2
        h = 2
        y = self._height - y - h
        #print "MosaicImageArea._compute_head_coordinates(): x=%.1f, y=%.1f, w=%.1f, h=%.1f" % (x, y, w, h)

        return x, y, w, h

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
        self.__yawStart = yawStart
        self.__yawEnd = yawEnd
        self.__pitchStart = pitchStart
        self.__pitchEnd = pitchEnd
        self.__yawOverlap = yawOverlap
        self.__pitchOverlap = pitchOverlap

    def add_pict(self, yaw, pitch, status=None, next=False):
        #print "MosaicArea.add_pict(%.1f, %.1f, status=%s, next=%s)" % (yaw, pitch, status, next)

        # Check if image already in list
        try:
            image = self._pictures["%.1f, %.1f" % (yaw, pitch)]
            if status is not None:
                image.status = status
            image.next = next

        except KeyError:
            x, y, h, w = None, None, None, None
            image = MosaicImageArea(self, yaw, pitch, x, y, w, h, status)
            self._pictures["%.1f, %.1f" % (yaw, pitch)] = image


class PresetArea(ShootingArea):
    """ GTK PresetArea widget
    """
    def __init__(self):
        ShootingArea.__init__(self)
        self.__yawMargin = None
        self.__pitchMargin = None

    # Callbacks
    def _configure_cb(self, widget, event):
        #print "PresetArea._configure_cb()"
        ShootingArea._configure_cb(self, widget, event)
        yawMargin = self.__yawMargin
        pitchMargin = self.__pitchMargin
        self._compute_margins()
        if self.__yawMargin != yawMargin or self.__pitchMargin != pitchMargin:
            for image in self._pictures.itervalues():
                yaw = image.yaw
                pitch = image.pitch
                x, y, w, h = self._compute_image_coordinates(yaw, pitch)
                image.x = x
                image.y = y
                image.w = w
                image.h = h

        return True

    def _expose_cb(self, widget, event):

        # Draw background
        self.window.draw_rectangle(self.gc['background'], True, 0, 0, self._width, self._height)

        # Draw 360°x180° area and axis
        xFull = int(round(self._width / 2. - 180 * self._scale))
        yFull = int(round(self._height / 2. - 90 * self._scale))
        wFull = int(round(360 * self._scale)) - 1
        hFull = int(round(180 * self._scale)) - 1
        ##print "xFull=%.1f, yFull=%.1f, wFull=%.1f, hFull=%.1f" % (xFull, yFull, wFull, hFull)
        self.window.draw_rectangle(self.gc['axis'], False, xFull, yFull, wFull, hFull)
        x1 = 0
        y1 = int(round(self._height / 2.)) + 1
        x2 = self._width
        y2 = y1
        self.window.draw_line(self.gc['axis'], x1, y1, x2, y2)
        x1 = self.__yawMargin
        y1 = 0
        x2 = x1
        y2 = self._height
        self.window.draw_line(self.gc['axis'], x1, y1, x2, y2)

        # Draw picts
        for image in self._pictures.itervalues():
            image.draw()

        # Draw head position
        x, y, w, h = self._compute_head_coordinates(self._yawHead, self._pitchHead)
        self.window.draw_line(self.gc['head'], 0, y, self._width, y)
        self.window.draw_line(self.gc['head'], x, 0, x, self._height)

        return False

    # Helpers
    def _compute_margins(self):
        """ Recompute drawing margins.
        """
        self.__yawMargin = int(round((self._width - 360. * self._scale) / 2.))
        self.__pitchMargin = int(round((self._height - 180. * self._scale) / 2.))
        #print "PresetArea._compute_margins(): yawMargin=%d, pitchMargin=%d" % (self.__yawMargin, self.__pitchMargin)

    def _compute_image_coordinates(self, yaw, pitch):
        """
        @todo: move to ImageArea
        """
        pitch = 180 / 2. - pitch
        x = int(round(yaw * self._scale - self._yawCameraFov * self._scale / 2.)) + self.__yawMargin
        y = int(round(pitch * self._scale - self._pitchCameraFov * self._scale / 2.)) + self.__pitchMargin
        w = int(round(self._yawCameraFov * self._scale))
        h = int(round(self._pitchCameraFov * self._scale))
        #print "PresetImageArea._compute_image_coordinates(): x=%.1f, y=%.1f, w=%.1f, h=%.1f" % (x, y, w, h)

        return x, y, w, h

    def _compute_head_coordinates(self, yaw, pitch):
        pitch = 180 / 2. - pitch
        x = int(round(yaw * self._scale)) + self.__yawMargin
        y = int(round(pitch * self._scale)) + self.__pitchMargin
        w = 2
        h = 2
        #print "PresetImageArea._compute_head_coordinates(): x=%.1f, y=%.1f, w=%.1f, h=%.1f" % (x, y, w, h)

        return x, y, w, h

    # Interface
    def init(self, yawFov, pitchFov, yawCameraFov, pitchCameraFov):
        ShootingArea.init(self, yawFov, pitchFov, yawCameraFov, pitchCameraFov)

    def add_pict(self, yaw, pitch, status=None, next=False):
        #print "PresetArea.add_pict(%.1f, %.1f, status=%s, next=%s)" % (yaw, pitch, status, next)

        # Check if image already in list
        try:
            image = self._pictures["%.1f, %.1f" % (yaw, pitch)]
            if status is not None:
                image.status = status
            image.next = next

        except KeyError:
            x, y, w, h = None, None, None, None
            image = PresetImageArea(self, yaw, pitch, x, y, w, h, status)
            self._pictures["%.1f, %.1f" % (yaw, pitch)] = image

        self.refresh()
