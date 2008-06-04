# -*- coding: iso-8859-1 -*-

""" Panohead remote control.

Configuration.

Implements class:

- ConfigManager

@author: Frédéric Mantegazza
@copyright: 2008
@license: CeCILL
@todo: 
"""

__revision__ = "$Id$"

import os.path
import ConfigParser

from papywizard.common import config
from papywizard.common.loggingServices import Logger


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
        
        @todo: update user config. from global config. instead of overwriting
        """
        if ConfigManager.__init:
            globalConfig = ConfigParser.SafeConfigParser()
            globalConfig.read(config.GLOBAL_CONFIG_FILE)
            globalConfigVersion = globalConfig.get('General', 'VERSION')
            userConfig = ConfigParser.SafeConfigParser()
            
            # Check if user config. exists
            if userConfig.read(config.USER_CONFIG_FILE) == []:
                Logger().warning("User config. does not exist; copying from global config.")
                globalConfig.write(file(config.USER_CONFIG_FILE, 'w'))
                userConfig.read(config.USER_CONFIG_FILE)

            # Check if user config. needs to be updated
            userConfigVersion = userConfig.get('General', 'VERSION')
            if userConfigVersion != globalConfigVersion:
                Logger().warning("User config. has wrong version.; updating from global config.")
                
                # Remove obsolete sections
                globalSections = globalConfig.sections()
                for userSection in userConfig.sections():
                    if userSection not in globalSections:
                        userConfig.remove_section()

                # Update all sections
                for globalSection in globalSections:

                    # If the section does not yet exist, we create it
                    if not userConfig.has_section(globalSection):
                        userConfig.add_section(globalSection)

                    # Remove obsolete options
                    for option in userConfig.options(globalSection):
                        if not globalConfig.has_option(globalSection, option):
                            userConfig.remove_option(globalSection, option)

                    # Update the options
                    for option, value in globalConfig.items(globalSection):
                        userConfig.set(globalSection, option, value)

            self.__config = userConfig

            ConfigManager.__init = False

    def save(self):
        """ Save config.
        
        Config is saved in user config. directory
        """
        self.__config.write(file(config.USER_CONFIG_FILE, 'w'))

    def getPreferences(self):
        """ Get the current preferences.
        
        Preferences are configs related to the model.
        
        @return: current preferences
        @rtype: dict
        """
        return dict(self.__config.items('Preferences'))

    def getDefaultPreferences(self):
        """ Get the default preferences.
        
        Preferences are configs related to the model.
        
        @return: default preferences
        @rtype: dict
        """
        return dict(self.__config.items('DefaultPreferences'))

    def get(self, section, option):
        """ Get a value.
        
        @param section: section name to use
        @type section: str
        
        @param option: option to get value from
        @type option: str
        """
        return self.__config.get(section, option)
        
    def set(self, section, option, value):
        """ Set a value.
        
        @param section: section name to use
        @type section: str
        
        @param option: option to set value to
        @type option: str
        
        @param value: value to set
        @type value: str
        """
        self.__config.set(section, option, value)
        