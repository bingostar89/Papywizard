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
    def __init__(self, yaw, pitch, yawCameraFov, pitchCameraFov):
        """ Init Picture widget.
        
        @param yaw: yaw position (°)
        @type yaw: float
        
        @param pitch: pitch position (°)
        @type pitch: float
        
        @param yawCameraFov: yaw camera fov (°)
        @type yawCameraFov: float
        
        @param pitchCameraFov: pitch camera fov (°)
        @type pitchCameraFov: float
        """
        self.yaw = yaw
        self.pitch = pitch
        

class ShootingArea(gtk.DrawingArea):
    """ GTK ShootingArea widget
    """
    def __init__(self, yawStart, yawEnd, pitchStart, pitchEnd, yawFov, pitchFov, yawCameraFov, pitchCameraFov, yawOverlap, pitchOverlap, yawNbPicts, pitchNbPicts):
        """ Init ShootingArea widget.
        
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
        
        @param yawNbPicts: yaw number of picts
        @type yawNbPicts: int
        
        @param pitchNbPicts: pitch number of picts
        @type pitchNbPicts: int
        
        @todo: give rawStart/End instead of yaw...
        """
        gtk.DrawingArea.__init__(self)
        
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
        self._yawNbPicts = yawNbPicts
        self._pitchNbPicts = pitchNbPicts
        
        self._picts = []
        self._yawInc = yawCameraFov * (1 - yawOverlap)
        self._yawInc *= cmp(yawEnd, yawStart)
        self._pitchInc = pitchCameraFov * (1 - pitchOverlap)
        self._pitchInc *= cmp(pitchEnd, pitchStart)
        print "yawInc=%.1f, pitchInc=%.1f" % (self._yawInc, self._pitchInc)
        
        self._border = 20
        self._yawScale = 2.
        self._pitchScale = 2.
        self._width = int(self._yawFov * self._yawScale)
        self._height = int(self._pitchFov * self._pitchScale)
        self.set_size_request(self._width + 2 * self._border, self._height + 2 * self._border)

        self.connect("realize", self._realize_cb)
        self.connect("configure-event", self._configure_cb)
        self.connect("expose-event", self._expose_cb)

    # Callbacks
    def _realize_cb(self, widget):
        """ The widget is realized.
        
        This callback is called only once, at widget creation,
        right after the _configure_cb callback.
        """
        #print "_realize_cb()"
        self._set_colors({'back': "#d0d0d0", 'fg1': "#000000", 'fg2': "#80ff80"})

    def _configure_cb(self, widget, event):
        """ Called when the drawing area changes size.
        
        This callback is also the first called when creating the widget.
        We create (or re-create) the pixmap with correct size.
        Note that the 
        """
        #print "_configure_cb()"
        x, y, self._width, self._height = widget.get_allocation()
        self._yawScale = (self._width - 2 * self._border) / self._yawFov
        self._pitchScale = (self._height - 2 * self._border) / self._pitchFov
        return True
        
    def _expose_cb(self, widget, event):
        """ Called when the drawing area is exposed.
        
        We copy the pixmap to the drawing area.
        """
        #print "_expose_cb()"
        self.window.draw_rectangle(self._back, True, self._border, self._border, self._width - 2 * self._border, self._height - 2 * self._border)
        for yawIndex, pitchIndex in self._picts:
            yaw = self._yawCameraFov / 2. + yawIndex * self._yawInc * self._yawScale
            pitch = self._pitchCameraFov / 2. + pitchIndex * self._pitchInc * (self._height - 2 * self._border) / self._pitchFov
            self.window.draw_rectangle(self._fg1, True, int((yaw - self._yawCameraFov / 2) + self._border),
                                                        int((pitch - self._pitchCameraFov / 2) + self._border),
                                                        int(self._yawCameraFov * self._yawScale),
                                                        int(self._pitchCameraFov * self._pitchScale))
            self.window.draw_rectangle(self._fg2, True, int((yaw - self._yawCameraFov / 2) + self._border + 1),
                                                        int((pitch - self._pitchCameraFov / 2) + self._border + 1),
                                                        int(self._yawCameraFov * self._yawScale - 2),
                                                        int(self._pitchCameraFov * self._pitchScale - 2))
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


