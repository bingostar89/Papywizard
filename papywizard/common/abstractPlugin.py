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

Plugins architecture

Implements
==========

- AbstractPlugin

@author: Frédéric Mantegazza
@copyright: (C) 2007-2009 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

import sys
import os.path

from papywizard.common.loggingServices import Logger
from papywizard.common.orderedDict import OrderedDict

from PyQt4 import QtCore

from papywizard.common.orderedDict import OrderedDict


class AbstractPlugin(QtCore.QObject):
    """ Abstract definition of a plugin.
    """
    capacity = None # in ('yawAxis', 'pitchAxis', 'shutter', analysis', ...)
    name = None

    def __init__(self):
        """ Init the abstract plugin.
        """
        QtCore.QObject.__init__(self)

        # Check capacity validity
        if self.capacity not in ('yawAxis', 'pitchAxis', 'shutter', 'analysis'):
            raise RuntimeError("Unknown plugin capacity (%d)" % self.capacity)

        # Plugin specific init
        self._init()
        #self._loadConfig()

    # Properties
    def __getCapacity():
        """ Return the capacity of the plugin.
        """
        return self.__class__.capacity

    capacity = property(__getCapacity)

    def __getName(self):
        """ Return the name of the plugin.
        """
        return self.__class__.name

    name = property(__getName)

    # Private methods
    def _init(self):
        """ Additional init of the plugin.
        """
        raise NotImplementedError("AbstractPlugin._init() must be overidden")

    def _loadConfig(self):
        """ Load the plugin config.
        """
        raise NotImplementedError("AbstractPlugin._loadConfig() must be overidden")

    def _saveConfig(self):
        """ Save the plugin config.
        """
        raise NotImplementedError("AbstractPlugin._saveConfig() must be overidden")

    # Common interface
    def activate(self):
        """ Activate the plugin.

        The plugin may need to perform some operations when activated.
        """
        raise NotImplementedError("AbstractPlugin.activate() must be overidden")

    # Plugin specific interface
