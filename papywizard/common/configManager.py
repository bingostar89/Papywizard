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

Configuration

Implements
==========

- ConfigManager

@author: Frédéric Mantegazza
@copyright: (C) 2007-2009 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

import sys
import os.path
import shutil
import sets

from PyQt4 import QtCore

from papywizard.common import config
from papywizard.common.loggingServices import Logger
from papywizard.common.helpers import isOdd

if hasattr(sys, "frozen"):
    path = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "papywizard", "common")
else:
    path = os.path.dirname(__file__)
configManager = None


class ConfigManagerObject(QtCore.QObject):
    """ Configuration manager.
    """
    def __init__(self):
        """ Init the object.
        """
        self.__config = None
        self.__action = 'none'
        self.__saved = False

    def load(self):
        """ Load configuration.
        """

        #Load dist config.
        distConfigFile = os.path.join(path, config.CONFIG_FILE)
        distConfig = QtCore.QSettings(distConfigFile, QtCore.QSettings.IniFormat)
        if not distConfig.contains('CONFIG_VERSION'):
            raise IOError("Can't read configuration file (%s)" % distConfigFile)

        # Check if user config. exists, or need to be updated/overwritten
        distConfigVersion = config.VERSION.split('.')
        userConfig = QtCore.QSettings(config.USER_CONFIG_FILE, QtCore.QSettings.IniFormat)
        if not userConfig.contains('CONFIG_VERSION'):
            self.__action = 'install'
        else:
            userConfigVersion = unicode(userConfig.value('CONFIG_VERSION').toString()).split('.')
            Logger().debug("ConfigManager.__init__(): versions: dist=%s, user=%s" % (distConfigVersion, userConfigVersion))

            # Old versioning system
            if len(userConfigVersion) < 2:
                self.__action = 'overwrite'

            # Versions differ
            elif distConfigVersion != userConfigVersion:

                # Dev. version over any version
                if isOdd(int(distConfigVersion[1])):
                    self.__action = 'overwrite'

                # Stable version...
                elif not isOdd(int(distConfigVersion[1])):

                    # ...over dev. version
                    if isOdd(int(userConfigVersion[1])):
                        self.__action = 'overwrite'

                    # ...over stable version
                    else:
                        self.__action = 'update'

        if self.__action == 'install':
            Logger().debug("ConfigManager.__init__(): install user config.")
            shutil.copy(distConfigFile, config.USER_CONFIG_FILE)

            # Set config. version
            userConfig.setValue('CONFIG_VERSION', QtCore.QVariant("%s" % '.'.join(distConfigVersion)))

            # Write user config.
            userConfig.sync()

        elif self.__action == 'overwrite':
            Logger().debug("ConfigManager.__init__(): overwrite user config.")
            shutil.copy(distConfigFile, config.USER_CONFIG_FILE)

            # Set config. version
            userConfig.setValue('CONFIG_VERSION', QtCore.QVariant("%s" % '.'.join(distConfigVersion)))

            # Write user config.
            userConfig.sync()

        elif self.__action == 'update':
            Logger().debug("ConfigManager.__init__(): update user config.")
            keys = sets.Set(userConfig.allKeys())
            keys.update(distConfig.allKeys())
            for key in keys:
                if distConfig.contains(key):
                    if not userConfig.contains(key):
                        value = distConfig.value(key)
                        userConfig.setValue(key, value)
                        Logger().debug("ConfigManager.__init__(): added %s key with %s" % (key, value.toString()))
                else:
                    userConfig.remove(key)
                    Logger().debug("ConfigManager.__init__(): removed %s key" % key)

            # Set config. version
            userConfig.setValue('CONFIG_VERSION', QtCore.QVariant("%s" % '.'.join(distConfigVersion)))

            # Write user config.
            userConfig.sync()

        elif self.__action == 'none':
            Logger().debug("ConfigManager.__init__(): user config. is up-to-date")

        self.__config = userConfig

    def save(self):
        """ Save config.

        Config is saved in user directory. Preferences are first
        set back to config.
        """
        self.__config.sync()
        self.__saved = True
        Logger().debug("Configuration saved")

    def isConfigured(self):
        """ Check if configuration has been set by user.
        """
        if self.__saved or self.__action in ('none', 'update'):
            return True
        else:
            return False

    def contains(self, key):
        """ Check if the config contains the given section/option.

        @param key: config key
        @type key: str
        """
        return self.__config.contains(key)

    def _check(self, key):
        """ Check if the config contains the given section/option.

        @param key: config key
        @type key: str
        """
        if not self.contains(key):
            raise KeyError("ConfigManager does not contain key '%s'" % key)

    def get(self, key):
        """ Get a str value.

        @param key: config key
        @type key: str
        """
        self._check(key)
        return unicode(self.__config.value(key).toString())

    def getInt(self, key):
        """ Get an int value.

        @param key: config key
        @type key: str
        """
        self._check(key)
        value, flag = self.__config.value(key).toInt()
        if flag:
            return value
        else:
            raise ValueError("ConfigManager can't get key '%s' as int" % key)

    def getFloat(self, key):
        """ Get a float value.

        @param key: config key
        @type key: str
        """
        self._check(key)
        value, flag = self.__config.value(key).toDouble()
        if flag:
            return value
        else:
            raise ValueError("ConfigManager can't get key '%s' as float" % key)

    def getBoolean(self, key):
        """ Get a boolean value.

        @param key: config key
        @type key: str
        """
        self._check(key)
        return self.__config.value(key).toBool()

    def set(self, key, value):
        """ Set a value as str.

        @param key: config key
        @type key: str

        @param value: value to set
        @type value: str
        """
        self.__config.setValue(key, QtCore.QVariant(value))
        self.__saved = False

    def setInt(self, key, value):
        """ Set a value as int.

        @param key: config key
        @type key: str

        @param value: value to set
        @type value: int
        """
        self.__config.setValue(key, QtCore.QVariant(value))
        self.__saved = False

    def setFloat(self, key, value, prec):
        """ Set a value as float.

        @param key: config key
        @type key: str

        @param value: value to set
        @type value: float

        @param prec: precision
        @type prec: int
        """
        #value = ("%(format)s" % {'format': "%%.%df" % prec}) % value
        self.__config.setValue(key, QtCore.QVariant(value))
        self.__saved = False

    def setBoolean(self, key, value):
        """ Set a value as boolean.

        @param key: config key
        @type key: str

        @param value: value to set
        @type value: str
        """
        self.__config.setValue(key, QtCore.QVariant(value))
        self.__saved = False


# ConfigManager factory
def ConfigManager():
    global configManager
    if configManager is None:
        configManager = ConfigManagerObject()

    return configManager
