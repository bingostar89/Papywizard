# -*- coding: iso-8859-1 -*-

""" Panohead remote control.

Data management.

Implements class:

- Data

Data is used during shooting, and generate a xml file containing
usefull information for stitchers. AutoPano Pro takes advantage of
such datas, for example to correctly set unlinked pictures at their
correct place (sky pictures without any details are often unlinked).

<?xml version="1.0" encoding="UTF-8"?>
<papywizard>
    <header>
        <focal>17.0</focal>
        <fisheye>True</fisheye>
        <sensorCoef>1.6</sensorCoef>
        <sensorRatio>3:2</sensorRatio>
        <cameraOrientation>portrait</cameraOrientation>
        <nbPicts>2</nbPicts>                             <!-- bracketing -->
        <relYawOverlap>0.54</realYawOverlap>             <!-- real overlaps -->
        <realPitchOverlap>0.32</realPitchOverlap>
        <template type="mosaic" rows="3" columns="4" />
    </header>
    <shoot>
        ...
        <image id="7" pict="1">
            <time>Mon Dec 31 00:52:18 CET 2007</time>
            <yaw>-32.5</yaw>
            <pitch>12.3</pitch>
        </image>
        <image id="8" pict="2">
            <time>Mon Dec 31 00:52:22 CET 2007</time>
            <yaw>-32.5</yaw>
            <pitch>12.3</pitch>
        </image>
        ...
    </shoot>
<papywizard>

@author: Frederic Mantegazza
@copyright: 2007
@license: CeCILL
@todo:
"""

__revision__ = "$Id$"

import time
import xml.dom.minidom

from common import config
from common.loggingServices import Logger


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

        self.__imageId = 1

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

    def __serialize(self):
        """ Serialize xml tree to file.
        """
        Logger().trace("Data.serialize()")
        xmlFile = file(config.DATA_FILE % self.__date, 'w')
        self.__doc.writexml(xmlFile, addindent='    ', newl='\n')
        xmlFile.close()

    def addHeaderNode(self, tag, value=None, **attr):
        """ Add a header node.
        
        @param tag: tag of the node
        @type tag: str
        
        @param value: value of the node
        @type value: str
        
        @param attr: optionnal attributes
        @type attr: dict
        """
        Logger().debug("Data.addHeaderNode(): tag=%s, value=%s, attr=%s" % (tag, value, attr))
        if value is not None:
            headerNode = self.__createTextNode(self.__headerNode, tag, value)
        else:
            headerNode = self.__createNode(self.__headerNode, tag)
        for key, val in attr.iteritems():
            headerNode.setAttribute(key, val)
        
        # Serialize xml file
        self.__serialize()

    def addImageNode(self, pict, yaw, pitch):
        """ Add a new image node to shoot node.
        
        @param pict: num of the pict (bracketing)
        @type pict: int
        
        @param yaw: yaw position
        @type yaw: float
        
        @param pitch: pitch position
        @type pitch: float
        """
        Logger().debug("Data.addImageNode(): pict=%d, yaw=%.1f, pitch=%.1f" % (pict, yaw, pitch))
        imageNode = self.__createNode(self.__shootNode, 'image')
        imageNode.setAttribute('id', "%d" % self.__imageId)
        self.__imageId += 1
        imageNode.setAttribute('pict', "%d" % pict)
        self.__shootNode.appendChild(imageNode)
        self.__createTextNode(imageNode, 'time', time.ctime())
        self.__createTextNode(imageNode, 'yaw', "%.1f" % yaw)
        self.__createTextNode(imageNode, 'pitch', "%.1f" % pitch)
        
        # Serialize xml file
        self.__serialize()
