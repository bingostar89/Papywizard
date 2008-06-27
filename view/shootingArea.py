# -*- coding: iso-8859-1 -*-

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

import time

import gtk


class Picture(object):
    """ GTK Picture widget.
    """
    def __init__(self, yaw, pitch, pictYawFov, pictPitchFov):
        """ Init Picture widget.
        
        @param yaw: yaw position (°)
        @type yaw: float
        
        @param pitch: pitch position (°)
        @type pitch: float
        
        @param pictYawFov: yaw fov (°)
        @type pictYawFov: float
        
        @param pictPitchFov: pitch fov (°)
        @type pictPitchFov: float
        """
        self.yaw = yaw
        self.pitch = pitch
        
        

class ShootingArea(gtk.DrawingArea):
    """ GTK ShootingArea widget
    """
    def __init__(self, yawFov, pitchFov, pictYawFov, pictPitchFov):
        """ Init ShootingArea widget.
        
        @param yawFov: total yaw fov (°)
        @type yawFov: float
        
        @param pitchFov: total pitch fov (°)
        @type pitchFov: float
        
        @param pictYawFov: pict yaw fov (°)
        @type pictYawFov: float
        
        @param pictPitchFov: pict pitch fov (°)
        @type pictPitchFov: float
        """
        gtk.DrawingArea.__init__(self)
        
        self._yawFov = yawFov
        self._pitchFov = pitchFov
        self._pictYawFov = pictYawFov
        self._pictPitchFov = pictPitchFov
        self._picts = []
        
        self._pixmap = None
        self._width = yawFov
        self._height = pitchFov
        self.set_size_request(self._width, self._height)

        self.connect("realize", self._realize_cb)
        self.connect("configure-event", self._configure_cb)
        self.connect("expose-event", self._expose_cb)

    # Callbacks
    def _realize_cb(self, widget):
        """ The widget is realized.
        
        This callback is called only once, at widget creation,
        right after the _configure_cb callback.
        """
        print "_realize_cb()"
        self._set_colors({'back': "#DCDAD5", 'fg1': "#000000", 'fg2': "#00ff00"})

    def _configure_cb(self, widget, event):
        """ Called when the drawing area changes size.
        
        This callback is also the first called when creating the widget.
        We create (or re-create) teh pixmap with correct size.
        Note that the 
        """
        print "_configure_cb()"
        x, y, self._width, self._height = widget.get_allocation()
        #self._pixmap = gtk.gdk.Pixmap(widget.window, self._width, self._height)
        return True
        
    def _expose_cb(self, widget, event):
        """ Called when the drawing area is exposed.
        
        We copy the pixmap to the drawing area.
        """
        print "_expose_cb()"
        #self._pixmap.draw_rectangle(self._back, True, 0, 0, self._width, self._height)
        self.window.draw_rectangle(self._back, True, 0, 0, self._width, self._height)
        for yaw, pitch in self._picts:
            #self._pixmap.draw_rectangle(self._fg1, False, yaw - self._pictYawFov / 2, pitch - self._pictPitchFov / 2, 
                                                          #self._pictYawFov, self._pictPitchFov)
            self.window.draw_rectangle(self._fg1, False, yaw - self._pictYawFov / 2, pitch - self._pictPitchFov / 2, 
                                                          self._pictYawFov, self._pictPitchFov)
        #widget.window.draw_drawable(self._back, self._pixmap, 0, 0, 0, 0, self._width, self._height)
        return False

    def refresh(self):
        """ Refresh the LCD widget
        """
        print "refresh()"
        self.queue_draw_area(0, 0, self._width, self._height)

    def add_pict(self, yaw, pitch):
        """ Add a pict at yaw/pitch coordinates.
        
        @param yaw: pict yaw position (°)
        @type yaw: float
        
        @param pitch: pict pitch position (°)
        @type pitc: float
        """
        print "add_pict()"
        self._picts.append((yaw, pitch))
        self.refresh()

    def clear(self):
        print "clear()"
        """ Clear the LCD display
        """
        #self._pixmap.draw_rectangle(self._back, True, 0, 0, self._width, self._height)
        self.window.draw_rectangle(self._back, True, 0, 0, self._width, self._height)
        #self.refresh()

    def _set_colors(self, colors):
        print "set_colors()"
        
        for widget, color in colors.iteritems():
            #exec "self._%s = gtk.gdk.GC(self._pixmap)" % widget
            exec "self._%s = gtk.gdk.GC(self.window)" % widget
            exec "self._%s.set_rgb_fg_color(gtk.gdk.color_parse('%s'))" % (widget, color)


def main():
    def on_button_clicked(self):
        shootingArea.add_pict(50, 50)
        
    def on_button_clear(self):
        shootingArea.clear()
        
    window = gtk.Window()
    vbox = gtk.VBox()
    window.add(vbox)
    shootingArea = ShootingArea(360, 180, 30, 20)
    vbox.add(shootingArea)
    hbox = gtk.HBox()
    vbox.add(hbox)
    TestButton = gtk.Button("Test")
    TestButton.connect("clicked", on_button_clicked)
    hbox.add(TestButton)
    ClearButton = gtk.Button("Clear")
    ClearButton.connect("clicked", on_button_clear)
    hbox.add(ClearButton)
    window.connect("destroy", gtk.main_quit)
    window.show_all()
    gtk.main()


if __name__ == "__main__":
    main()