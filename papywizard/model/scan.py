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

Model

Implements
==========

- AbstractScan
- MosaicScan
- PresetScan

@author: Frédéric Mantegazza
@copyright: (C) 2007-2008 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id: scan.py 307 2008-06-24 06:02:36Z fma $"

from papywizard.common.loggingServices import Logger
from papywizard.common.configManager import ConfigManager
from papywizard.common.presetManager import PresetManager


class AbstractScan(object):
    """ AbstractScan object.

    Scan is the base object for shooting object.
    """
    def __init__(self, model):
        """ Init the Scan object.

        @param camera: model
        @type camera: {Shooting}
        """
        super(AbstractScan, self).__init__()
        self._model = model
        self._positions = None
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

    # Helpers

    # Interface
    def generatePositions(self):
        """ Generate all (yaw, pitch) positions.
        """
        raise NotImplementedError

    def iterPositions(self):
        """ Iteration over all shooting positions.
        """
        self._index = 1
        while True:
            try:
                yield self._index, self._positions[self._index - 1]
            except IndexError:
                raise StopIteration
            self._index += 1

    def getPositionIndex(self):
        """ Get the index of the current position position.

        @return: index of the current position
        @rtype: int
        """
        return self._index

    def setPositionIndex(self, index):
        """ Set the next position to index.

        @param index: index of the next position
        @type index: int
        """
        if 1 <= index <= len(self._positions):
            self._index = index - 1 # Next iteration will increase index by 1
        else:
            raise IndexError("index out of range")


class MosaicScan(AbstractScan):
    """ MosaicScan model.
    """
    def __init__(self, *args, **kwargs):
        """ Init the MosaicScan object.
        """
        super(MosaicScan, self).__init__(*args, **kwargs)
        self.__yawIndex = None
        self.__pitchIndex = None
        self.__yawInc = None
        self.__pitchInc = None
        self.__yawIndex = None
        self.__pitchIndex = None
        self.__yawSens = None
        self.__pitchSens = None

        self.yawStart = 0.
        self.pitchStart = 0.
        self.yawEnd = 0.
        self.pitchEnd = 0.

    # Properties
    def __getStartFrom(self):
        """
        """
        return ConfigManager().get('Preferences', 'MOSAIC_START_FROM')

    def __setStartFrom(self, startFrom):
        """
        """
        ConfigManager().set('Preferences', 'MOSAIC_START_FROM', startFrom)

    startFrom = property(__getStartFrom, __setStartFrom)

    def __getInitialDirection(self):
        """
        """
        return ConfigManager().get('Preferences', 'MOSAIC_INITAL_DIR')

    def __setInitialDirection(self, initialDirection):
        """
        """
        ConfigManager().set('Preferences', 'MOSAIC_INITAL_DIR', initialDirection)

    initialDirection = property(__getInitialDirection, __setInitialDirection)

    def __getCR(self):
        """
        """
        return ConfigManager().getBoolean('Preferences', 'MOSAIC_CR')

    def __setCR(self, cr):
        """
        """
        ConfigManager().setBoolean('Preferences', 'MOSAIC_CR', cr)

    cr = property(__getCR, __setCR)

    def __getOverlap(self):
        """
        """
        return ConfigManager().getFloat('Preferences', 'MOSAIC_OVERLAP')

    def __setOverlap(self, overlap):
        """
        """
        ConfigManager().setFloat('Preferences', 'MOSAIC_OVERLAP', overlap, 2)

    overlap = property(__getOverlap, __setOverlap)

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

    #Interface
    def generatePositions(self):
        self._positions = []
        yawCameraFov = self._model.camera.getYawFov(self._model.cameraOrientation)
        pitchCameraFov = self._model.camera.getPitchFov(self._model.cameraOrientation)
        try:
            self.__yawInc = (self.yawFov - yawCameraFov) / (self.yawNbPicts - 1)
        except ZeroDivisionError:
            self.__yawInc = self.yawFov - yawCameraFov
        try:
            self.__pitchInc = (self.pitchFov - pitchCameraFov) / (self.pitchNbPicts - 1)
        except ZeroDivisionError:
            self.__pitchInc = self.pitchFov - pitchCameraFov
        self.__yawInc *= cmp(self.yawEnd, self.yawStart)
        self.__pitchInc *= cmp(self.pitchEnd, self.pitchStart)

        self.__yawIndex = 0
        self.__pitchIndex = 0
        self.__yawSens = 1
        self.__pitchSens = 1

        generate = True
        while generate:
            if self.startFrom == "start":
                yaw = self.yawStart + self.__yawIndex * self.__yawInc
                pitch = self.pitchStart + self.__pitchIndex * self.__pitchInc
            elif self.startFrom == "end":
                yaw = self.yawEnd - self.__yawIndex * self.__yawInc
                pitch = self.pitchEnd - self.__pitchIndex * self.__pitchInc
            else:
                raise ValueError("Unknown '%s' <Start from> param" % self.startFrom)
            #Logger().debug("MosaicScan.generatePositions(): __yawIndex=%d, __pitchIndex=%d, yaw=%.1f, pitch=%.1f" % (self.__yawIndex, self.__pitchIndex, yaw, pitch))
            self._positions.append((yaw, pitch))

            # Compute next position
            if self.initialDirection == "yaw":
                self.__yawIndex += self.__yawSens
            elif self.initialDirection == "pitch":
                self.__pitchIndex += self.__pitchSens

            for i in xrange(2):
                if self.__yawIndex == self.yawNbPicts: # __yawSens was 1
                    if self.initialDirection == "pitch":
                        generate = False
                    if self.cr:
                        self.__yawIndex = 0
                        self.__yawSens = 1
                    else:
                        self.__yawIndex = self.yawNbPicts - 1
                        self.__yawSens = -1
                    self.__pitchIndex += self.__pitchSens
                    continue
                elif self.__yawIndex == -1:            # __yawSens was -1
                    if self.initialDirection == "pitch":
                        generate = False
                    if self.cr:
                        self.__yawIndex = self.yawNbPicts - 1
                        self.__yawSens = -1
                    else:
                        self.__yawIndex = 0
                        self.__yawSens = 1
                    self.__pitchIndex += self.__pitchSens
                    continue

                if self.__pitchIndex == self.pitchNbPicts: # __pitchSens was 1
                    if self.initialDirection == "yaw":
                        generate = False
                    if self.cr:
                        self.__pitchIndex = 0
                        self.__pitchSens = 1
                    else:
                        self.__pitchIndex = self.pitchNbPicts - 1
                        self.__pitchSens = -1
                    self.__yawIndex += self.__yawSens
                    continue
                elif self.__pitchIndex == -1:              # __pitchSens was -1
                    if self.initialDirection == "yaw":
                        generate = False
                    if self.cr:
                        self.__pitchIndex = self.pitchNbPicts - 1
                        self.__pitchSens = -1
                    else:
                        self.__pitchIndex = 0
                        self.__pitchSens = 1
                    self.__yawIndex += self.__yawSens
                    continue
                break


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
        return ConfigManager().get("Preferences", "PRESET_NAME")

    def __setName(self, name):
        """
        """
        ConfigManager().set("Preferences", "PRESET_NAME", name)

    name = property(__getName, __setName)

    # Interface
    def generatePositions(self):
        self._positions = []
        preset = self.__presets.getByName(self.name)
        Logger().debug("PresetScan.generatePositions(): preset=%s" % preset)
        self._positions = preset.getPositions()
