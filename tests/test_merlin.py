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

Tests

Implements
==========

- MerlinTest

@author: Frédéric Mantegazza
@copyright: (C) 2007-2011 Frédéric Mantegazza
@license: CeCILL
"""


import serial
import bluetooth

BT_ADDRESS = "00:50:C2:58:55:B9"
SERIAL_PORT = "/dev/ttyS0"


class HardwareError(Exception):
    pass


class BluetoothDriver(object):
    """ Driver for bluetooth connection.

    This driver only uses bluetooth socket.
    """
    def __init__(self):
        print "BluetoothDriver._init(): trying to connect to %s..." % BT_ADDRESS
        try:
            self._sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            self._sock.connect((BT_ADDRESS, 1))
            try:
                self._sock.settimeout(1.)
            except NotImplementedError:
                print "BluetoothDriver._init(): bluetooth stack does not implment settimeout()"
        except bluetooth.BluetoothError, error:
            err, msg = eval(error.message)
            raise HardwareError(msg)
        except:
            print "BluetoothDriver._init()"
            raise
        else:
            time.sleep(8)
            self.empty()
            print "BluetoothDriver._init(): successfully connected to %s" % address

    def write(self, data):
        print "BluetoothDriver.write(): data=%s" % repr(data)
        size = self._sock.send(data)
        return size

    def read(self, size):
        data = self._sock.recv(size)
        print "BluetoothDriver.read(): data=%s" % repr(data)
        if size and not data:
            raise IOError("Timeout while reading on bluetooth bus")
        else:
            return data


class SerialDriver(object):
    """ Driver for serial connection.
    """
    def __init__(self):
        self._serial = serial.Serial(port=SERIAL_PORT)
        self._serial.timeout = 1
        self._serial.baudrate = 9600

    def empty(self):
        self.read(self._serial.inWaiting())

    def write(self, data):
        print "SerialDriver.write(): data=%s" % repr(data)
        size = self._serial.write(data)
        return size

    def read(self, size):
        data = self._serial.read(size)
        print "SerialDriver.read(): data=%s" % repr(data)
        if size and not data:
            raise IOError("Timeout while reading on serial bus")
        else:
            return data


class MerlinTest(object):
    """ Test Merlin com.
    """
    def __init__(self):
        print "MerlinTest.__init__()"
        self._numAxis = 1
        #self._driver = BluetoothDriver()
        self._driver = SerialDriver()

    def _sendCmd(self, cmd, param=""):
        """ Send a command to the axis.

        @param cmd: command to send
        @type cmd: str

        @return: answer
        @rtype: str
        """
        print "MerlinTest._sendCmd()"
        cmd = "%s%d%s" % (cmd, self._numAxis, param)
        for nbTry in xrange(3):
            try:
                answer = ""
                self._driver.empty()
                self._driver.write(":%s\r" % cmd)
                c = ''
                while c not in ('=', '!'):
                    c = self._driver.read(1)
                    print c,
                if c == '!':
                    c = self._driver.read(1) # Get error code
                    raise IOError("Merlin didn't understand the command '%s' (err=%s)" % (cmd, c))
                answer = ""
                while True:
                    c = self._driver.read(1)
                    print c,
                    if c == '\r':
                        break
                    answer += c
            except IOError:
                print "MerlinTest._sendCmd(): axis %d can't sent command '%s'. Retrying..." % (self._numAxis, cmd)
            else:
                break
        else:
            raise HardwareError("Merlin axis %d can't send command '%s'" % (self._numAxis, cmd))

        print "MerlinHardware._sendCmd(): axis %d cmd=%s, ans=%s" % (self._numAxis, cmd, answer)
        return answer

    def go(self):
        """ Make the test.
        """

        # Stop axis
        self._sendCmd("L")

        # Check motor?
        self._sendCmd("F")

        # Get full circle count
        self._sendCmd("a")

        # Get sidereal rate
        self._sendCmd("D")


def main():
    test = MerlinTest()
    test.go()


if __name__ == "__main__":
    main()
