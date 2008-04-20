# -*- coding: iso-8859-1 -*-

""" Panohead remote control.

Custom exceptions.

Implements class:

- HardwareError

@author: Frederic Mantegazza
@copyright: 2007
@license: CeCILL
@todo:
"""

__revision__ = "$Id$"


class PapywizardError(Exception):
    """ Base class for custom exceptions.
    """


class HardwareError(PapywizardError):
    """ A hardware error occured.
    """