def main():
    import time
    
    def on_button_clicked(widget):
        print "on_button_go()"
        global stop
        goButton.set_sensitive(False)
        stop = False
        shootingArea.clear()
        
        for pitchIndex in xrange(shootingArea._pitchNbPicts):
            for yawIndex in xrange(shootingArea._yawNbPicts):
                shootingArea.add_pict(yawIndex, pitchIndex)
                
                t = time.time()
                while time.time() - t < 0.2:
                    if gtk.events_pending():
                        gtk.main_iteration()
                    else:
                        time.sleep(0.01)
                if stop:
                    break
            if stop:
                break
        goButton.set_sensitive(True)

    def on_button_stop(widget):
        print "on_button_stop()"
        global stop
        stop = True
        
    stop = None
    
    yawCameraFov = 30.
    pitchCameraFov = 20.
    overlap = 0.25

    # 360°x180°
    #yawStart = -180. + yawCameraFov * (1 - overlap) / 2.
    #yawEnd = 180. - yawCameraFov * (1 - overlap) / 2.
    #pitchStart = -90. + pitchCameraFov * (1 - overlap) / 2.
    #pitchEnd = 90. - pitchCameraFov * (1 - overlap) / 2.

    # Any start/end
    yawStart = -100.
    yawEnd = 75.
    pitchStart = -55.
    pitchEnd = 10.
    
    yawFov = abs(yawEnd - yawStart) + yawCameraFov
    pitchFov = abs(pitchEnd - pitchStart) + pitchCameraFov
    yawNbPicts = int(((yawFov - overlap * yawCameraFov) / (yawCameraFov * (1 - overlap))) + 1)
    pitchNbPicts = int(((pitchFov - overlap * pitchCameraFov) / (pitchCameraFov * (1 - overlap))) + 1)
    if yawNbPicts > 1:
        yawOverlap = (yawNbPicts * yawCameraFov - yawFov) / (yawCameraFov * (yawNbPicts - 1))
    else:
        yawOverlap = 1.
    if pitchNbPicts > 1:
        pitchOverlap = (pitchNbPicts * pitchCameraFov - pitchFov) / (pitchCameraFov * (pitchNbPicts - 1))
    else:
        pitchOverlap = 1.

    print "yawStart=%.1f, yawEnd=%.1f, yawFov=%.1f, yawCameraFov=%.1f, yawNbPicts=%d, yawOverlap=%.2f" % (yawStart, yawEnd, yawFov, yawCameraFov, yawNbPicts, yawOverlap)
    print "pitchStart=%.1f, pitchEnd=%.1f, pitchFov=%.1f, pitchCameraFov=%.1f, pitchNbPicts=%d, pitchOverlap=%.2f" % (pitchStart, pitchEnd, pitchFov, pitchCameraFov, pitchNbPicts, pitchOverlap)

    window = gtk.Window()
    vbox = gtk.VBox()
    window.add(vbox)
    shootingArea = ShootingArea(yawStart, yawEnd, pitchStart, pitchEnd, yawFov, pitchFov, yawCameraFov, pitchCameraFov, yawOverlap, pitchOverlap, yawNbPicts, pitchNbPicts)
    vbox.add(shootingArea)
    hbox = gtk.HBox()
    vbox.add(hbox)
    goButton = gtk.Button("Go")
    goButton.connect("clicked", on_button_clicked)
    hbox.add(goButton)
    stopButton = gtk.Button("Stop")
    stopButton.connect("clicked", on_button_stop)
    hbox.add(stopButton)
    window.connect("destroy", gtk.main_quit)
    window.show_all()
    gtk.main()


if __name__ == "__main__":
    main()