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
import ConfigParser

from papywizard.common import config
from papywizard.common.loggingServices import Logger
from papywizard.common.helpers import isOdd

if hasattr(sys, "frozen"):
    path = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "papywizard", "common")
else:
    path = os.path.dirname(__file__)


class ConfigManager(object):
    """ ConfigManager.
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
        if ConfigManager.__init:
            action = 'none'

            # Load dist config.
            distConfig = ConfigParser.SafeConfigParser()
            distConfigFile = os.path.join(path, config.CONFIG_FILE)
            if distConfig.read(distConfigFile) == []:
                raise IOError("Can't read configuration file (%s)" % distConfigFile)
            distConfig.set('General', 'CONFIG_VERSION', config.VERSION)

            # Check if user config. exists, or need to be updated/overwriteed
            #distConfigVersion = distConfig.get('General', 'CONFIG_VERSION').split('.')
            distConfigVersion = config.VERSION.split('.')
            userConfig = ConfigParser.SafeConfigParser()
            if userConfig.read(config.USER_CONFIG_FILE) == []:
                action = 'install'
            else:
                userConfigVersion = userConfig.get('General', 'CONFIG_VERSION').split('.')
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
                distConfig.write(file(config.USER_CONFIG_FILE, 'w'))
                userConfig.read(config.USER_CONFIG_FILE)

            elif action == 'overwrite':
                Logger().debug("ConfigManager.__init__(): overwrite user config.")
                distConfig.write(file(config.USER_CONFIG_FILE, 'w'))
                #userConfig = ConfigParser.SafeConfigParser()
                userConfig.read(config.USER_CONFIG_FILE)

            elif action == 'update':
                Logger().debug("ConfigManager.__init__(): update user config.")

                # Remove obsolete sections
                distSections = distConfig.sections()
                for userSection in userConfig.sections():
                    if userSection not in distSections:
                        userConfig.remove_section(userSection)
                        Logger().debug("ConfigManager.__init__(): Removed [%s] section" % userSection)

                # Update all sections
                for distSection in distSections:

                    # Create new sections
                    if not userConfig.has_section(distSection):
                        userConfig.add_section(distSection)
                        Logger().debug("ConfigManager.__init__(): Added [%s] section" % distSection)

                    # Remove obsolete options
                    for option in userConfig.options(distSection):
                        if not distConfig.has_option(distSection, option):
                            userConfig.remove_option(distSection, option)
                            Logger().debug("ConfigManager.__init__(): Removed [%s] %s option" % (distSection, option))

                    # Update the options
                    for option, value in distConfig.items(distSection):
                        if not userConfig.has_option(distSection, option) or \
                        value != userConfig.get(distSection, option) and not distSection.endswith("Preferences"):
                            if isinstance(value, str):
                                value = value.replace("%", "%%")
                            userConfig.set(distSection, option, value)
                            Logger().debug("ConfigManager.__init__(): Updated [%s] %s option with %s" % (distSection, option, value))

                    # Set config. version
                    userConfig.set('General', 'CONFIG_VERSION', "%s" % '.'.join(distConfigVersion))

                # Write user config.
                userConfig.write(file(config.USER_CONFIG_FILE, 'w'))

            elif action == 'none':
                Logger().debug("ConfigManager.__init__(): user config. is up-to-date")

            self.__config = userConfig

            ConfigManager.__init = False

    def save(self):
        """ Save config.

        Config is saved in user directory. Preferences are first
        set back to config.
        """
        self.__config.write(file(config.USER_CONFIG_FILE, 'w'))
        Logger().info("Configuration saved")

    def get(self, section, option):
        """ Get a value.

        @param section: section name to use
        @type section: str

        @param option: option to get value from
        @type option: str
        """
        return self.__config.get(section, option)

    def getInt(self, section, option):
        """ Get a value.

        @param section: section name to use
        @type section: str

        @param option: option to get value from
        @type option: int
        """
        return self.__config.getint(section, option)

    def getFloat(self, section, option):
        """ Get a value.

        @param section: section name to use
        @type section: str

        @param option: option to get value from
        @type option: float
        """
        return self.__config.getfloat(section, option)

    def getBoolean(self, section, option):
        """ Get a value.

        @param section: section name to use
        @type section: str

        @param option: option to get value from
        @type option: bool
        """
        return self.__config.getboolean(section, option)

    def set(self, section, option, value):
        """ Set a value.

        @param section: section name to use
        @type section: str

        @param option: option to set value to
        @type option: str

        @param value: value to set
        @type value: str
        """
        value = value.replace("%", "%%")
        self.__config.set(section, option, value)

    def setInt(self, section, option, value):
        """ Set a value as int.

        @param section: section name to use
        @type section: str

        @param option: option to set value to
        @type option: str

        @param value: value to set
        @type value: int
        """
        self.__config.set(section, option, "%d" % value)

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
        self.__config.set(section, option, ("%(format)s" % {'format': "%%.%df" % prec}) % value)

    def setBoolean(self, section, option, value):
        """ Set a value.

        @param section: section name to use
        @type section: str

        @param option: option to set value to
        @type option: str

        @param value: value to set
        @type value: str
        """
        self.__config.set(section, option, str(value))
