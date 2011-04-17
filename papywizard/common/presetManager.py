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

Configuration

Implements
==========

- PresetManager

@author: Frédéric Mantegazza
@copyright: (C) 2007-2011 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

import copy
import sys
import os.path
import xml.dom.minidom

from PyQt4 import QtCore

from papywizard.common import config
from papywizard.common.orderedDict import OrderedDict
from papywizard.common.loggingServices import Logger

if hasattr(sys, "frozen"):
    path = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "papywizard", "common")
else:
    path = os.path.dirname(__file__)
presetManager = None


class Preset(object):
    """ Preset object.

    Contain a preset
    """
    def __init__(self, domElement):
        """ Init the Preset object.

        @param domElement: DOM element to parse
        @type domElement: {Element}
        """
        super(Preset, self).__init__()

        # Parse the element and store it as python objects
        self.__name = domElement.getAttributeNode('name').value[:30]
        Logger().debug("Preset.__init__(): loading name='%s'" % self.__name)

        domTooltip = domElement.getElementsByTagName('tooltip')[0]
        tooltipLines = domTooltip.firstChild.data.strip()
        self.__tooltip = ""
        for line in tooltipLines.split('\n'):
            self.__tooltip += "%s\n" % line.strip()

        domShoot = domElement.getElementsByTagName('shoot')[0]
        domPicts = domShoot.getElementsByTagName('pict')
        self.__positions = []
        for domPict in domPicts:
            yaw = domPict.getAttributeNode('yaw').value
            if yaw == 'None':
                yaw = self.__positions[-1][0]
            pitch = domPict.getAttributeNode('pitch').value
            if pitch == 'None':
                pitch = self.__positions[-1][1]
            self.__positions.append((float(yaw), float(pitch)))

    def __repr__(self):
        return "<Preset name=%s>" % self.__name.decode(sys.getfilesystemencoding())

    def getName(self):
        """ Return the preset name.
        """
        return self.__name

    def getTooltip(self):
        """ Return teh perset rooltip.
        """
        return self.__tooltip

    def getPositions(self):
        """ Return preset positions.
        """
        return copy.deepcopy(self.__positions)

    def getNbPicts(self):
        """ Get the number of pictures to shoot.
        """
        return len(self.__positions)


class Presets(object):
    """ Presets object.

    Contain a set of Preset.
    """
    def __init__(self):
        """ Init the Presets object.
        """
        super(Presets, self).__init__()
        self.__presets = OrderedDict()

    def add(self, preset):
        """ Add a preset.

        @param preset: the preset to add
        @type preset {Preset}
        """
        if self.__presets.has_key(preset.getName()):
            Logger().warning("Presets.add(): Preset '%s' alreay in presets table. Overwriting..." % preset.getName())
        self.__presets[preset.getName()] = preset

    def nameToIndex(self, name):
        """ Get the index of the preset.

        Mainly use by the GUI for combobox.

        @param name: name of the preset to get the index
        @type name: str
        """
        for iIndex, (iName, iPreset) in enumerate(self.__presets.iteritems()):
            if name == iName:
                return iIndex
        raise ValueError("Preset '%s' not found" % name)

    def getByIndex(self, index):
        """ Get the index.

        Mainly use by the GUI for combobox.

        @param index: index of the preset to get the name
        @type index: int
        """
        for iIndex, (iName, iPreset) in enumerate(self.__presets.iteritems()):
            if index == iIndex:
                return iPreset
        raise ValueError("No Preset at index '%d'" % index)

    def getByName(self, name):
        """ Return the preset from its given name.

        @param name: name of the preset
        @type name: str

        @return: preset
        @rtype: {Preset}
        """
        for iName, iPreset in self.__presets.iteritems():
            if name == iName:
                return iPreset
        raise ValueError("Preset '%s' not found" % name)

    def getAll(self):
        """ Get all presets.
        """
        return copy.deepcopy(self.__presets)


class PresetManagerObject(QtCore.QObject):
    """ Presets manager object.
    """
    def __init__(self):
        """ Init the object.
        """
        self.__presets = Presets()

        # Load default presets
        presetFile = os.path.join(path, config.PRESET_FILE)
        Logger().info("Loading default presets")
        self.importPresetFile(presetFile)

        # Load user presets
        try:
            Logger().info("Loading user presets")
            self.importPresetFile(config.USER_PRESET_FILE)
        except IOError:
            Logger().warning("No user presets found")

    def importPresetFile(self, presetFileName):
        """ Import the presets from given file.

        @param presetFileName: xml file containing the presets to import
        @type presetFileName: str
        """
        document = xml.dom.minidom.parse(file(presetFileName))
        for presetElement in document.getElementsByTagName('preset'):
            preset = Preset(presetElement)
            self.__presets.add(preset)

    def getPresets(self):
        """ return the list of preset.
        """
        return self.__presets


# ConfigManager factory
def PresetManager():
    global presetManager
    if presetManager is None:
        presetManager = PresetManagerObject()

    return presetManager
