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

from PyQt4 import QtCore

from papywizard.common.orderedDict import OrderedDict
from papywizard.common.loggingServices import Logger
from papywizard.common.configManager import ConfigManager


class AbstractPlugin(object): #(QtCore.QObject):
    """ Abstract definition of a plugin.
    """
    def __init__(self, capacity, name):
        """ Init the abstract plugin.

        @param capacity: capacity of the plugin, in ('yawAxis', 'pitchAxis', 'shutter')
        @type capacity: str

        @param name: name of the plugin
        @type name: str
        """
        #QtCore.QObject.__init__(self)

        # Plugin specific init
        self._capacity = capacity
        self._name = name
        self._init()
        self._config = {}
        self._defineConfig()
        self._loadConfig()

    # Properties
    def __getCapacity(self):
        """ Return the capacity of the plugin.
        """
        return self._capacity

    capacity = property(__getCapacity, "Plugin capacity")

    def __getName(self):
        """ Return the name of the plugin.
        """
        return self._name

    name = property(__getName, "Plugin name")

    def _init(self):
        """ Additional init of the plugin.
        """
        raise NotImplementedError("AbstractPlugin._init() must be overloaded")

    def _defineConfig(self):
        """ Define the config for the plugin.

        Config keys defined here must match the ones used in the controller.
        """
        raise NotImplementedError("AbstractPlugin._defineConfig() must be overloaded")

    def _addConfigKey(self, attr, key, default):
        """ Add a new config key.

        @param attr: attribute to add to the plugin object
        @type attr: str

        @param key: key to add
        @type key: str

        @param default: default value for the given key
        @type default:
        """
        #self.__dict__[attr] = default # Find a way to bind to _config[key]. Use property?
        self._config[key] = default

    def _loadConfig(self):
        """ Load the plugin config.
        """
        Logger().trace("AbstractPlugin._loadConfig()")
        for key, defaultValue in self._config.iteritems():
            configKey = "%s_%s/%s" % (self.name, self.capacity, key)
            #Logger().debug("AbstractPlugin._loadConfig(): key=%s" % configKey)
            if ConfigManager().contains(configKey):
                if isinstance(defaultValue, bool):
                    self._config[key] = ConfigManager().getBoolean(configKey)
                elif isinstance(defaultValue, str):
                    self._config[key] = ConfigManager().get(configKey)
                elif isinstance(defaultValue, int):
                    self._config[key] = ConfigManager().getInt(configKey)
                elif isinstance(defaultValue, float):
                    self._config[key] = ConfigManager().getFloat(configKey)
        #Logger().debug("AbstractPlugin._loadConfig(): config=%s" % self._config)

    def _saveConfig(self):
        """ Save the plugin config.
        """
        Logger().trace("AbstractPlugin._saveConfig()")
        for key, value in self._config.iteritems():
            group = "%s_%s" % (self.name, self.capacity)
            #Logger().debug("AbstractPlugin._saveConfig(): %s/%s=%s" % (group, key, value))
            ConfigManager().set('%s/%s' % (group, key), value)
        ConfigManager().save()

    def activate(self):
        """ Activate the plugin.

        The plugin may need to perform some operations when activated,
        like starting a thread or so.
        """
        raise NotImplementedError("AbstractPlugin.activate() must be overloaded")

    def deactivate(self):
        """ Shutdown the plugin.

        The plugin may need to perform some operations when desactivated.
        """
        raise NotImplementedError("AbstractPlugin.deactivate() must be overloaded")

    def establishConnection(self):
        """ Establish the connexion.
        """
        raise NotImplementedError("AbstractPlugin.establishConnection() must be overloaded")

    def stopConnection(self):
        """ Stop the connexion.
        """
        raise NotImplementedError("AbstractPlugin.stopConnection() must be overloaded")


    def init(self):
        """ Init the plugin.

        This method is called after the connection is established.
        Can be used to make some low-level init operations.
        """
        raise NotImplementedError("AbstractPlugin.init() must be overloaded")

    def shutdown(self):
        """ Shutdown the plugin.

        This method is called before the connection is stopped.
        Can be used to make some low-level shotdown operations.
        """
        raise NotImplementedError("AbstractPlugin.shutdown() must be overloaded")