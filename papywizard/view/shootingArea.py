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

@author: Frédéric Mantegazza
@copyright: (C) 2007-2008 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id: shooting.py 327 2008-06-25 14:29:36Z fma $"

import pygtk
pygtk.require("2.0")
import gtk

        
class ShootingArea(gtk.DrawingArea):
    """ GTK ShootingArea widget
    """
    def __init__(self):
        """ Init ShootingArea widget.
        """
        gtk.DrawingArea.__init__(self)

        self._picts = []
        self._width = 300
        self._height = 150
        self.set_size_request(self._width, self._height)
        
        self._yawFov = None
        self._pitchFov = None
        self._yawCameraFov = None
        self._pitchCameraFov = None
        self._yawScale = None
        self._pitchScale = None
        self._yawOffset = None
        self._pitchOffset = None
        
    def init(self, yawFov, pitchFov, yawCameraFov, pitchCameraFov):
        """ Init internal values.

        @param yawFov: yaw fov (�)
        @type yawFov: float
        
        @param pitchFov: pitch fov (�)
        @type pitchFov: float
        
        @param yawCameraFov: pict yaw fov (�)
        @type yawCameraFov: float
        
        @param pitchCameraFov: pict pitch fov (�)
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
        self._yawOffset = (self._width - self._yawFov * self._scale) / 2.
        self._pitchOffset = (self._height - self._pitchFov * self._scale) / 2.
        #print "yawScale=%f, pitchScale=%f, scale=%f, yawOffset=%f, pitchOffset=%f" % (yawScale, pitchScale, self._scale, self._yawOffset, self._pitchOffset)
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

    def add_pict(self, yawIndex, pitchIndex):
        """ Add a pict at yaw/pitch coordinates.
        
        @param yawIndex: pict yaw position index
        @type yawIndex: int
        
        @param pitchIndex: pict pitch position index
        @type pitchIndex: int
        """
        #print "add_pict(yawIndex=%d, pitchIndex=%d)" % (yawIndex, pitchIndex)
        self._picts.append((yawIndex, pitchIndex))
        self.refresh()

    def clear(self):
        """ Clear the shooting area
        """
        #print "clear()"
        self._picts = []
        self.refresh()

    def _set_colors(self, colors):
        #print "set_colors()"
        for widget, color in colors.iteritems():
            exec "self._%s = gtk.gdk.GC(self.window)" % widget
            exec "self._%s.set_rgb_fg_color(gtk.gdk.color_parse('%s'))" % (widget, color)

