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
        """ Init PresetArea widget.
        """
        ShootingArea.__init__(self)

    # Callbacks
    def _expose_cb(self, widget, event):

        # Draw background
        xBack = int(round(self._yawOffset))
        yBack = int(round(self._pitchOffset))
        wBack = self._width - int(round(2 * self._yawOffset))
        hBack = self._height - int(round(2 * self._pitchOffset))
        self.window.draw_rectangle(self._back, True, xBack, yBack, wBack, hBack)
        #print "xBack=%d, yBack=%d, wBack=%d, hBack=%d" % (xBack, yBack, wBack, hBack)
                                                
        # Draw picts
        for i, (yaw, pitch) in enumerate(self._picts):
            #if cmp(self._yawEnd, self._yawStart) > 0:
                #yaw -= self._yawStart
            #else:
                #yaw -= self._yawEnd
            #if cmp(self._pitchEnd, self._pitchStart) > 0:
                #pitch -= self._pitchStart
            #else:
                #pitch -= self._pitchEnd
            x = int(round(yaw * self._scale)) + int(round(self._yawOffset))
            y = int(round(pitch * self._scale)) + int(round(self._pitchOffset))
            w = int(round(self._yawCameraFov * self._scale))
            h = int(round(self._pitchCameraFov * self._scale))
            y = self._height - y - h
            #print "pict=%d, yaw=%.1f, pitch=%.1f, x=%.1f, y=%.1f, w=%.1f, h=%.1f" % (i + 1, yaw, pitch, x, y, w, h)
            self.window.draw_rectangle(self._fg1, True, x, y, w, h)
            x += 1
            y += 1
            w -= 2
            h -= 2
            self.window.draw_rectangle(self._fg2, True, x, y, w, h)
            
        # Draw 360°x180° area
        xFull = int(round(self._width / 2.)) - int(round(180 * self._scale))
        yFull = int(round(self._height / 2.)) - int(round(90 * self._scale))
        wFull = int(round(360 * self._scale)) - 1
        hFull = int(round(180 * self._scale)) - 1
        #print "xFull=%.1f, yFull=%.1f, wFull=%.1f, hFull=%.1f" % (xFull, yFull, wFull, hFull)
        self.window.draw_rectangle(self._fg3, False, xFull, yFull, wFull, hFull)
        
        return False
