# -*- coding: utf-8 -*-

""" Panohead remote control.

License
=======

 - B{Papywizard} (U{http://www.papywizard.org}) is Copyright:
  - (C) 2007-2011 Frédéric Mantegazza

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

Model

Implements
==========

- AbstractScan
- MosaicScan
- PresetScan

@author: Frédéric Mantegazza
@copyright: (C) 2007-2011 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

import math

from papywizard.common.loggingServices import Logger
from papywizard.common.configManager import ConfigManager
from papywizard.common.presetManager import PresetManager


class AbstractScan(object):
    """ AbstractScan object.

    Scan is the base object for shooting object.
    """
    def __init__(self, model):
        """ Init the Scan object.

        @param model: model
        @type model: {Shooting}
        """
        super(AbstractScan, self).__init__()
        self._model = model
        self._positions = None
        self._reversed = False
        self._index = None

    # Properties
    def _getTotalNbPicts(self):
        """ Compute the total number of pictures.
        """
        raise NotImplementedError

    def __getTotalNbPicts(self):
        """ Workarround to have totalNbPicts property working in subclasses.
        """
        return self._getTotalNbPicts()

    totalNbPicts = property(__getTotalNbPicts)

    def _getIndex(self):
        """ Get the current position index.
        """
        return self._index

    def _setIndex(self, index):
        """ Set the current position index.

        @param index: index of the current position
        @type index: int
        """
        if 1 <= index <= len(self._positions):
            self._index = index
        else:
            raise IndexError("position index out of range")

    index = property(_getIndex, _setIndex)

    # Helpers

    # Interface
    def generatePositions(self):
        """ Generate all positions.
        """
        raise NotImplementedError

    def reverseDirection(self, reverse=None):
        """ Reverse the direction according to flag.

        @param reverse: if True, reverse direction
                        if False, use default direction
                        if None, toggle direction
        @type reverse: bool
        """
        if reverse is None or reverse and not self._reversed or not reverse and self._reversed:
            self._positions.reverse()
            self._reversed = not self._reversed

    def getCurrentPosition(self):
        """ Get the current position.
        """
        raise NotImplementedError

    def getAllPositions(self):
        """ Get all positions.
        """
        raise NotImplementedError

    def setOverPosition(self):
        """ Workarround use by Shooting.

        Hugly!!!
        """
        self._index = len(self._positions) + 1


class MosaicScan(AbstractScan):
    """ MosaicScan model.
    """
    def __init__(self, *args, **kwargs):
        """ Init the MosaicScan object.
        """
        super(MosaicScan, self).__init__(*args, **kwargs)
        self.corners = [{'yaw': 0., 'pitch': 0.},
                        {'yaw': 0., 'pitch': 0.}]  # Use properties and compute yaw/pitc start/end when modified

    # Properties
    def __getYawStart(self):
        """
        """
        if self.startFrom == 'nearest-corner':
            try:
                startFrom = self.__getNearestCorner()
            except:  # Occurs when not connected
                Logger().exception("MosaicScan.__getYawStart():", debug=True)
                startFrom = 'top-left'
        else:
            startFrom = self.startFrom
        if startFrom in ('top-left', 'bottom-left'):
            return min(self.corners[0]['yaw'], self.corners[1]['yaw'])
        elif startFrom in ('top-right', 'bottom-right'):
            return max(self.corners[0]['yaw'], self.corners[1]['yaw'])

    yawStart = property(__getYawStart)

    def __getYawEnd(self):
        """
        """
        if self.startFrom == 'nearest-corner':
            try:
                startFrom = self.__getNearestCorner()
            except:  # Occurs when not connected
                Logger().exception("MosaicScan.__getYawStart():", debug=True)
                startFrom = 'top-left'
        else:
            startFrom = self.startFrom
        if startFrom in ('top-left', 'bottom-left'):
            return max(self.corners[0]['yaw'], self.corners[1]['yaw'])
        elif startFrom in ('top-right', 'bottom-right'):
            return min(self.corners[0]['yaw'], self.corners[1]['yaw'])

    yawEnd = property(__getYawEnd)

    def __getPitchStart(self):
        """
        """
        if self.startFrom == 'nearest-corner':
            try:
                startFrom = self.__getNearestCorner()
            except:  # Occurs when not connected
                Logger().exception("MosaicScan.__getYawStart():", debug=True)
                startFrom = 'top-left'
        else:
            startFrom = self.startFrom
        if startFrom in ('top-left', 'top-right'):
            return max(self.corners[0]['pitch'], self.corners[1]['pitch'])
        elif startFrom in ('bottom-left', 'bottom-right'):
            return min(self.corners[0]['pitch'], self.corners[1]['pitch'])

    pitchStart = property(__getPitchStart)

    def __getPitchEnd(self):
        """
        """
        if self.startFrom == 'nearest-corner':
            try:
                startFrom = self.__getNearestCorner()
            except:  # Occurs when not connected
                Logger().exception("MosaicScan.__getYawStart():", debug=True)
                startFrom = 'top-left'
        else:
            startFrom = self.startFrom
        if startFrom in ('top-left', 'top-right'):
            return min(self.corners[0]['pitch'], self.corners[1]['pitch'])
        elif startFrom in ('bottom-left', 'bottom-right'):
            return max(self.corners[0]['pitch'], self.corners[1]['pitch'])

    pitchEnd = property(__getPitchEnd)

    def __getStartFrom(self):
        """
        """
        return ConfigManager().get('Configuration/MOSAIC_START_FROM')

    def __setStartFrom(self, startFrom):
        """
        """
        ConfigManager().set('Configuration/MOSAIC_START_FROM', startFrom)

    startFrom = property(__getStartFrom, __setStartFrom)

    def __getInitialDirection(self):
        """
        """
        return ConfigManager().get('Configuration/MOSAIC_INITAL_DIR')

    def __setInitialDirection(self, initialDirection):
        """
        """
        ConfigManager().set('Configuration/MOSAIC_INITAL_DIR', initialDirection)

    initialDirection = property(__getInitialDirection, __setInitialDirection)

    def __getCR(self):
        """
        """
        return ConfigManager().getBoolean('Configuration/MOSAIC_CR')

    def __setCR(self, cr):
        """
        """
        ConfigManager().setBoolean('Configuration/MOSAIC_CR', cr)

    cr = property(__getCR, __setCR)

    def __getOverlap(self):
        """
        """
        return ConfigManager().getFloat('Configuration/MOSAIC_OVERLAP')

    def __setOverlap(self, overlap):
        """
        """
        ConfigManager().setFloat('Configuration/MOSAIC_OVERLAP', overlap, 2)

    overlap = property(__getOverlap, __setOverlap)

    # Move to normal interface
    def __getYawFov(self):
        """
        """
        yawCameraFov = self._model.camera.getYawFov(self._model.cameraOrientation)
        yawFov = abs(self.yawEnd - self.yawStart) + yawCameraFov
        return yawFov

    yawFov = property(__getYawFov, "Total yaw FoV")

    def __getPitchFov(self):
        """
        """
        pitchCameraFov = self._model.camera.getPitchFov(self._model.cameraOrientation)
        pitchFov = abs(self.pitchEnd - self.pitchStart) + pitchCameraFov
        return pitchFov

    pitchFov = property(__getPitchFov, "Total pitch FoV")

    def __getYawNbPicts(self):
        """
        """
        yawCameraFov = self._model.camera.getYawFov(self._model.cameraOrientation)
        if round(self.yawFov - yawCameraFov, 1) >= 0.1:
            yawNbPicts = int(((self.yawFov - self.overlap * yawCameraFov) / (yawCameraFov * (1 - self.overlap))) + 1)
        else:
            yawNbPicts = 1
        return yawNbPicts

    yawNbPicts = property(__getYawNbPicts, "Yaw nb picts")

    def __getPitchNbPicts(self):
        """
        """
        pitchCameraFov = self._model.camera.getPitchFov(self._model.cameraOrientation)
        if round(self.pitchFov - pitchCameraFov, 1) >= 0.1:
           nbPicts = int(((self.pitchFov - self.overlap * pitchCameraFov) / (pitchCameraFov * (1 - self.overlap))) + 1)
        else:
            nbPicts = 1
        return nbPicts

    pitchNbPicts = property(__getPitchNbPicts, "Pitch nb picts")

    def _getTotalNbPicts(self):
        return self.yawNbPicts * self.pitchNbPicts

    def __getYawRealOverlap(self):
        """ Recompute real yaw overlap.
        """
        yawCameraFov = self._model.camera.getYawFov(self._model.cameraOrientation)
        if self.yawNbPicts > 1:
            yawOverlap = (self.yawNbPicts * yawCameraFov - self.yawFov) / (yawCameraFov * (self.yawNbPicts - 1))
        else:
            yawOverlap = 1.
        return yawOverlap

    yawRealOverlap = property(__getYawRealOverlap, "Yaw real overlap")

    def __getPitchRealOverlap(self):
        """ Recompute real pitch overlap.
        """
        pitchCameraFov = self._model.camera.getPitchFov(self._model.cameraOrientation)
        if self.pitchNbPicts > 1:
            pitchOverlap = (self.pitchNbPicts * pitchCameraFov - self.pitchFov) / (pitchCameraFov * (self.pitchNbPicts - 1))
        else:
            pitchOverlap = 1.
        return pitchOverlap

    pitchRealOverlap = property(__getPitchRealOverlap, "Pitch real overlap")

    # Helpers
    def __getNearestCorner(self):
        """ Return the nearest corner from the current position.

        @return: nearest corner, in ('top-left', 'top-right', 'bottom-left', 'bottom-right')
        @rtype: str

        @todo: use a cache system
        """
        #Logger().trace("MosaicScan.__getNearestCorner()")

        # Get current position
        yaw, pitch = self._model.head.readPosition()

        # Get corners
        left = min(self.corners[0]['yaw'], self.corners[1]['yaw'])
        right = max(self.corners[0]['yaw'], self.corners[1]['yaw'])
        top = max(self.corners[0]['pitch'], self.corners[1]['pitch'])
        bottom = min(self.corners[0]['pitch'], self.corners[1]['pitch'])

        # Compute distance
        toTopLeft = math.sqrt((yaw - left) ** 2 + (pitch - top) ** 2)
        toTopRight = math.sqrt((yaw - right) ** 2 + (pitch - top) ** 2)
        toBottomLeft = math.sqrt((yaw - left) ** 2 + (pitch - bottom) ** 2)
        toBottomRight = math.sqrt((yaw - right) ** 2 + (pitch - bottom) ** 2)

        # Search nearest
        nearest = min(toTopLeft, toTopRight, toBottomLeft, toBottomRight)
        if nearest == toTopLeft:
            return 'top-left'
        elif nearest == toTopRight:
            return 'top-right'
        elif nearest == toBottomLeft:
            return 'bottom-left'
        elif nearest == toBottomRight:
            return 'bottom-right'

    # Interface
    def generatePositions(self):
        self._positions = []
        self._index = 1
        yawStart = self.yawStart
        pitchStart = self.pitchStart
        yawEnd = self.yawEnd
        pitchEnd = self.pitchEnd
        try:
            yawInc = (yawEnd - yawStart) / (self.yawNbPicts - 1)
        except ZeroDivisionError:
            yawInc = yawEnd - yawStart
        try:
            pitchInc = (pitchEnd - pitchStart) / (self.pitchNbPicts - 1)
        except ZeroDivisionError:
            pitchInc = pitchEnd - pitchStart

        yaw = yawStart
        pitch = pitchStart
        yawIndex = 1
        pitchIndex = 1
        yawIndexInc = 1
        pitchIndexInc = 1

        if self.initialDirection == 'yaw':
            for i in xrange(self.pitchNbPicts):
                for j in xrange(self.yawNbPicts):
                    self._positions.append((yawIndex, pitchIndex, yaw, pitch))
                    yaw += yawInc
                    yawIndex += yawIndexInc
                pitch += pitchInc
                pitchIndex += pitchIndexInc
                if self.cr:
                    yaw = yawStart
                    yawIndex = 1
                else:
                    yaw -= yawInc
                    yawInc *= -1
                    yawIndexInc *= -1
                    yawIndex += yawIndexInc
        else:
            for i in xrange(self.yawNbPicts):
                for j in xrange(self.pitchNbPicts):
                    self._positions.append((yawIndex, pitchIndex, yaw, pitch))
                    pitch += pitchInc
                    pitchIndex += pitchIndexInc
                yaw += yawInc
                yawIndex += yawIndexInc
                if self.cr:
                    pitch = pitchStart
                    pitchIndex = 1
                else:
                    pitch -= pitchInc
                    pitchInc *= -1
                    pitchIndexInc *= -1
                    pitchIndex += pitchIndexInc

    def getCurrentPosition(self):
        yawIndex, pitchIndex, yaw, pitch = self._positions[self._index - 1]
        return (self._index, yawIndex, pitchIndex), (yaw, pitch)

    def getAllPositions(self):
        positions = []
        for index, position in enumerate(self._positions):
            yawIndex, pitchIndex, yaw, pitch = position
            positions.append(((index + 1, yawIndex, pitchIndex), (yaw, pitch)))
        return positions

    def getYawResolution(self):
        """ Compute the total pano yaw resolution

        @return: pano yaw resolution (Mpx)
        @rtype: float
        """
        yawCameraFov = self._model.camera.getYawFov(self._model.cameraOrientation)
        return self.yawFov / yawCameraFov * self._model.camera.getYawSensorResolution(self._model.cameraOrientation)

    def getPitchResolution(self):
        """ Compute the total pano pitch resolution

        @return: pano pitch resolution (Mpx)
        @rtype: float
        """
        pitchCameraFov = self._model.camera.getPitchFov(self._model.cameraOrientation)
        return self.pitchFov / pitchCameraFov * self._model.camera.getPitchSensorResolution(self._model.cameraOrientation)


class PresetScan(AbstractScan):
    """ PresetScan model.
    """
    def __init__(self, *args, **kwargs):
        """ Init the Preset object.
        """
        super(PresetScan, self).__init__(*args, **kwargs)
        self.__presets = PresetManager().getPresets()

    # Properties
    def _getTotalNbPicts(self):
        """ Compute the total number of pictures.
        """
        preset = self.__presets.getByName(self.name)
        return preset.getNbPicts()

    def __getName(self):
        """
        """
        return ConfigManager().get('Core/PRESET_NAME')

    def __setName(self, name):
        """
        """
        ConfigManager().set('Core/PRESET_NAME', name)

    name = property(__getName, __setName)

    # Interface
    def generatePositions(self):
        self._positions = []
        self._index = 1
        preset = self.__presets.getByName(self.name)
        Logger().debug("PresetScan.generatePositions(): preset=%s" % preset)
        self._positions = preset.getPositions()

    def getCurrentPosition(self):
        yaw, pitch = self._positions[self._index - 1]
        return self._index, (yaw, pitch)

    def getAllPositions(self):
        positions = []
        for index, position in enumerate(self._positions):
            yaw, pitch = position
            positions.append((index + 1, (yaw, pitch)))
        return positions
