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

Data management

Implements
==========

- Data
- MosaicData
- Presetdata

Usage
=====

Data is used during shooting, and generate a xml file containing
usefull information for stitchers. AutoPano Pro takes advantage of
such datas, for example to correctly set unlinked pictures at their
correct place (sky pictures without any details are often unlinked).

@author: Frédéric Mantegazza
@copyright: (C) 2007-2008 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

import time
import os.path
import xml.dom.minidom

from papywizard.common import config
from papywizard.common.configManager import ConfigManager
from papywizard.common.loggingServices import Logger

XML_VERSION = "0.9"


class AbstractData(object):
    """ Manage the data.
    """
    def __init__(self):
        """ Init object.
        """
        super(AbstractData, self).__init__()
        date = time.strftime("%Y-%m-%d", time.localtime())
        time_ = time.strftime("%H:%M:%S", time.localtime())
        mode = self._getMode()
        self._dataFileFormatDict = {'date': date,
                                    'time': time_,
                                    'date_time': "%s_%s" % (date, time_),
                                    'mode': mode}

        # Create xml tree
        Logger().debug("Data.__init__(): create xml tree")
        self.__impl = xml.dom.minidom.getDOMImplementation()
        self._doc = self.__impl.createDocument(None, "papywizard", None)
        self._rootNode = self._doc.documentElement
        self._rootNode.setAttribute("version", XML_VERSION)

        # Create 'header' node
        self._headerNode = self._doc.createElement('header')
        self._rootNode.appendChild(self._headerNode)

        # Create 'shoot' node
        self._shootNode = self._doc.createElement('shoot')
        self._rootNode.appendChild(self._shootNode)

        self._pictId = 1

    def _getMode(self):
        """ Return the shooting mode.
        """
        raise NotImplementedError

    def _createNode(self, parent, tag):
        """ Create a node.

        @param parent: parent node
        @type parent: {DOM Element}

        @param tag: name of the tag
        @type tag: str
        """
        node = self._doc.createElement(tag)
        parent.appendChild(node)
        return node

    def _createTextNode(self, parent, tag, text):
        """ Create a text node.

        @param parent: parent node
        @type parent: {DOM Element}

        @param tag: name of the text tag
        @type tag: str

        @param text: text to use
        @type text: str
        """
        textNode = self._createNode(parent, tag)
        text = self._doc.createTextNode(text)
        textNode.appendChild(text)
        return textNode

    def _addNode(self, parent, tag, value=None, **attr):
        """ Add a sub node.

        @param parent: parent node
        @type parent: {DOM Element}

        @param tag: tag of the node
        @type tag: str

        @param value: value of the node
        @type value: str

        @param attr: optionnal attributes
        @type attr: dict
        """
        Logger().debug("Data._addNode(): parent=%s, tag=%s, value=%s, attr=%s" % (parent.tagName, tag, value, attr))
        if value is not None:
            node = self._createTextNode(parent, tag, value)
        else:
            node = self._createNode(parent, tag)
        for key, val in attr.iteritems():
            node.setAttribute(key, val)
        return node

    def _serialize(self):
        """ Serialize xml tree to file.
        """
        if ConfigManager().getBoolean('Data', 'DATA_FILE_ENABLE'):

            # Update end shooting date
            #self._headerShootingEnd.

            Logger().trace("Data.serialize()")
            dataFileFormat = "papywizard_%s.xml" % ConfigManager().get('Data', 'DATA_FILE_FORMAT')
            fileName = os.path.join(config.HOME_DIR, dataFileFormat)
            xmlFile = file(fileName % self._dataFileFormatDict, 'w')
            self._doc.writexml(xmlFile, addindent="    ", newl='\n', encoding="utf-8")
            xmlFile.close()

    def createHeader(self, values):
        """ Create the header.

        @param values: values to put in the header
        @type values: dict
        """
        Logger().debug("Data.createHeader(): values=%s" % values)

        # Shooting
        node = self._addNode(self._headerNode, 'shooting', mode=self._getMode())
        self._addNode(node, 'stabilizationDelay', values['stabilizationDelay'])
        self._addNode(node, 'cameraOrientation', values['cameraOrientation'])
        self._addNode(node, 'start', time.ctime())
        self._headerShootingEnd = self._addNode(node, 'end', time.ctime())
        self._addNode(node, 'comment', values['comment'])

        # Camera
        node = self._addNode(self._headerNode, 'camera')
        self._addNode(node, 'timeValue', values['timeValue'])
        self._addNode(node, 'bracketing', nbPicts=values['bracketingNbPicts'],
                                          intent=values['bracketingIntent'])
        self._addNode(node, 'sensor', coef=values['sensorCoef'],
                                      ratio=values['sensorRatio'])

        # Lens
        node = self._addNode(self._headerNode, 'lens', type=values['lensType'])
        if values['lensType'] == 'rectilinear':
            self._addNode(node, 'focal', values['focal'])

    def addPicture(self, bracket, yaw, pitch):
        """ Add a new picture node to shoot node.

        @param bracket: num of the pict (bracketing)
        @type bracket: int

        @param yaw: yaw position
        @type yaw: float

        @param pitch: pitch position
        @type pitch: float
        """
        Logger().debug("Data.addPicture(): bracket=%d, yaw=%.1f, pitch=%.1f" % (bracket, yaw, pitch))
        node = self._addNode(self._shootNode, 'pict', id="%d" % self._pictId, bracket="%d" % bracket)
        self._pictId += 1
        self._addNode(node, 'time', time.ctime())
        self._addNode(node, 'position', yaw="%.1f" % yaw, pitch="%.1f" % pitch)
        self._headerShootingEnd.firstChild.data = time.ctime()

        # Serialize xml file
        self._serialize()


