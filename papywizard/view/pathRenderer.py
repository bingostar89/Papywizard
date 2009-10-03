# -*- coding: utf-8 -*-

""" Panohead remote control.

License
=======

 - B{Papywizard} (U{http://www.papywizard.org}) is Copyright:
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

View.

@author: Frédéric Mantegazza
@copyright: (C) 2007-2009 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

import sys

from PyQt4 import QtCore, QtGui

from papywizard.common.loggingServices import Logger
from papywizard.view.arthurFrame import ArthurFrame

POINT_SIZE = 10
CAP_STYLE = QtCore.Qt.FlatCap
JOIN_STYLE = QtCore.Qt.BevelJoin
PATH_MODE = 'curveMode'
#PATH_MODE = 'lineMode'
PEN_WIDTH = 1
PEN_STYLE = QtCore.Qt.SolidLine


class PathRenderer(ArthurFrame):
    """ Path renderer class.
    """
    def __init__(self, parent=None):
        """
        """
        ArthurFrame.__init__(self, parent)
        self.__activePoint = -1
        self._points = []
        self._vectors = []
        self._mousePress = None
        self._mouseDrag = False
        self._tile = QtGui.QPixmap(128, 128)
        self._tile.fill(QtCore.Qt.white)

        self.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)

    def paintEvent(self, paintEvent):
        """
        """
        Logger().trace("PathRenderer.paintEvent()")
        painter = QtGui.QPainter()
        painter.begin(self)
        painter.setClipRect(paintEvent.rect())
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        r = self.rect()
        left = r.x() + 1
        right = r.right()
        top = r.y() + 1
        bottom = r.bottom()
        radius2 = 8. * 2.
        clipPath = QtGui.QPainterPath()
        clipPath.moveTo(right - radius2, top)
        clipPath.arcTo(right - radius2, top, radius2, radius2, 90, -90)
        clipPath.arcTo(right - radius2, bottom - radius2, radius2, radius2, 0, -90)
        clipPath.arcTo(left, bottom - radius2, radius2, radius2, 270, -90)
        clipPath.arcTo(left, top, radius2, radius2, 180, -90)
        clipPath.closeSubpath()
        painter.save()
        painter.setClipPath(clipPath, QtCore.Qt.IntersectClip)
        painter.drawTiledPixmap(self.rect(), self._tile)
        self.__paint(painter)
        painter.restore()

    def __paint(self, painter):
        Logger().trace("PathRenderer.__paint()")
        if not self._points:
            self.__initializePoints()

        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setPen(QtCore.Qt.NoPen)
        pal = QtGui.QPalette()

        # Construct path
        path = QtGui.QPainterPath()
        path.moveTo(self._points[0])
        if PATH_MODE == 'lineMode':
            for point in self._points:
                path.lineTo(point)
        else:
            i = 1
            while i + 2 < len(self._points):
                path.cubicTo(self._points[i], self._points[i + 1], self._points[i + 2])
                i += 3
            while i < len(self._points):
                path.lineTo(self._points[i])

        # Draw the path
        lg = QtCore.Qt.red

        # 'custom' pen
        if PEN_STYLE == QtCore.Qt.NoPen:
            strocker = QtGui.QPainterPathStrocker()
            strocker.setWidth(PEN_WIDTH)
            strocker.setJoinStyle(JOIN_STYLE)
            strocker.setCapStyle(CAP_STYLE)
            space = 4.
            dashes = [1, space, 3, space, 9, space, 27, space, 9, sapce, 3, space]
            strocker.setDashPattern(dashes)
            stroke = strocker.createStroke(path)
            painter.fillPath(stroke, lg)
        else:
            pen = QtGui.QPen(lg, PEN_WIDTH, PEN_STYLE, CAP_STYLE, JOIN_STYLE)
            painter.strokePath(path, pen)

        # Draw the control points
        painter.setPen(QtGui.QColor(50, 100, 120, 200))
        painter.setBrush(QtGui.QColor(200, 200, 210, 120))
        for pos in self._points:
            painter.drawEllipse(QtCore.QRectF(pos.x() - POINT_SIZE,
                                              pos.y() - POINT_SIZE,
                                              POINT_SIZE * 2,
                                              POINT_SIZE * 2))
        painter.setPen(QtGui.QPen(QtCore.Qt.lightGray, 0, QtCore.Qt.SolidLine))
        painter.setBrush(QtCore.Qt.NoBrush)
        painter.drawPolyline(QtGui.QPolygonF(self._points))

    def __initializePoints(self):
        """
        """
        Logger().trace("PathRenderer._initializePoints()")
        COUNT = 7
        self._points = []
        self._vectors = [] # ???
        m = QtGui.QMatrix()
        rot = 360. / COUNT
        center = QtCore.QPointF(self.width() / 2, self.height() / 2)
        vm = QtGui.QMatrix()
        vm.shear(2, -1)
        vm.scale(3, 3)
        for i in xrange(COUNT):
            self._vectors.append(QtCore.QPointF(.1, .25) * (m * vm))
            self._points.append(QtCore.QPointF(0, 100) * m + center)

    def __updatePoints(self):
        """
        """
        Logger().trace("PathRenderer._updatePoints()")
        PAD = 10
        left = PAD
        right = self.width() - PAD
        top = PAD
        bottom = self.height() - PAD
        assert(len(self._points) == len(self._vectors))
        for i in xrange(len(self._points)):
            if i == self.__activePoint:
                continue
            pos = self._points[i]
            vec = self._vectors[i]
            pos += vec
            if pos.x() < left or pos.x() > right:
                vec.setX(-vec.x())
                if pos.x() < left:
                    pos.setX(left)
                else:
                    pos.setX(right)
            if pos.y() < top or pos.y() > bottom:
                vec.setY(-vec.y())
                if pos.y() < top:
                    pos.setY(top)
                else:
                    pos.setY(bottom)
            self._points[i] = pos
            self._vectors[i] = vec
        self.update()

    def mousePressEvent(self, mouseEvent):
        """
        """
        Logger().trace("PathRenderer.mousePressEvent()")
        #self.setDescriptionEnable(False)
        self.__activePoint = -1
        distance = -1.
        for i, point in enumerate(self._points):
            d = QtCore.QLineF(mouseEvent.posF(), point).length()
            if distance < 0 and d < 8. * POINT_SIZE or d < distance:
                distance = d
                self.__activePoint = i

        self._mouseDrag = True
        self._mousePress = mouseEvent.pos()

        if self.__activePoint != -1:
            self.mouseMoveEvent(mouseEvent)

    def mouseMoveEvent(self, mouseEvent):
        """
        """
        Logger().trace("PathRenderer.mouseMoveEvent()")
        if not self._mouseDrag and \
        QtCore.QPoint(self._mousePress - mouseEvent.pos()).manhattanLength() > 25:
            self._mouseDrag = True

        if self._mouseDrag and 0 <= self.__activePoint < len(self._points):
            self._points[self.__activePoint] = QtCore.QPointF(mouseEvent.pos())
            self.update()

    def mouseReleaseEvent(self, mouseEvent):
        """
        """
        Logger().trace("PathRenderer.mouseReleaseEvent()")
        self.__activePoint = -1
        if not self._mouseDrag:
            self.emit(QtCore.SIGNAL("clicked()"))


def main():
    Logger()
    app = QtGui.QApplication(sys.argv)
    pathRenderer = PathRenderer()
    pathRenderer.show()
    app.exec_()


if __name__ == "__main__":
    main()
