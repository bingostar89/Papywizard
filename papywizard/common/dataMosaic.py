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

 - DataMosaic

XML format
==========

<?xml version="1.0" ?>
<papywizard>
    <header>
        <shooting mode="mosaic">
            <stabilizationDelay>0.5</stabilizationDelay>
        </shooting>
        <mosaic>
            <nbPicts pitch="1" yaw="2"/>
            <overlap minimum="0.25" pitch="1.00" yaw="0.58"/>
            <cameraOrientation>portrait</cameraOrientation>
        </mosaic>
        <camera>
            <timeValue>0.5</timeValue>
            <nbPicts>2</nbPicts>
            <sensor coef="1.6" ratio="3:2"/>
        </camera>
        <lens>
            <focal>17.0</focal>
        </lens>
    </header>
    <shoot>
        <pict id="1" num="1">
            <time>Wed Jun 25 10:37:16 2008</time>
            <position pitch="0.0" yaw="0.0"/>
        </pict>
        <pict id="2" num="2">
            <time>Wed Jun 25 10:37:17 2008</time>
            <position pitch="0.0" yaw="0.0"/>
        </pict>
        <pict id="3" num="1">
            <time>Wed Jun 25 10:37:20 2008</time>
            <position pitch="0.0" yaw="20.1"/>
        </pict>
        <pict id="4" num="2">
            <time>Wed Jun 25 10:37:21 2008</time>
            <position pitch="0.0" yaw="20.1"/>
        </pict>
    </shoot>
</papywizard>

@author: Frédéric Mantegazza
@copyright: (C) 2007-2008 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id: data.py 442 2008-07-14 16:18:16Z fma $"

from papywizard.common.loggingServices import Logger
from papywizard.common.data import Data


class DataMosaic(Data):
    """ Manage the data.
    """
    def __init__(self):
        super(DataMosaic, self).__init__()

    def createHeader(self, values):
        Logger().debug("DataMosaic.createHeader(): values=%s" % values)
        
        # Shooting
        node = self._addNode(self._headerNode, 'shooting', mode='mosaic')
        self._addNode(node, 'stabilizationDelay', values['stabilizationDelay'])
        
        # Mosaic
        node = self._addNode(self._headerNode, 'mosaic')
        self._addNode(node, 'nbPicts', yaw=values['yawNbPicts'],
                                       pitch=values['pitchNbPicts'])
        self._addNode(node, 'overlap', minimum=values['overlap'],
                                       yaw=values['yawRealOverlap'],
                                       pitch=values['pitchRealOverlap'])
        self._addNode(node, 'cameraOrientation', values['cameraOrientation'])
        
        # Camera
        node = self._addNode(self._headerNode, 'camera')
        self._addNode(node, 'timeValue', values['timeValue'])
        self._addNode(node, 'nbPicts', values['nbPicts'])
        self._addNode(node, 'sensor', coef=values['sensorCoef'],
                                      ratio=values['sensorRatio'])

        # Lens
        node = self._addNode(self._headerNode, 'lens')
        self._addNode(node, 'focal', values['focal'])

        # Serialize xml file
        self._serialize()
