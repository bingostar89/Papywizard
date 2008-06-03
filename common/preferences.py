# -*- coding: iso-8859-1 -*-

""" Panohead remote control.

misc classes.

Implements class:

- Preferences

@author: Frederic Mantegazza
@copyright: 2007
@license: CeCILL
@todo:
"""

__revision__ = "$Id$"

import shelve

from papywizard.common import config
from papywizard.common.loggingServices import Logger


class Preferences(object):
    """ Manage the preferences.

    Preferences is a Borg.
    """
    __state = {}
    __init = True

    def __new__(cls, *args, **kwds):
        """ Create the object.
        """
        self = object.__new__(cls, *args, **kwds)
        self.__dict__ = cls.__state
        return self

    def __init__(self):
        """ Init object.
        """
        if Preferences.__init:
            self.__prefs = shelve.open(config.CONFIG_FILE, writeback=True)
            Logger().debug("Preferences.__init__(): __prefs=%s" % self.__prefs)
            if not self.__prefs:
                Logger().debug("Preferences.__init__(): set default values")
                self.__prefs.update(config.DEFAULT_PREFS)
                self.__prefs.sync()

            Preferences.__init = False

    def load(self):
        """ Get prefs.

        @return: preferences
        @rtype: dict
        """
        return self.__prefs

    def save(self):
        """ Sync prefs to disk.
        """
        Logger().debug("Preferences.save(): __prefs=%s" % self.__prefs)
        self.__prefs.sync()
