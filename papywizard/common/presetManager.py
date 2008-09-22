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

Configuration

Implements
==========

- PresetManager

@author: Frédéric Mantegazza
@copyright: (C) 2007-2008 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id: configManager.py 557 2008-09-18 18:51:24Z fma $"

import copy
import os.path
import sets
import xml.dom.minidom

from papywizard.common import config
from papywizard.common.loggingServices import Logger

path = os.path.dirname(__file__)


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
        self.__name = domElement.getAttributeNode('name').value
        Logger().debug("Preset.__init__(): loading name='%s'" % self.__name)

        domTooltip = domElement.getElementsByTagName('tooltip')[0]
        tooltipLines = domTooltip.firstChild.data.strip()
        self.__tooltip = ""
        for line in tooltipLines.split('\n'):
            self.__tooltip += line.strip()

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
        return "<Preset name=%s>" % self.__name.decode("utf-8")

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

    def iterPositions(self):
        """ Iter over all positions.
        """
        for yaw, pitch in self.__positions:
            yield yaw, pitch
        raise StopIteration


class Presets(object):
    """ Presets object.

    Contain a set of Preset.
    """
    def __init__(self):
        """ Init the Presets object.
        """
        super(Presets, self).__init__()
        self.__presets = sets.Set()
        self.__numIndex = 0
        self.__index = {}

    def add(self, preset):
        """ Add a preset.

        @param preset: the preset to add
        @type preset {Preset}
        """
        self.__presets.add(preset)
        self.__index[self.__numIndex] = preset
        self.__index[preset.getName()] = self.__numIndex
        self.__numIndex += 1

    def getIndexByName(self, name):
        """ Get the index.

        Mainly use by the GUI for combobox.

        @param name: name of the preset to get the index
        @type name: str
        """
        return self.__index[name]

    def getIndexByNum(self, num):
        """ Get the index.

        Mainly use by the GUI for combobox.

        @param num: index of the preset to get the name
        @type num: int
        """
        return self.__index[num]

    def getByName(self, name):
        """ Return the preset from its given name.

        @param name: name of the preset
        @type name: str

        @return: preset
        @rtype: {Preset}
        """
        for preset in self.__presets:
            if preset.getName() == name:
                return preset

    def getAll(self):
        """ Get all presets.
        """
        return copy.deepcopy(self.__presets)


class PresetManager(object):
    """ Presets manager object.
    """
    __state = {}
    __init = True

    def __new__(cls, *args, **kwds):
        """ Implement the Borg pattern.
        """
        self = object.__new__(cls, *args, **kwds)
        self.__dict__ = cls.__state
        return self

    def __init__(self):
        """ Init the object.
        """
        if PresetManager.__init:
            self.__presets = Presets()

            # Load default presets
            presetFile = os.path.join(path, config.PRESET_FILE)
            Logger().info("Loading default presets")
            document = xml.dom.minidom.parse(presetFile)
            for presetElement in document.getElementsByTagName('preset'):
                preset = Preset(presetElement)
                self.__presets.add(preset)

            # Load user presets
            try:
                document = xml.dom.minidom.parse(config.USER_PRESET_FILE)
                Logger().info("Loading user presets")
                for presetElement in document.getElementsByTagName('preset'):
                    preset = Preset(presetElement)
                    self.__presets.add(preset)
            except IOError:
                Logger().warning("No user presets found")

            PresetManager.__init = False

    def getPresets(self):
        """ return the list of preset.
        """
        return self.__presets