class MosaicData(AbstractData):
    """ Manage the data for mosaic.

    Format for mosaic data::

    <?xml version="1.0" encoding="utf-8"?>
    <papywizard version="0.9">
        <header>
            <shooting mode="mosaic">
                <stabilizationDelay>0.5</stabilizationDelay>
                <cameraOrientation>portrait</cameraOrientation>
                <start>Mon Oct 13 10:52:33 2008</start>
                <end>Mon Oct 13 10:52:53 2008</end>
                <comment>Néron mountain</comment>
            </shooting>
            <mosaic>
                <nbPicts pitch="1" yaw="3"/>
                <overlap minimum="0.25" pitch="1.00" yaw="0.26"/>
            </mosaic>
            <camera>
                <timeValue>0.5</timeValue>
                <bracketing intent="focus" nbPicts="1"/>
                <sensor coef="1.6" ratio="3:2"/>
            </camera>
            <lens type="rectilinear">
                <focal>17.0</focal>
            </lens>
        </header>
        <shoot>
            <pict id="1" bracket="1">
                <time>Mon Oct 13 10:52:39 2008</time>
                <position pitch="0.0" yaw="-44.4"/>
            </pict>
            <pict id="2" bracket="2">
                <time>Mon Oct 13 10:52:40 2008</time>
                <position pitch="0.0" yaw="-44.4"/>
            </pict>
            <pict id="3" bracket="3">
                <time>Mon Oct 13 10:52:41 2008</time>
                <position pitch="0.0" yaw="-44.4"/>
            </pict>
            <pict id="4" bracket="1">
                <time>Mon Oct 13 10:52:45 2008</time>
                <position pitch="0.0" yaw="-9.3"/>
            </pict>
            <pict id="5" bracket="2">
                <time>Mon Oct 13 10:52:46 2008</time>
                <position pitch="0.0" yaw="-9.3"/>
            </pict>
            <pict id="6" bracket="3">
                <time>Mon Oct 13 10:52:47 2008</time>
                <position pitch="0.0" yaw="-9.3"/>
            </pict>
            <pict id="7" bracket="1">
                <time>Mon Oct 13 10:52:51 2008</time>
                <position pitch="0.0" yaw="25.7"/>
            </pict>
            <pict id="8" bracket="2">
                <time>Mon Oct 13 10:52:52 2008</time>
                <position pitch="0.0" yaw="25.7"/>
            </pict>
            <pict id="9" bracket="3">
                <time>Mon Oct 13 10:52:53 2008</time>
                <position pitch="0.0" yaw="25.7"/>
            </pict>
        </shoot>
    </papywizard>
    """
    def _getMode(self):
        """ Return the shooting mode.
        """
        return 'mosaic'

    def createHeader(self, values):
        super(MosaicData, self).createHeader(values)

        # Mosaic
        node = self._addNode(self._headerNode, 'mosaic')
        self._addNode(node, 'nbPicts', yaw=values['yawNbPicts'],
                                       pitch=values['pitchNbPicts'])
        self._addNode(node, 'overlap', minimum=values['overlap'],
                                       yaw=values['yawRealOverlap'],
                                       pitch=values['pitchRealOverlap'])

        # Serialize xml file
        self._serialize()


