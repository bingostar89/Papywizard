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
CROSSHAIR_WIDTH = 3


class AbstractPictureItem(QtGui.QGraphicsItemGroup):
    """ Abstract picture item.
    """
    nextIndex = 0 # 0 is not a valid index

    def __init__(self, index, yawFov, pitchFov, parent=None):
        """  Init the abstract picture item.

        @param yawFov: yaw fov of the picture
        @type yawFov: float

        @param pitchFov: pitch fov of the picture
        @type pitchFov: float
        """
        QtGui.QGraphicsItemGroup.__init__(self, parent)
        self._index = index
        self.setZValue(index)
        self._yawFov = yawFov
        self._pitchFov = pitchFov
        self._state = 'preview'
        x, y, w, h = self._computeRect()
        self._item = self._createItem(x, y, w, h)
        self.addToGroup(self._item)

    def _createItem(self):
        """ Create the real item.
        """
        raise NotImplementedError("AbstractPictureItem._createItem() is abstract and must be overidden")

    # Helpers
    def _computeBorderWidth(self):
        """ Compute picture border width.

        Compute the width of the border to use in refresh() and boundingRect()
        methods so the size on screen is constant, whatever the view size is.

        What if there are several views?
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
        if self._index < AbstractPictureItem.nextIndex:
            innerColor = config.SHOOTING_COLOR_SCHEME['default'][self._state]
        elif self._index == AbstractPictureItem.nextIndex:
            innerColor = config.SHOOTING_COLOR_SCHEME['default']['%s-next' % self._state]
        else:
            innerColor = config.SHOOTING_COLOR_SCHEME['default']['%s-toshoot' % self._state]

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

    # Interface
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
        self.refresh()

    def refresh(self):
        """ Refresh the picture.
        """
        innerColor, borderColor = self._computeColors()
        self._item.setPen(QtGui.QPen(QtGui.QBrush(QtGui.QColor(*borderColor)), self._computeBorderWidth()))
        self._item.setBrush(QtGui.QBrush(QtGui.QColor(*innerColor))) #, QtCore.Qt.LinearGradientPattern))


class MosaicPictureItem(AbstractPictureItem):
    """ Picture item implementation for mosaic.
    """
    def _createItem(self, x, y, w, h):
        return QtGui.QGraphicsRectItem(x, y, w, h, self)


class PresetPictureItem(AbstractPictureItem):
    """ Picture item implementation for preset.
    """
    def _createItem(self, x, y, w, h):
        return QtGui.QGraphicsEllipseItem(x, y, w, h, self)

    def shape(self):
        path = QtGui.QPainterPath()
        path.addEllipse(self.boundingRect())
        return path


class CrosshairCusrsor(QtGui.QGraphicsItemGroup):
    """ Crosshair cursor item for head and next picture to shoot.

    @todo: use view sqrt(width ** 2 + height ** 2) as limits.
    """
    def __init__(self, size, parent=None):
        QtGui.QGraphicsItemGroup.__init__(self, parent)
        self._yawLine = QtGui.QGraphicsLineItem()
        self._yawLine.setLine(0, -size, 0, size)
        self._yawLine.setPen(QtGui.QColor(*config.SHOOTING_COLOR_SCHEME['default']['head']))
        self.addToGroup(self._yawLine)
        self._pitchLine = QtGui.QGraphicsLineItem()
        self._pitchLine.setLine(-size, 0, size, 0)
        self._pitchLine.setPen(QtGui.QColor(*config.SHOOTING_COLOR_SCHEME['default']['head']))
        self.addToGroup(self._pitchLine)
        self.rotate(45)

    # Helpers
    def _computeWidth(self):
        """ Compute width.

        Compute the width of the border to use in refresh() and boundingRect()
        methods so the size on screen is constant, whatever the view size is.

        What if there are several views?
        """
        xRatio = self.scene().views()[0].width() / self.scene().width()
        yRatio = self.scene().views()[0].height() / self.scene().height()
        return CROSSHAIR_WIDTH / min(xRatio, yRatio)

    # Qt overloaded methods
    def shape(self):
        """ Return the shape of the crosshair.

        We return an empty shape, so the crosshair is not detected in the
        scene mousePressEvent() callback, using event.itemAt() method.
        """
        path = QtGui.QPainterPath()
        return path

    def boundingRegion(self, itemToDeviceTransform):
        """ Return the region of the crosshair.
        """
        return QtGui.QRegion()

    # Interface
    def refresh(self):
        """ Refresh the crosshair.
        """
        self._yawLine.setPen(QtGui.QPen(self._yawLine.pen().brush(), self._computeWidth()))
        self._pitchLine.setPen(QtGui.QPen(self._pitchLine.pen().brush(), self._computeWidth()))
