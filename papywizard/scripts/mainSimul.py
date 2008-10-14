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

Main script for simulator

@author: FrÃ©dÃ©ric Mantegazza
@copyright: (C) 2007-2008 FrÃ©dÃ©ric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

import sys
import optparse

from papywizard.common import config
from papywizard.common.configManager import ConfigManager
from papywizard.common.loggingServices import Logger
from papywizard.hardware.simulator import MerlinOrionEthernetSimulator, MerlinOrionSerialSimulator


def main():
    usage = "Usage: %prog bluetooth|serial|ethernet [options]"
    version = "%%prog %s" % config.VERSION
    parser = optparse.OptionParser(usage=usage, version=version)
    parser.set_defaults(connexion=config.SIMUL_DEFAULT_CONNEXION)
    parser.add_option("-c", "--connexion", action="store",
                                           dest="connexion",
                                           choices=('bluetooth', 'serial', 'ethernet'),
                                           help="Connection")
    parser.add_option("-a", "--address", action="store",
                                         dest="btAddress",
                                         help="Bluetooth device address")
    parser.set_defaults(serialPort=config.SIMUL_SERIAL_PORT)
    parser.add_option("-s", "--serial-port", action="store",
                                             dest="serialPort",
                                             help="Serial port")
    parser.set_defaults(ethernetHost=config.SIMUL_ETHERNET_HOST)
    parser.add_option("-n", "--hostname", action="store",
                                          dest="ethernetHost",
                                          help="Ethernet hostname/IP address")
    parser.set_defaults(ethernetPort=config.SIMUL_ETHERNET_PORT)
    parser.add_option("-p", "--ethernet-port", action="store",
                                               dest="ethernetPort",
                                               help="Ethernet port")
    parser.set_defaults(loggerLevel=config.SIMUL_LOGGER_LEVEL)
    parser.add_option("-l", "--logger-level", action="store",
                                              choices=('trace', 'debug', 'info', 'warning', \
                                                       'error', 'exception', 'critical'),
                                              dest="loggerLevel",
                                              help="Logger level")
    (option, args) = parser.parse_args()
    #Logger().debug("option=%s" % option)

    if option.connexion == 'serial':
        simulator = MerlinOrionSerialSimulator(option.serialPort)
    elif option.connexion == 'bluetooth':
        Logger().warning("Bluetooth simulator not yet impemented")
        sys.exit(1)
    elif option.connexion == 'ethernet':
        simulator = MerlinOrionEthernetSimulator(option.ethernetHost, option.ethernetPort)
    else:
        parser.print_help()
        sys.exit(1)

    Logger().setLevel(option.loggerLevel)
    Logger().info("Starting Papywizard simulator...")
    simulator.run()
    Logger().info("Papywizard simulator stopped")


if __name__ == "__main__":
    main()
