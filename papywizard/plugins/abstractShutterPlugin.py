# -*- coding: utf-8 -*-

""" Panohead remote control.

License
=======

 - B{Papywizard} (U{http://www.papywizard.org}) is Copyright:
  - (C) 2007-2011 Frédéric Mantegazza

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

Plugin

Implements
==========

- AbstractShutterPlugin

@author: Frédéric Mantegazza
@copyright: (C) 2007-2011 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

from papywizard.plugins.abstractPlugin import AbstractPlugin


class AbstractShutterPlugin(AbstractPlugin):
    """ Abstract class for shutter plugins.
    """
    def _getTimeValue(self):
        """ Get the time value parameter.

        If this parameter is not relevant in the plugin, return -1.
        This parameter is only used in the xml data file header.

        @return: time value parameter
        @rtype: int
        """
        raise NotImplementedError("AbstractShutterPlugin._getTimeValue() must be overloaded")

    def __getTimeValue(self):
        return self._getTimeValue()

    timeValue = property(__getTimeValue)

    def _getMirrorLockup(self):
        """ Get the mirror lockup flag.

        If this parameter is not relevant in the plugin, return False.

        @return: mirror lockup flag
        @rtype: bool
        """
        raise NotImplementedError("AbstractShutterPlugin._getMirrorLockup() must be overloaded")

    def __getMirrorLockup(self):
        return self._getMirrorLockup()

    mirrorLockup = property(__getMirrorLockup)

    def _getBracketingNbPicts(self):
        """ Return the number of bracketed pictures.

        This parameter must be at least >= 1. If it is the responsability of
        the plugin to determine this value, return 1 here. The drawbackup is
        that Papywizard won't be able to set the correct number of bracketed
        pictures in the xml data file.

        This need to be fixed in future releases.

        @return: number of bracketed pictures
        @rtype: int
        """
        raise NotImplementedError("AbstractShutterPlugin._getBracketingNbPicts() must be overloaded")

    def __getBracketingNbPicts(self):
        return self._getBracketingNbPicts()

    bracketingNbPicts = property(__getBracketingNbPicts)

    def lockupMirror(self):
        """ Lockup the mirror.

        @return: error code (0 for OK)
        @rtype: int
        """
        raise NotImplementedError("AbstractShutterPlugin.lockupMirror() must be overloaded")

    def shoot(self, bracketNumber):
        """ Shoot.

        @param bracketNumber: num. of the current bracketed picture
        @type bracketNumber: int

        @return: error code (0 for OK)
        @rtype: int
        """
        raise NotImplementedError("AbstractShutterPlugin.shoot() must be overloaded")
