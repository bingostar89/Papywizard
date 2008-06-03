# -*- coding: iso-8859-1 -*-

""" Panohead remote control.

Controller.

Implements class:

- AbstractController

@author: Frederic Mantegazza
@copyright: 2007
@license: CeCILL
@todo:
"""

__revision__ = "$Id$"


class AbstractController(object):
    """ Base class for controllers.
    """
    def refreshView(self):
        """ Refresh the view widgets according to model values.
        """
        raise NotImplementedError
