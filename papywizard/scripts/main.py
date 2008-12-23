#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Panohead remote control.

License
=======

 - B{papywizard} (U{http://trac.gbiloba.org/papywizard}) is Copyright:
  - (C) 2007-2008 FrÃ©dÃ©ric Mantegazza

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

Main script

@author: FrÃ©dÃ©ric Mantegazza
@copyright: (C) 2007-2008 FrÃ©dÃ©ric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

import sys
import os.path
import traceback
import StringIO
import locale
import gettext

import pygtk
pygtk.require("2.0")
import gtk
import gtk.glade
import gobject

from papywizard.common import config
from papywizard.common.configManager import ConfigManager
from papywizard.common.loggingServices import Logger
from papywizard.common.serializer import Serializer
from papywizard.common.exception import HardwareError
from papywizard.common.publisher import Publisher
from papywizard.hardware.head import Head, HeadSimulation
from papywizard.model.shooting import Shooting
from papywizard.controller.messageController import ExceptionMessageController
from papywizard.controller.mainController import MainController
from papywizard.controller.spy import Spy
from papywizard.view.logBuffer import LogBuffer

DOMAIN = "papywizard"
LANGS = ('en_US', 'fr_FR', 'pl_PL', 'de_DE', 'es_ES', 'nl_NL', 'it_IT')

_ = lambda a: a


class BlackHole:
    """ Dummy class for stderr redirection.
    """
    softspace = 0

    def write(self, text):
        pass


class Papywizard(object):
    """ Main application class.
    """
    def __init__(self):
        """ Init the application.
        """
        self.__gtkLogStream = LogBuffer()
        Logger().addStreamHandler(self.__gtkLogStream)
        #Logger().setLevel(ConfigManager().get('Preferences', 'LOGGER_LEVEL'))

    def init(self):
        """ Init the application.
        """
        Logger().info("Starting Papywizard...")

        # Gtk threads
        gtk.gdk.threads_init()
        gtk.gdk.threads_enter()

        # Gtk style
        gtk.rc_parse(config.USER_GTKRC_FILE)

        # Create hardware and model
        head = Head()
        headSimulation = HeadSimulation()
        self.__model = Shooting(head, headSimulation)

        # Create spy thread
        Spy(self.__model, config.SPY_FAST_REFRESH)
        #Spy().start()

        # Create publisher thread
        self.__publisher = Publisher()

        # Create serializer, for async events
        self.__serializer = Serializer()

        # Create main controller
        controller = MainController(self.__model, self.__serializer, self.__gtkLogStream)

    def weave(str):
        """ Weave stuffs.
        """
        try:
            from papywizard.common.loggingAspects import logMethods
            logMethods(Head)
            logMethods(HeadSimulation)
            logMethods(MainController)
        except ImportError:
            Logger().warning("Lobilab aspects module must be installed to use logging aspects")

    def l10n(self):
        """ i10n stuff.

        Thanks to Mark Mruss from http://www.learningpython.com

        @todo: even if launch locally, locales are first searched in system dir
        """
        langs = []

        # Check the default locale
        lc, encoding = locale.getdefaultlocale()
        Logger().debug("Papywizard.l10n(): default locale=%s" % lc)
        if lc:

            # If we have a default, it's the first in the list
            langs.append(lc)

        # Now lets get all of the supported languages on the system
        language = os.environ.get('LANGUAGE', None)
        Logger().debug("Papywizard.l10n(): LANGUAGE=%s" % language)
        if language is not None:

            # Language comes back something like en_CA:en_US:en_GB:en
            # on linux systems, on Win32 it's nothing, so we need to
            # split it up into a list
            for lang in language.split(":"):
                if lang not in langs:
                    langs.append(lang)

        # Now add on to the back of the list the translations that we
        # know that we have, our defaults
        for lang in LANGS:
            if lang not in langs:
                langs.append(lang)

        Logger().debug("Papywizard.l10n(): langs=%s" % langs)

        # Get the locale dir
        # First check in windows install
        if hasattr(sys, "frozen"):
            localeDir = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "share", "locale")
        else:

            # Search in current dir
            localeDir = os.path.realpath(os.path.dirname(sys.argv[0]))
            localeDir = os.path.join(localeDir, "locale")
            localeFile = gettext.find(DOMAIN, localeDir, languages=langs)
            if localeFile is None:

                # Search in default system dirs
                localeFile = gettext.find(DOMAIN, languages=langs)
                if localeFile is None:
                    localeFile = gettext.find(DOMAIN, "/usr/local/share/locale", languages=langs)

                if localeFile is not None:
                    localeDir = os.path.join(os.path.dirname(localeFile), os.pardir, os.pardir)
        Logger().debug("Papywizard.l10n(): localeDir=%s" % localeDir)

        #gettext.bindtextdomain(DOMAIN, localeDir)
        #gettext.textdomain(DOMAIN)
        gtk.glade.bindtextdomain(DOMAIN, localeDir)
        gtk.glade.textdomain(DOMAIN)

        # Get the Translation object
        try:
            lang = gettext.translation(DOMAIN, localeDir, languages=langs)
        except IOError:
            Logger().warning("Can't find i18n file")
            lang = gettext.translation(DOMAIN, localeDir, languages=langs, fallback=True)

        # Install the language, map _()
        _ = lang.gettext
        lang.install()

    def run(self):
        """ Run the appliction.
        """
        gobject.timeout_add(config.SERIALIZER_REFRESH , self.__serializer.processWork)
        Spy().start()
        if config.PUBLISHER_ENABLE:
            self.__publisher.start()
        Logger().setLevel(ConfigManager().get('Preferences', 'LOGGER_LEVEL'))
        gtk.main()

    def shutdown(self):
        """ Shutdown the application.
        """
        Spy().stop()
        Spy().join()
        del self.__publisher
        self.__model.shutdown()

        # Gtk threads
        gtk.gdk.threads_leave()

        Logger().info("Papywizard stopped")


def main():
    if hasattr(sys, "frozen"):
        sys.stderr = BlackHole()
        Logger(defaultStream=False)
    else:
        Logger()

    try:
        app = Papywizard()
        app.l10n()
        app.init()
        #app.weave()
        try:
            app.run()
        except KeyboardInterrupt:
            pass
        app.shutdown()

    except Exception, msg:
        Logger().exception("main()")
        controller = ExceptionMessageController("main()")
        controller.run()


if __name__ == "__main__":
    main()
