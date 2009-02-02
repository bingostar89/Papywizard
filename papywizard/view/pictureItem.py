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
- CrosshairCusrsor

@author: Frédéric Mantegazza
@copyright: (C) 2007-2009 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id: imageArea.py 1308 2009-01-11 16:19:42Z fma $"

from PyQt4 import QtCore, QtGui

from papywizard.common import config
from papywizard.common.loggingServices import Logger

BORDER_WIDTH = 3


class AbstractPictureItem(QtGui.QGraphicsItem):
    """ Abstract picture item.
    """
    def __init__(self, yaw, pitch ,yawFov, pitchFov, parent=None):
        """  Init the abstract picture item.

        @param scene: scene owning this picture
        @type scene: L{QGraphicsScene<QtGui>}

        @param x: x coordinate of the picture
        @type x: int

        @param y: y coordinate of the picture
        @type y: int

        @param w: width of the picture
        @type w: int

        @param h: height of the picture
        @type h: int
        """
        QtGui.QGraphicsItem.__init__(self, parent)
        self.setPos(yaw, pitch)
        self._yawFov = yawFov
        self._pitchFov = pitchFov
        self._index = None
        self._state = None
        self._nextIndex = 0 # 0 is not a valid index

    # Helpers
    def _computeBorderWidth(self):
        """ Compute picture border width.

        Compute the width of the border to use in paint() and boundingRect()
        methods so the size on screen is constant, whatever the view size is.
        """
        xRatio = self.scene().views()[0].width() / self.scene().width()
        yRatio = self.scene().views()[0].height() / self.scene().height()
        return BORDER_WIDTH / min(xRatio, yRatio)

    def _computeColors(self):
        """ Compute colors according to state.

        Also check if the current picture is before or after the next to shoot.

        @return: inner and border colors
        @rtype: tuple of int
        """
        if self._index < self._nextIndex:
            innerColor = config.SHOOTING_COLOR_SCHEME['default'][self._state]
        else:
            innerColor = config.SHOOTING_COLOR_SCHEME['default']["%s-toshoot" % self._state]
        if self._index == self._nextIndex:
            borderColor = config.SHOOTING_COLOR_SCHEME['default']['border-next']
        else:
            borderColor = config.SHOOTING_COLOR_SCHEME['default']['border']

        return innerColor, borderColor

    def _computeRect(self):
        """ Compute the rectangle coordinates.
        """
        x = -self._yawFov / 2
        y = -self._pitchFov / 2
        w = self._yawFov
        h = self._pitchFov
        return x, y, w, h

    # Qt overloaded methods
    def boundingRect(self):
        x, y, w, h = self._computeRect()
        return QtCore.QRectF(x - self._computeBorderWidth() / 2, y - self._computeBorderWidth() / 2,
                             w + self._computeBorderWidth(), h + self._computeBorderWidth())

    # Interface
    def setIndex(self, index):
        """ Set the index of the current picture.

        @param index: index of the current picture
        @type index: int
        """
        self.setZValue(index)
        self._index = index

    def getIndex(self):
        """ Return the index of the picture in the shooting sequence.
        """
        return self._index

    def setState(self, state):
        """ Set the current state of the picture.

        @param state: state of the picture, in ('preview', 'ok', 'error')
        @type state: str
        """
        self._state = state

    def setNextIndex(self, index):
        """ Give the index of the next picture to shoot.

        @param index: index of the next picture to shoot
        @type index: int
        """
        self._nextIndex = index


class MosaicPictureItem(AbstractPictureItem):
    """ Picture item implementation for mosaic.
    """

    # Qt overloaded methods
    def paint(self, painter, options, widget):
        x, y, w, h = self._computeRect()
        innerColor, borderColor = self._computeColors()
        painter.fillRect(x, y, w, h, QtGui.QColor(*innerColor))
        #painter.setPen(QtGui.QPen(QtGui.QBrush(QtGui.QColor(*borderColor)), self._computeBorderWidth()))
        painter.setPen(QtGui.QPen(QtGui.QBrush(QtGui.QColor(*config.SHOOTING_COLOR_SCHEME['default']['border'])), self._computeBorderWidth()))
        painter.drawRect(x, y, w, h)


class PresetPictureItem(AbstractPictureItem):
    """ Picture item implementation for preset.
    """

    # Qt overloaded methods
    def boundingRegion(self, itemToDeviceTransform):
        x, y, w, h = self._computeRect()
        return QtCore.QRegion(x - self._computeBorderWidth() / 2, y - self._computeBorderWidth() / 2,
                              w + self._computeBorderWidth(), h + self._computeBorderWidth(),
                              QtGui.QRegion.Ellipse)

    def shape(self):
        path = QtGui.QPainterPath()
        path.addEllipse(self.boundingRect())
        return path

    def paint(self, painter, options, widget):
        x, y, w, h = self._computeRect()
        innerColor, borderColor = self._computeColors()
        path = QtGui.QPainterPath()
        path.addEllipse(x, y, w, h)
        painter.fillPath(path, QtGui.QColor(*innerColor))
        #painter.setPen(QtGui.QPen(QtGui.QBrush(QtGui.QColor(*borderColor)), self._computeBorderWidth()))
        painter.setPen(QtGui.QPen(QtGui.QBrush(QtGui.QColor(*config.SHOOTING_COLOR_SCHEME['default']['border'])), self._computeBorderWidth()))
        painter.drawEllipse(x, y, w, h)


class CrosshairCusrsor(QtGui.QGraphicsItemGroup):
    """ Crosshair cursor item for head and next picture to shoot.

    @todo: use view sqrt(width ** 2 + height ** 2) has limits.
    """
    def __init__(self, parent=None):
        QtGui.QGraphicsItemGroup .__init__(self, parent)
        self._yawLine = QtGui.QGraphicsLineItem()
        self._yawLine.setLine(0, -1000, 0, 1000)
        self.addToGroup(self._yawLine)
        self._pitchLine = QtGui.QGraphicsLineItem()
        self._pitchLine.setLine(-1000, 0, 1000, 0)
        self.addToGroup(self._pitchLine)

    # Qt overloaded methods
    def shape(self):
        """ Return the shape of the crosshair.

        We return an empty shape, so the crosshair is not detected in the
        scene mousePressEvent() callback, using event.itemAt() method.
        """
        path = QtGui.QPainterPath()
        return path

    # Interface
    def setPen(self, pen):
        """ Set the pen of the crosshair.

        We simulate this method, and call all sub-items one.
        """
        self._yawLine.setPen(pen)
        self._pitchLine.setPen(pen)
