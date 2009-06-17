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

Plugin architecture

Implements
==========

- PluginManagerObject

@author: Frédéric Mantegazza
@copyright: (C) 2007-2009 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

import sys
import os
import os.path
import sets
import imp

from PyQt4 import QtCore

from papywizard.common import config
from papywizard.common.loggingServices import Logger


if hasattr(sys, "frozen"):
    path = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "papywizard", "common")
else:
    path = os.path.dirname(__file__)
pluginManager = None


class PluginManagerObject(QtCore.QObject):
    """ Plugins manager object.
    """
    def __init__(self):
        """ Init the object.
        """
        self.__plugins = sets.Set()

    def load(self):
        """
        """

        # Load default plugins
        #Logger().info("Loading default plugins...")
        #pluginDir = os.path.join(path, os.path.pardir, "plugins")
        #self.parseDir(pluginDir)

        # Load user plugins
        Logger().info("Loading user plugins...")
        if os.path.isdir(config.USER_PLUGINS_DIR):
            self.parseDir(config.USER_PLUGINS_DIR)

    def parseDir(self, pluginDir):
        """ Load plugins from given dir.

        @param pluginDir: dir where to search plugins
        @type pluginDir: str
        """
        Logger().debug("PluginManager.register(): parsing '%s' dir..." % pluginDir)
        for entry in os.listdir(pluginDir):
            #Logger().debug("PluginManager.register(): entry=%s" % entry)
            if os.path.isfile(os.path.join(pluginDir, entry)):
                moduleName, ext = os.path.splitext(entry)
                if ext == '.py' and moduleName != "__init__":
                    file, pathname, description = imp.find_module(moduleName, [pluginDir])
                    Logger().debug("PluginManager.register(): found '%s' module" % moduleName)
                    try:
                        module = imp.load_module('module', file, pathname, description)
                        module.register()
                    except AttributeError:
                        Logger().exception("PluginManager.register()", debug=True)
                        Logger().warning("Plugin module '%s' does not have a register function" % pathname)
                    finally:
                        file.close()

    def register(self, pluginClass, pluginControllerClass):
        """ Register a new plugin.

        @param pluginClass: class of the plugin model
        @type pluginClass: {AbstractPlugin<common.abstractPlugin>}

        @param pluginControllerClass: class of the plugin controller
        @type pluginControllerClass: {AbstractPluginController<controller.abstractPluginController>}
        """
        model = pluginClass()
        self.__plugins.add((model, pluginControllerClass))
        Logger().debug("PluginManager.register(): added '%s' plugin with capacity '%s'" % (model.name, model.capacity))

    def getList(self, capacity):
        """ Return the plugins with the given capacity.

        @param capacity: capacity
        @type capacity: str

        @return: plugins with given capacity (model + controller)
        @rtype: list of tuple
        """
        plugins = []
        for plugin in self.__plugins:
            if plugin[0].capacity == capacity:
                plugins.append(plugin)
        return plugins

    def get(self, capacity, name):
        """ Return the plugin 
        """
        for model, controllerClass in self.getList(capacity):
            if model.capacity == capacity and model.name == name:
                return model, controllerClass
        raise ValueError("No plugin named '%s' with capacity '%s'" % (name, capacity))


# ConfigManager factory
def PluginManager():
    global pluginManager
    if pluginManager is None:
        pluginManager = PluginManagerObject()

    return pluginManager
