# -*- coding: utf-8 -*-

""" Panohead remote control.

License
=======

 - B{papywizard} (U{http://trac.gbiloba.org/papywizard}) is Copyright:
  - (C) 2007-2009 Frédéric Mantegazza

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

- PictureItem
- MosaicPictureItem
- PresetPictureItem

@author: Frédéric Mantegazza
@copyright: (C) 2007-2009 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id: imageArea.py 1308 2009-01-11 16:19:42Z fma $"

from PyQt4 import QtCore, QtGui


class AbstractPictureItem(QtGui.QGraphicsRectItem):
    """ Abstract picture item.
    """
    def __init__(self, x, y, w, h, parent=None):
        """  Init the abstract picture item.

        @param x: x coordinate of the image
        @type x: int

        @param y: y coordinate of the image
        @type y: int

        @param w: width of the image
        @type w: int

        @param h: height of the image
        @type h: int
        """
        #print "PictureItem.__init__()"
        self._drawingArea = drawingArea
        self.yaw = yaw
        self.pitch = pitch
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.status = status
        self.next = next

    # Helpers

    # Interface
    def setPosition(self, index, yaw, pitch):
        """ Set the position of the picture.
        
        @param index: index in the shooting sequence
        @type index: int
        
        @param yaw: yaw of the image (°)
        @type yaw: float

        @param pitch: pitch of the image (°)
        @type pitch: float
        """
        pass

    def setState(self, status=None, next=False):
        """ Set the current state of the picture.

        @param status: status of the picture, in
                       ('ok', 'okReshoot', 'error', 'errorReshoot', 'preview', 'skip')
        @type status: str

        @param next: if True, this picture is the next to shoot
        @type next: bool
        """

    def draw(self):
        """ Draw itself on the drawable.
        """
        raise NotImplementedError

    def isCoordsIn(self, x, y):
        """ Check if given coords are in the pict. area.
        """
        raise NotImplementedError


class MosaicPictureItem(AbstractPictureItem):
    """ Picture item implementation for mosaic.
    """
    def draw(self):
        #print "MosaicPictureItem.draw()"

        # Border
        if self.next:
            gc = self._drawingArea.gc['border-next']
        else:
            gc = self._drawingArea.gc['border']
        self._drawingArea.window.draw_rectangle(gc, True, self.x, self.y, self.w, self.h)

        # Inside
        self._drawingArea.window.draw_rectangle(self._drawingArea.gc[self.status], True, self.x + 2, self.y + 2, self.w - 4, self.h - 4)

    def isCoordsIn(self, x, y):
        if self.x <= x <= (self.x + self.w) and \
           self.y <= y <= (self.y + self.h):
            return True
        else:
            return False


class PresetPictureItem(AbstractPictureItem):
    """ Picture item implementation for preset.
    """
    def draw(self):
        #print "PresetPictureItem.draw()"

        # Border
        if self.next:
            gc = self._drawingArea.gc['border-next']
        else:
            gc = self._drawingArea.gc['border']
        self._drawingArea.window.draw_arc(gc, True, self.x, self.y, self.w, self.h, 0, 360 * 64)

        # Inside
        self._drawingArea.window.draw_arc(self._drawingArea.gc[self.status], True, self.x + 2, self.y + 2, self.w - 4, self.h - 4, 0, 360 * 64)

    def isCoordsIn(self, x, y):
        """
        @todo: make circle detection instead of square
        """
        if self.x <= x <= (self.x + self.w) and \
           self.y <= y <= (self.y + self.h):
            return True
        else:
            return False
