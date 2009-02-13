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

- ShootingView
- AbstractShootingScene
- MosaicShootingScene
- PresetShootingScene

@author: Frédéric Mantegazza
@copyright: (C) 2007-2009 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id: shootingScene.py 1308 2009-01-11 16:19:42Z fma $"

import math

from PyQt4 import QtCore, QtGui

from papywizard.common import config
from papywizard.common.loggingServices import Logger
from papywizard.common.configManager import ConfigManager
from papywizard.view.pictureItem import AbstractPictureItem, MosaicPictureItem, PresetPictureItem, \
                                        CrosshairCusrsor


class ShootingView(QtGui.QGraphicsView):
    def __init__(self, parent=None):
        QtGui.QGraphicsView.__init__(self, parent)
        self.setBackgroundBrush(QtGui.QColor(*config.SHOOTING_COLOR_SCHEME[config.COLOR_SCHEME]['background']))
        #self.setOptimizationFlag(QtGui.QGraphicsView.DontClipPainter, True)
        #self.setOptimizationFlag(QtGui.QGraphicsView.DontSavePainterState, True)
        #self.setOptimizationFlag(QtGui.QGraphicsView.DontAdjustForAntialiasing, False)
        self.setCacheMode(QtGui.QGraphicsView.CacheBackground)

        # Enable OpenGL support
        if config.QtOpenGL:
            try:
                from PyQt4 import QtOpenGL
                self.setViewport(QtOpenGL.QGLWidget())
                Logger().info("Use OpenGL")
            except ImportError:
                Logger().warning("QtOpenGL module not available")

    def resizeEvent(self, event):
        self.fitInView(self.scene().sceneRect(), QtCore.Qt.KeepAspectRatio)


class AbstractShootingScene(QtGui.QGraphicsScene):
    """ Qt ShootingScene widget
    """
    def __init__(self, yawStart, yawEnd, pitchStart, pitchEnd, yawFov, pitchFov, yawCameraFov, pitchCameraFov, parent=None):
        """ Init shooting scene.

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
        """
        QtGui.QGraphicsScene.__init__(self, parent)
        self._yawStart = yawStart
        self._yawEnd = yawEnd
        self._pitchStart = pitchStart
        self._pitchEnd = pitchEnd
        self._yawFov = yawFov
        self._pitchFov = pitchFov
        self._yawCameraFov = yawCameraFov
        self._pitchCameraFov = pitchCameraFov
        self._pictures = {}

        # Head position crosshair
        self._headCrosshair = CrosshairCusrsor(math.sqrt(self._yawFov ** 2 + self._pitchFov ** 2) / 10)
        self._headCrosshair.setZValue(9999)
        self.addItem(self._headCrosshair)

        self._init()

    def _init(self):
        """ Init the scene rect.
        """
        raise NotImplementedError("ShootingScene._init() is abstract and must be overidden")

    # Signals
    def pictureClicked(self, index):
        """ User clicked on a picture in the scene.
        """
        self.emit(QtCore.SIGNAL("pictureClicked"), index)

    # Qt handlers
    def mousePressEvent(self, event):
        Logger().trace("ShootingScene.mousePressEvent()")
        picture = self.itemAt(event.scenePos())
        Logger().debug("ShootingScene.mousePressEvent(): picture=%s" % picture)
        try:
            index = picture.parentItem().getIndex()
            Logger().debug("ShootingScene.mousePressEvent(): picture index=%d" % index)
            self.pictureClicked(index)
        except AttributeError:
            Logger().exception("ShootingScene.mousePressEvent()", debug=True)

    # Interface
    def addPicture(self, index, yaw, pitch, state='preview'):
        """ Add a pict at yaw/pitch coordinates.

        @param yaw: yaw pict position (°)
        @type yaw: float

        @param pitch: pitch pict position (°)
        @type pitch: float

        @param state: state of the shooting at this position
        @type state: str
        """
        raise NotImplementedError("ShootingScene.addPicture() is abstract and must be overidden")

    def setPictureState(self, index, state):
        """ Set the picture state.

        @param index: index of the picture to set the state
        @type index: int

        @param state: new state of the picture
        @type state: str
        """
        self._pictures[index].setState(state)

    def selectNextPicture(self, index):
        """ Set the picture at index the next to shoot.

        @param index: index of the next picture to shoot
        @type index: int
        """
        previousIndex = AbstractPictureItem.nextIndex
        AbstractPictureItem.nextIndex = index
        for picture in self._pictures.itervalues():
            if previousIndex <= picture.getIndex() <= index or \
               index <= picture.getIndex() <= previousIndex:
                picture.refresh()

    def clear(self):
        """ Clear the shooting area
        """
        for picture in self._pictures.itervalues():
            picture.setState(state='preview')
            AbstractPictureItem.nextIndex = 1

    def setHeadPosition(self, yaw, pitch):
        """ Set the current head position.
        """
        self._headCrosshair.setPos(yaw, -pitch)

    def refresh(self):
        """ Force refresh the scene.

        This method is mainly called by the view resizeEvent, and ask
        the items to recompute their width according to the new view size.
        """
        for picture in self._pictures.itervalues():
            picture.refresh()
        self._headCrosshair.refresh()


class MosaicShootingScene(AbstractShootingScene):
    def _init(self):
        x = min(self._yawStart, self._yawEnd) - self._yawCameraFov / 2
        y = min(self._pitchStart, self._pitchEnd) - self._pitchCameraFov / 2
        w = self._yawFov
        h = self._pitchFov
        #Logger().debug("MosaicShootingScene._init(): x=%d, y=%d, w=%d, h=%d" % (x, y, w, h))
        self.setSceneRect(x, y, w, h)

    # Interface
    def addPicture(self, index, yaw, pitch, state='preview'):
        #Logger().debug("MosaicShootingScene.addPicture(): index=%d, yaw=%.1f, pitch%.1f, state=%s" % (index, yaw, pitch, state))

        # Check if picture already in list
        if self._pictures.has_key(index):
            raise ValueError("Picture at index %d already exists" % index)
        else:
            picture = MosaicPictureItem(index, self._yawCameraFov, self._pitchCameraFov)
            self.addItem(picture)
            picture.setState(state)
            picture.setPos(yaw, -pitch)
            self._pictures[index] = picture


class PresetShootingScene(AbstractShootingScene):
    def _init(self):
        x = min(self._yawStart, self._yawEnd) - self._yawCameraFov / 2
        y = min(self._pitchStart, self._pitchEnd) - self._pitchCameraFov / 2
        w = self._yawFov + self._yawCameraFov
        h = self._pitchFov + self._pitchCameraFov
        #Logger().debug(""PresetShootingScene._init(): x=%d, y=%d, w=%d, h=%d" % (x, y, w, h))
        self.setSceneRect(x, y, w, h)

        # Add full-sphere border
        fullSphericalArea = QtGui.QGraphicsRectItem(self._yawStart, self._pitchStart, self._yawFov, self._pitchFov)
        fullSphericalArea.setZValue(0)
        self.addItem(fullSphericalArea)

    # Interface
    def addPicture(self, index, yaw, pitch, state='preview'):
        #Logger().debug("PresetShootingScene.addPicture(): index=%d, yaw=%.1f, pitch%.1f, state=%s" % (index, yaw, pitch, state))

        # Check if picture already in list
        if self._pictures.has_key(index):
            raise ValueError("Picture at index %d already exists" % index)
        else:
            picture = PresetPictureItem(index, self._yawCameraFov, self._pitchCameraFov)
            self.addItem(picture)
            picture.setState(state)
            picture.setPos(yaw, -pitch)
            self._pictures[index] = picture
