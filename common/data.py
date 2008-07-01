# -*- coding: iso-8859-1 -*-

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

Usage
=====

Data is used during shooting, and generate a xml file containing
usefull information for stitchers. AutoPano Pro takes advantage of
such datas, for example to correctly set unlinked pictures at their
correct place (sky pictures without any details are often unlinked).

<?xml version="1.0" ?>
<papywizard>
    <header>
        <shooting>
            <stabilizationDelay>0.5</stabilizationDelay>
            <overlap minimum="0.25" pitch="1.00" yaw="0.58"/>
            <cameraOrientation>portrait</cameraOrientation>
        </shooting>
        <camera>
            <timeValue>0.5</timeValue>
            <nbPicts>2</nbPicts>
            <sensor coef="1.6" ratio="3:2"/>
        </camera>
        <lens>
            <focal>17.0</focal>
            <fisheye>False</fisheye>
        </lens>
        <template type="mosaic">
            <nbPicts pitch="1" yaw="2"/>
        </template>
    </header>
    <shoot>
        <image id="1" pict="1">
            <time>Wed Jun 25 10:37:16 2008</time>
            <position pitch="0.0" yaw="0.0"/>
        </image>
        <image id="2" pict="2">
            <time>Wed Jun 25 10:37:17 2008</time>
            <position pitch="0.0" yaw="0.0"/>
        </image>
        <image id="3" pict="1">
            <time>Wed Jun 25 10:37:20 2008</time>
            <position pitch="0.0" yaw="20.1"/>
        </image>
        <image id="4" pict="2">
            <time>Wed Jun 25 10:37:21 2008</time>
            <position pitch="0.0" yaw="20.1"/>
        </image>
    </shoot>
</papywizard>

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


class Data(object):
    """ Manage the data.
    """
    def __init__(self):
        """ Init object.

        #@param headerInfo: informations stored in the <header> section
        #@type headerInfo: dict
        """
        Logger().debug("Data.__init__(): create xml tree")
        self.__date = time.strftime("%Y-%m-%d_%H:%M:%S", time.localtime())

        # Create xml tree
        self.__impl = xml.dom.minidom.getDOMImplementation()
        self.__doc = self.__impl.createDocument(None, "papywizard", None)
        self.__rootNode = self.__doc.documentElement

        # Create 'header' node
        self.__headerNode = self.__doc.createElement('header')
        self.__rootNode.appendChild(self.__headerNode)

        # Create 'shoot' node
        self.__shootNode = self.__doc.createElement('shoot')
        self.__rootNode.appendChild(self.__shootNode)

        self.__pictId = 1

    def __createNode(self, parent, tag):
        """ Create a node.

        @param parent: parent node
        @type parent: {DOM Element}

        @param tag: name of the tag
        @type tag: str
        """
        node = self.__doc.createElement(tag)
        parent.appendChild(node)
        return node

    def __createTextNode(self, parent, tag, text):
        """ Create a text node.

        @param parent: parent node
        @type parent: {DOM Element}

        @param tag: name of the text tag
        @type tag: str

        @param text: text to use
        @type text: str
        """
        textNode = self.__createNode(parent, tag)
        text = self.__doc.createTextNode(text)
        textNode.appendChild(text)
        return textNode

    def __addNode(self, parent,  tag, value=None, **attr):
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
        Logger().debug("Data.__addNode(): parent=%s, tag=%s, value=%s, attr=%s" % (parent, tag, value, attr))
        if value is not None:
            node = self.__createTextNode(parent, tag, value)
        else:
            node = self.__createNode(parent, tag)
        for key, val in attr.iteritems():
            node.setAttribute(key, val)
        return node

    def __serialize(self):
        """ Serialize xml tree to file.
        """
        if ConfigManager().getBoolean('Data', 'DATA_FILE_ENABLE'):
            Logger().trace("Data.serialize()")
            filename = os.path.join(config.HOME_DIR, config.DATA_FILE)
            xmlFile = file(filename % self.__date, 'w')
            self.__doc.writexml(xmlFile, addindent="    ", newl='\n', encoding="utf-8")
            xmlFile.close()

    def createHeader(self, values):
        """ Create the header.
        
        @param values: values to put in the header
        @type values: dict
        """
        Logger().debug("Data.createHeader(): values=%s" % values)
        
        # Shooting
        node = self.__addNode(self.__headerNode, 'shooting')
        self.__addNode(node, 'stabilizationDelay', values['stabilizationDelay'])
        self.__addNode(node, 'overlap', minimum=values['overlap'],
                                        yaw=values['yawRealOverlap'],
                                        pitch=values['pitchRealOverlap'])
        self.__addNode(node, 'cameraOrientation', values['cameraOrientation'])
        
        # Camera
        node = self.__addNode(self.__headerNode, 'camera')
        self.__addNode(node, 'timeValue', values['timeValue'])
        self.__addNode(node, 'nbPicts', values['nbPicts'])
        self.__addNode(node, 'sensor', coef=values['sensorCoef'],
                                       ratio=values['sensorRatio'])
        
        # Lens
        node = self.__addNode(self.__headerNode, 'lens')
        self.__addNode(node, 'focal', values['focal'])
        self.__addNode(node, 'fisheye', values['fisheye'])
        
        # Template
        node = self.__addNode(self.__headerNode, 'template', type=values['template'])
        self.__addNode(node, 'nbPicts', yaw=values['yawNbPicts'],
                                        pitch=values['pitchNbPicts'])

        # Serialize xml file
        self.__serialize()

    def addPicture(self, num, yaw, pitch):
        """ Add a new picture node to shoot node.

        @param num: num of the pict (bracketing)
        @type num: int

        @param yaw: yaw position
        @type yaw: float

        @param pitch: pitch position
        @type pitch: float
        """
        Logger().debug("Data.addPicture(): num=%d, yaw=%.1f, pitch=%.1f" % (num, yaw, pitch))
        node = self.__addNode(self.__shootNode, 'pict', id="%d" % self.__pictId, num="%d" % num)
        self.__pictId += 1
        self.__addNode(node, 'time', time.ctime())
        self.__addNode(node, 'position', yaw="%.1f" % yaw, pitch="%.1f" % pitch)

        # Serialize xml file
        self.__serialize()
