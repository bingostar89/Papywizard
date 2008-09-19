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

- PresetArea

@author: Frédéric Mantegazza
@copyright: (C) 2007-2008 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id: shooting.py 327 2008-06-25 14:29:36Z fma $"

import pygtk
pygtk.require("2.0")
import gtk

from papywizard.view.shootingArea import ShootingArea


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
        for i, (yaw, pitch) in enumerate(self._picts):
            pitch = 180 / 2. - pitch
            x = int(round(yaw * self._scale - self._yawCameraFov * self._scale / 2.)) + self.__yawMargin
            y = int(round(pitch * self._scale - self._pitchCameraFov * self._scale / 2.)) + self.__pitchMargin
            w = int(round(self._yawCameraFov * self._scale))
            h = int(round(self._pitchCameraFov * self._scale))
            #print "pict=%d, yaw=%.1f, pitch=%.1f, x=%.1f, y=%.1f, w=%.1f, h=%.1f" % (i + 1, yaw, pitch, x, y, w, h)
            #self.window.draw_rectangle(self._fg1, True, x, y, w, h)
            self.window.draw_arc(self._fg1, True, x, y, w, h, 0, 360 * 64)
            x += 1
            y += 1
            w -= 2
            h -= 2
            #self.window.draw_rectangle(self._fg2, True, x, y, w, h)
            self.window.draw_arc(self._fg2, True, x, y, w, h, 0, 360 * 64)

        return False
