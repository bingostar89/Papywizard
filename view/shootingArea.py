# -*- coding: iso-8859-1 -*-

""" Panohead remote control.

License
=======

 - B{papywizard} (U{http://trac.gbiloba.org/papywizard}) is Copyright:
  - (C) 2007-2008 Fr�d�ric Mantegazza

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

@author: Fr�d�ric Mantegazza
@copyright: (C) 2007-2008 Fr�d�ric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id: shooting.py 327 2008-06-25 14:29:36Z fma $"

#import pygtk
#pygtk.require("2.0")
import gtk

        
class ShootingArea(gtk.DrawingArea):
    """ GTK ShootingArea widget
    """
    def __init__(self):
        """ Init ShootingArea widget.
        """
        gtk.DrawingArea.__init__(self)

        self._picts = []
        self._border = 0
        x, y, self._width, self._height = self.get_allocation()

        self._yawStart = None
        self._yawEnd = None
        self._pitchStart = None
        self._pitchEnd = None
        self._yawFov = None
        self._pitchFov = None
        self._yawCameraFov = None
        self._pitchCameraFov = None
        self._yawOverlap = None
        self._pitchOverlap = None
        self._yawSens = None
        self._pitchSens = None
        self._yawScale = None
        self._pitchScale = None
        
    def init(self, yawStart, yawEnd, pitchStart, pitchEnd, yawFov, pitchFov, yawCameraFov, pitchCameraFov, yawOverlap, pitchOverlap):
        """ Init internal values.
        
        @param yawStart: yaw start position (�)
        @type yawStart: float
        
        @param yawEnd: yaw end position (�)
        @type yawEnd: float
        
        @param pitchStart: pitch start position (�)
        @type pitchStart: float
        
        @param pitchEnd: pitch end position (�)
        @type pitchEnd: float
        
        @param yawFov: yaw fov (�)
        @type yawFov: float
        
        @param pitchFov: pitch fov (�)
        @type pitchFov: float
        
        @param yawCameraFov: pict yaw fov (�)
        @type yawCameraFov: float
        
        @param pitchCameraFov: pict pitch fov (�)
        @type pitchCameraFov: float
        
        @param yawOverlap: yaw real overlap (ratio)
        @type yawOverlap: float
        
        @param pitchOverlap: pitch overlap (ratio)
        @type pitchOverlap: float
        """
        Logger().trace("ShootingArea.init()")
        self._yawStart = yawStart
        self._yawEnd = yawEnd
        self._pitchStart = pitchStart
        self._pitchEnd = pitchEnd
        self._yawFov = yawFov
        self._pitchFov = pitchFov
        self._yawCameraFov = yawCameraFov
        self._pitchCameraFov = pitchCameraFov
        self._yawOverlap = yawOverlap
        self._pitchOverlap = pitchOverlap
        self._yawSens = cmp(yawEnd, yawStart)
        self._pitchSens = cmp(pitchEnd, pitchStart)
        self._yawScale = self._width / self._yawFov
        self._pitchScale = self._height / self._pitchFov

        self.connect("realize", self._realize_cb)
        self.connect("configure-event", self._configure_cb)
        self.connect("expose-event", self._expose_cb)

    # Callbacks
    def _realize_cb(self, widget):
        """ The widget is realized.
        
        This callback is called only once, at widget creation,
        right after the _configure_cb callback.
        """
        self._set_colors({'back': "#d0d0d0", 'fg1': "#000000", 'fg2': "#80ff80"})

    def _configure_cb(self, widget, event):
        """ Called when the drawing area changes size.
        
        This callback is also the first called when creating the widget.
        We create (or re-create) the pixmap with correct size.
        Note that the 
        """
        self._set_colors({'back': "#d0d0d0", 'fg1': "#000000", 'fg2': "#80ff80"})
        x, y, self._width, self._height = widget.get_allocation()
        self._yawScale = (self._width - 2 * self._border) / self._yawFov
        self._pitchScale = (self._height - 2 * self._border) / self._pitchFov
        return True
        
    def _expose_cb(self, widget, event):
        """ Called when the drawing area is exposed.
        
        We copy the pixmap to the drawing area.
        """
        self.window.draw_rectangle(self._back, True, self._border, self._border, self._width - 2 * self._border, self._height - 2 * self._border)
        for yaw, pitch in self._picts:
            if self._yawSens > 0:
                yaw -= self._yawStart
            else:
                yaw -= self._yawEnd
            if self._pitchSens > 0:
                pitch -= self._pitchStart
            else:
                pitch -= self._pitchEnd
            x = int(yaw * self._yawScale) + self._border
            y = int(pitch * self._pitchScale) + self._border
            w = int(self._yawCameraFov * self._yawScale)
            h = int(self._pitchCameraFov * self._pitchScale)
            #print "yaw=%.1f, pitch=%.1f, x=%.1f, y=%.1f, w=%.1f, h=%.1f" % (yaw, pitch, x, y, w, h)
            self.window.draw_rectangle(self._fg1, True, x, y, w, h)
            x += 1
            y += 1
            w -= 2
            h -= 2
            self.window.draw_rectangle(self._fg2, True, x, y, w, h)
        return False

    def refresh(self):
        """ Refresh the LCD widget
        """
        #print "refresh()"
        self.queue_draw_area(0, 0, self._width, self._height)

    def add_pict(self, yawIndex, pitchIndex):
        """ Add a pict at yaw/pitch coordinates.
        
        @param yaw: pict yaw position index
        @type yaw: int
        
        @param pitch: pict pitch position index
        @type pitc: int
        """
        #print "add_pict(yawIndex=%d, pitchIndex=%d)" % (yawIndex, pitchIndex)
        self._picts.append((yawIndex, pitchIndex))
        self.refresh()

    def clear(self):
        #print "clear()"
        """ Clear the LCD display
        """
        self._picts = []
        self.window.draw_rectangle(self._back, True, self._border, self._border, self._width - 2 * self._border, self._height - 2 * self._border)

    def _set_colors(self, colors):
        #print "set_colors()"
        for widget, color in colors.iteritems():
            exec "self._%s = gtk.gdk.GC(self.window)" % widget
            exec "self._%s.set_rgb_fg_color(gtk.gdk.color_parse('%s'))" % (widget, color)

