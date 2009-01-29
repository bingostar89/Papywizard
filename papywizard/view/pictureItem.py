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

from papywizard.common import config

BORDER_WIDTH = 3


class AbstractPictureItem(QtGui.QGraphicsItem):
    """ Abstract picture item.
    """
    def __init__(self, x, y, w, h, parent=None):
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
        self._x = x
        self._y = y
        self._w = w
        self._h = h
        self._status = 'preview'
        self._next = False

    def _computeBorderWidth(self):
        """ Compute picture border width.
        
        Compute the width of the border to use in paint() and boundingRect()
        methods so the size on screen is constant, whatever the view size is.
        """
        xRatio = self.scene().views()[0].width() / self.scene().width()
        yRatio = self.scene().views()[0].height() / self.scene().height()
        return BORDER_WIDTH / min(xRatio, yRatio)

    # Interface
    def setIndex(self, index):
        """ Set the index of the picture in the shooting sequence.
        """
        self._index = index

    def getIndex(self):
        """ Return the index of the picture in the shooting sequence.
        """
        return self._index

    def setState(self, status=None, next=False):
        """ Set the current state of the picture.

        @param status: status of the picture, in
                       ('ok', 'ok-reshoot', 'error', 'error-reshoot', 'preview', 'skip')
        @type status: str

        @param next: if True, this picture is the next to shoot
        @type next: bool
        """
        if status is not None:
            self._status = status
        self._next = next
        self.update()

    def isNext(self):
        """ Is the picture the next to shoot? 
        
        @return: True if next, False if not
        @rtype: bool
        """
        return self._next


class MosaicPictureItem(AbstractPictureItem):
    """ Picture item implementation for mosaic.
    """

    # Qt overloaded methods
    def boundingRect(self):
        return QtCore.QRectF(self._x - self._computeBorderWidth() / 2,
                             self._y - self._computeBorderWidth() / 2,
                             self._w + self._computeBorderWidth(),
                             self._h + self._computeBorderWidth())

    def paint(self, painter, options, widget):
        innerColor = config.SHOOTING_COLOR_SCHEME['default'][self._status]
        if self.isNext():
            borderColor = config.SHOOTING_COLOR_SCHEME['default']['border-next']
        else:
            borderColor = config.SHOOTING_COLOR_SCHEME['default']['border']
        painter.fillRect(self._x, self._y, self._w, self._h, QtGui.QColor(*innerColor))
        painter.setPen(QtGui.QPen(QtGui.QBrush(QtGui.QColor(*borderColor)), self._computeBorderWidth()))
        painter.drawRect(self._x, self._y, self._w, self._h)


class PresetPictureItem(AbstractPictureItem):
    """ Picture item implementation for preset.
    """

    # Qt overloaded methods
    def boundingRect(self):
        return QtCore.QRectF(self._x - self._computeBorderWidth() / 2,
                             self._y - self._computeBorderWidth() / 2,
                             self._w + self._computeBorderWidth(),
                             self._h + self._computeBorderWidth())

    def paint(self, painter, options, widget):
        innerColor = config.SHOOTING_COLOR_SCHEME['default'][self._status]
        if self.isNext():
            borderColor = config.SHOOTING_COLOR_SCHEME['default']['border-next']
        else:
            borderColor = config.SHOOTING_COLOR_SCHEME['default']['border']
        path = QtGui.QPainterPath()
        path.addEllipse(self._x, self._y, self._w, self._h)
        painter.fillPath(path, QtGui.QColor(*innerColor))
        painter.setPen(QtGui.QPen(QtGui.QBrush(QtGui.QColor(*borderColor)), self._computeBorderWidth()))
        painter.drawEllipse(self._x, self._y, self._w, self._h)