class PresetData(AbstractData):
    """ Manage the data for presets.

    Format for mosaic data:

    <?xml version="1.0" encoding="utf-8"?>
    <papywizard version="0.9">
        <header>
            <shooting mode="preset">
                <stabilizationDelay>0.5</stabilizationDelay>
                <cameraOrientation>portrait</cameraOrientation>
                <start>Mon Oct 13 10:30:47 2008</start>
                <end>Mon Oct 13 10:31:40 2008</end>
                <comment>Inside my living room</comment>
            </shooting>
            <preset template="3@-15 + Z"/>
            <camera>
                <timeValue>0.5</timeValue>
                <bracketing intent="focus" nbPicts="1"/>
                <sensor coef="1.6" ratio="3:2"/>
            </camera>
            <lens type="fisheye"/>
        </header>
        <shoot>
            <pict id="1" bracket="1">
                <time>Mon Oct 13 10:31:04 2008</time>
                <position pitch="-15.0" yaw="0.0"/>
            </pict>
            <pict id="2" bracket="2">
                <time>Mon Oct 13 10:31:05 2008</time>
                <position pitch="-15.0" yaw="0.0"/>
            </pict>
            <pict id="3" bracket="3">
                <time>Mon Oct 13 10:31:06 2008</time>
                <position pitch="-15.0" yaw="0.0"/>
            </pict>
            <pict id="4" bracket="1">
                <time>Mon Oct 13 10:31:16 2008</time>
                <position pitch="-15.0" yaw="120.0"/>
            </pict>
            <pict id="5" bracket="2">
                <time>Mon Oct 13 10:31:17 2008</time>
                <position pitch="-15.0" yaw="120.0"/>
            </pict>
            <pict id="6" bracket="3">
                <time>Mon Oct 13 10:31:18 2008</time>
                <position pitch="-15.0" yaw="120.0"/>
            </pict>
            <pict id="7" bracket="1">
                <time>Mon Oct 13 10:31:27 2008</time>
                <position pitch="-15.0" yaw="240.0"/>
            </pict>
            <pict id="8" bracket="2">
                <time>Mon Oct 13 10:31:28 2008</time>
                <position pitch="-15.0" yaw="240.0"/>
            </pict>
            <pict id="9" bracket="3">
                <time>Mon Oct 13 10:31:29 2008</time>
                <position pitch="-15.0" yaw="240.0"/>
            </pict>
            <pict id="10" bracket="1">
                <time>Mon Oct 13 10:31:38 2008</time>
                <position pitch="90.0" yaw="240.0"/>
            </pict>
            <pict id="11" bracket="2">
                <time>Mon Oct 13 10:31:39 2008</time>
                <position pitch="90.0" yaw="240.0"/>
            </pict>
            <pict id="12" bracket="3">
                <time>Mon Oct 13 10:31:40 2008</time>
                <position pitch="90.0" yaw="240.0"/>
            </pict>
        </shoot>
    </papywizard>
    """
    def _getMode(self):
        """ Return the shooting mode.
        """
        return 'preset'

    def createHeader(self, values):
        super(PresetData, self).createHeader(values)

        # Preset
        node = self._addNode(self._headerNode, 'preset', template=values['template'])
        #self._addNode(node, 'template', values['template'])

        # Serialize xml file
        self._serialize()
