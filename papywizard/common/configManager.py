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

path = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "papywizard", "common")
configManager = None


class ConfigManagerObject(QtCore.QObject):
    """ Configuration manager.
    """
    def __init__(self):
        """ Init the object.
        """
        action = 'none'

        # Load dist config.
        distConfigFile = os.path.join(path, config.CONFIG_FILE)
        print path
        distConfig = QtCore.QSettings(distConfigFile, QtCore.QSettings.IniFormat)
        if not distConfig.contains('CONFIG_VERSION'):
            raise IOError("Can't read configuration file (%s)" % distConfigFile)

        # Check if user config. exists, or need to be updated/overwritten
        distConfigVersion = config.VERSION.split('.')
        userConfig = QtCore.QSettings(config.USER_CONFIG_FILE, QtCore.QSettings.IniFormat)
        if not userConfig.contains('CONFIG_VERSION'):
            action = 'install'
        else:
            userConfigVersion = unicode(userConfig.value('CONFIG_VERSION').toString()).split('.')
            Logger().debug("ConfigManager.__init__(): versions: dist=%s, user=%s" % (distConfigVersion, userConfigVersion))

            # Old versioning system
            if len(userConfigVersion) < 2:
                action = 'overwrite'

            # Versions differ
            elif distConfigVersion != userConfigVersion:

                # Dev. version over any version
                if isOdd(int(distConfigVersion[1])):
                    action = 'overwrite'

                # Stable version...
                elif not isOdd(int(distConfigVersion[1])):

                    # ...over dev. version
                    if isOdd(int(userConfigVersion[1])):
                        action = 'overwrite'

                    # ...over stable version
                    else:
                        action = 'update'

        if action == 'install':
            Logger().debug("ConfigManager.__init__(): install user config.")
            shutil.copy(distConfigFile, config.USER_CONFIG_FILE)

            # Set config. version
            userConfig.setValue('CONFIG_VERSION', QtCore.QVariant("%s" % '.'.join(distConfigVersion)))

            # Write user config.
            userConfig.sync()

        elif action == 'overwrite':
            Logger().debug("ConfigManager.__init__(): overwrite user config.")
            shutil.copy(distConfigFile, config.USER_CONFIG_FILE)

            # Set config. version
            userConfig.setValue('CONFIG_VERSION', QtCore.QVariant("%s" % '.'.join(distConfigVersion)))

            # Write user config.
            userConfig.sync()

        elif action == 'update':
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

        elif action == 'none':
            Logger().debug("ConfigManager.__init__(): user config. is up-to-date")

        self.__config = userConfig

    def save(self):
        """ Save config.

        Config is saved in user directory. Preferences are first
        set back to config.
        """
        self.__config.sync()
        Logger().info("Configuration saved")

    def get(self, section, option):
        """ Get a value.

        @param section: section name to use
        @type section: str

        @param option: option to get value from
        @type option: str
        """
        if section == 'General':
            key = option
        else:
            key = '%s/%s' % (section, option)
        return unicode(self.__config.value(key).toString())

    def getInt(self, section, option):
        """ Get a value.

        @param section: section name to use
        @type section: str

        @param option: option to get value from
        @type option: int
        """
        if section == 'General':
            key = option
        else:
            key = '%s/%s' % (section, option)
        value, flag = self.__config.value(key).toInt()
        if flag:
            return value
        else:
            raise ValueError("ConfigManager.getInt(): can't get %s key as int" % key)

    def getFloat(self, section, option):
        """ Get a value.

        @param section: section name to use
        @type section: str

        @param option: option to get value from
        @type option: float
        """
        if section == 'General':
            key = option
        else:
            key = '%s/%s' % (section, option)
        value, flag = self.__config.value(key).toDouble()
        if flag:
            return value
        else:
            raise ValueError("ConfigManager.getInt(): can't get %s key as float" % key)

    def getBoolean(self, section, option):
        """ Get a value.

        @param section: section name to use
        @type section: str

        @param option: option to get value from
        @type option: bool
        """
        if section == 'General':
            key = option
        else:
            key = '%s/%s' % (section, option)
        return self.__config.value(key).toBool()

    def set(self, section, option, value):
        """ Set a value.

        @param section: section name to use
        @type section: str

        @param option: option to set value to
        @type option: str

        @param value: value to set
        @type value: str
        """
        if section == 'General':
            key = option
        else:
            key = '%s/%s' % (section, option)
        self.__config.setValue(key, QtCore.QVariant(value))

    def setInt(self, section, option, value):
        """ Set a value as int.

        @param section: section name to use
        @type section: str

        @param option: option to set value to
        @type option: str

        @param value: value to set
        @type value: int
        """
        if section == 'General':
            key = option
        else:
            key = '%s/%s' % (section, option)
        self.__config.setValue(key, QtCore.QVariant(value))

    def setFloat(self, section, option, value, prec):
        """ Set a value as float.

        @param section: section name to use
        @type section: str

        @param option: option to set value to
        @type option: str

        @param value: value to set
        @type value: float

        @param prec: precision
        @type prec: int
        """
        if section == 'General':
            key = option
        else:
            key = '%s/%s' % (section, option)
        self.__config.setValue(key, QtCore.QVariant(value))

    def setBoolean(self, section, option, value):
        """ Set a value.

        @param section: section name to use
        @type section: str

        @param option: option to set value to
        @type option: str

        @param value: value to set
        @type value: str
        """
        if section == 'General':
            key = option
        else:
            key = '%s/%s' % (section, option)
        self.__config.setValue(key, QtCore.QVariant(value))


# ConfigManager factory
def ConfigManager():
    global configManager
    if configManager is None:
        configManager = ConfigManagerObject()

    return configManager
