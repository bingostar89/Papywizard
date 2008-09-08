# -*- coding: iso-8859-1 -*-

""" Panohead remote control.

License
=======

 - B{papywizard} (U{http://trac.gbiloba.org/papywizard}) is Copyright:
  - (C) 2007-2008 Frédéric Mantegazza

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

View

Implements
==========

- Coords3D
- Fov3D
- Apn3D
- Arm3D
- Body3D
- Tripod3D
- World3D
- Head3D
- View3D

@author: Frédéric Mantegazza
@copyright: (C) 2007-2008 Frédéric Mantegazza
@license: CeCILL
"""

__revision__ = "$Id$"

import time
import math

#import PIL.Image
import visual as vp
import visual.text as vpt
import povexport

from papywizard.common import config
from papywizard.common.loggingServices import Logger


class Object3D(vp.frame):
    """ Class defining defaults method of 3D subObjects.
    """
    def __init__(self, display, frame=None, *args, **kwargs):
        """ Init Object3D.
        """
        super(Object3D, self).__init__(display=display, frame=frame, *args, **kwargs)


class Coords3D(Object3D):
    """ Wrold space axis.
    """
    def __init__(self, display, frame=None):
        """ Init Coords3D object.
        """
        super(Coords3D, self).__init__(display=display, frame=frame)

        self.xAxis = vp.arrow(display=display, frame=self,
                              pos=(0, 0, 0), axis=(0.300, 0, 0), fixedwidth=1, shaftwidth=0.01,
                              color=vp.color.green)
        self.xLabel = vpt.text(display=display,
                               pos=(0.320, 0, -0.030/2.), visible=1,
                               width=0.030, depth=0.100, height=0.030,
                               color=vp.color.green, up=(0, 0, 1), axis=(1, 0, 0),
                               string="X", justify='center')

        self.yAxis = vp.arrow(display=display, frame=self,
                              pos=(0, 0, 0), axis=(0, 0.300, 0), fixedwidth=1, shaftwidth=0.01,
                              color=vp.color.green)
        self.yLabel = vpt.text(display=display,
                               pos=(0, 0.320, -0.030/2.), visible=1,
                               width=0.030, depth=0.100, height=0.030,
                               color=vp.color.green, up=(0, 0, 1), axis=(0, 1, 0),
                               string="Y", justify='center')

        self.zAxis = vp.arrow(display=display, frame=self,
                              pos=(0, 0, 0), axis=(0, 0, 0.300), fixedwidth=1, shaftwidth=0.01,
                              color=vp.color.green)
        self.zLabel = vpt.text(display=display,
                               pos=(0, 0, 0.320), visible=1,
                               width=0.030, depth=0.100, height=0.030,
                               color=vp.color.green, up=(0, 0, 1), axis=(1, 0, 0),
                               string="Z", justify='center')


class Fov3D(Object3D):
    """ Lens fov representation.
    """
    def __init__(self, display, frame=None):
        """ Init Fov3D object.
        """
        super(Fov3D, self).__init__(display=display, frame=frame)

        hFov = config.VIEW3D_HEAD_HFOV * math.pi / 180.
        vFov = config.VIEW3D_HEAD_VFOV * math.pi / 180.
        l = config.VIEW3D_HEAD_FOV_LENGTH
        vertex1 = (l * math.sin(hFov / 2.), l * math.cos(hFov / 2.), -l * math.sin(vFov / 2.))
        vertex2 = (-l * math.sin(hFov / 2.), l * math.cos(hFov / 2.), -l * math.sin(vFov / 2.))
        vertex3 = (-l * math.sin(hFov / 2.), l * math.cos(hFov / 2.), l * math.sin(vFov / 2.))
        vertex4 = (l * math.sin(hFov / 2.), l * math.cos(hFov / 2.), l * math.sin(vFov / 2.))

        self.fov1 = vp.curve(display=display, frame=self,
                             pos=[(0, 0, 0,), vertex1])

        self.fov2 = vp.curve(display=display, frame=self,
                             pos=[(0, 0, 0,), vertex2])

        self.fov3 = vp.curve(display=display, frame=self,
                             pos=[(0, 0, 0,), vertex3])

        self.fov4 = vp.curve(display=display, frame=self,
                             pos=[(0, 0, 0,), vertex4])

        self.fov5 = vp.curve(display=display, frame=self,
                             pos=[vertex1, vertex2, vertex3, vertex4, vertex1])

    def draw(self, hFov, vFov):
        """
        """
        hFov *= math.pi / 180.
        vFov *= math.pi / 180.
        l = config.VIEW3D_HEAD_FOV_LENGTH
        vertex1 = (l * math.sin(hFov / 2.), l * math.cos(hFov / 2.), -l * math.sin(vFov / 2.))
        vertex2 = (-l * math.sin(hFov / 2.), l * math.cos(hFov / 2.), -l * math.sin(vFov / 2.))
        vertex3 = (-l * math.sin(hFov / 2.), l * math.cos(hFov / 2.), l * math.sin(vFov / 2.))
        vertex4 = (l * math.sin(hFov / 2.), l * math.cos(hFov / 2.), l * math.sin(vFov / 2.))

        self.fov1.pos = [(0, 0, 0,), vertex1]
        self.fov2.pos = [(0, 0, 0,), vertex2]
        self.fov3.pos = [(0, 0, 0,), vertex3]
        self.fov4.pos = [(0, 0, 0,), vertex4]
        self.fov5.pos = [vertex1, vertex2, vertex3, vertex4, vertex1]


class Apn3D(Object3D):
    """ APN representation class.
    """
    def __init__(self, display, frame=None):
        """ Init Apn3D object.
        """
        super(Apn3D, self).__init__(display=display, frame=frame)

        self.lens = vp.cylinder(display=display, frame=self,
                                pos=(0, -0.060, 0), axis=(0, 0.080, 0), radius=0.030,
                                color=vp.color.blue)

        self.body = vp.box(display=display, frame=self,
                           pos=(0, -0.060-0.040/2., 0), length=0.110, height=0.040, width=0.070,
                           color=vp.color.blue)


class Arm3D(Object3D):
    """ Arm representation class.
    """
    def __init__(self, display, frame=None):
        """ Init Arm3D object.
        """
        super(Arm3D, self).__init__(display=display, frame=frame)

        # Cylindrical base
        self.base = vp.cylinder(display=display, frame=self,
                                pos=(-0.070, 0, 0), axis=(0.040, 0, 0), radius=0.040,
                                color=vp.color.orange)

        # Vertical arm
        vPos = 0.
        self.vArm = vp.box(display=display, frame=self,
                           pos=(-0.070+0.025+0.015/2., 0, -vPos), length=0.015, height=0.040, width=0.110,
                           color=vp.color.orange)

        # Horizontal arm
        self.hArm = vp.box(display=display, frame=self,
                           pos=(-0.070+0.040+0.120/2., 0, -vPos-0.110/2.+0.015/2.), length=0.120, height=0.040, width=0.015,
                           color=vp.color.orange)


class Body3D(Object3D):
    """ Body representation class.
    """
    def __init__(self, display, frame=None):
        """ Init Body3D object.
        """
        super(Body3D, self).__init__(display=display, frame=frame)

        self.pitchBase = vp.cylinder(display=display, frame=self,
                                     pos=(-0.110, 0, 0), axis=(0.040, 0, 0), radius=0.045,
                                     color=vp.color.red)

        self.vBody = vp.box(display=display, frame=self,
                            pos=(-0.110+0.030/2., 0, -0.210/2.), length=0.030, height=0.090, width=0.210,
                            color=vp.color.red)

        self.hBody = vp.box(display=display, frame=self,
                            pos=(-0.110+0.160/2., 0, -0.210+0.060/2.), length=0.160, height=0.120, width=0.060,
                            color=vp.color.red)

        self.yawBase = vp.cylinder(display=display, frame=self,
                                   pos=(0, 0, -0.210), axis=(0, 0, -0.025), radius=0.035,
                                   color=vp.color.red)


class Tripod3D(Object3D):
    """ Tripod representation class.
    """
    def __init__(self, display, frame=None):
        """ Init Tripod3D object.
        """
        super(Tripod3D, self).__init__(display=display, frame=frame)

        self.plate = vp.cylinder(display=display, frame=self,
                                 pos=(0, 0, -0.025), axis=(0, 0, -0.005), radius=0.035,
                                 color=vp.color.white)

        self.upperColumn = vp.cylinder(display=display, frame=self,
                                       pos=(0, 0, -0.025-0.005), axis=(0, 0, -0.400), radius=0.012,
                                       color=vp.color.white)

        self.upperBase = vp.cylinder(display=display, frame=self,
                                     pos=(0, 0, -0.025-0.005-0.400), axis=(0, 0, -0.040), radius=0.050,
                                     color=(0.1, 0.1, 0.1))

        self.lowerColumn = vp.cylinder(display=display, frame=self,
                                       pos=(0, 0, -0.025-0.005-0.400), axis=(0, 0, -0.350), radius=0.017,
                                       color=vp.color.white)

        self.lowerBase = vp.cylinder(display=display, frame=self,
                                     pos=(0, 0, -0.025-0.005-0.400-0.351), axis=(0, 0, 0.024), radius=0.025,
                                     color=(0.1, 0.1, 0.1))

        self.hLegs = []
        for i in xrange(3):
            angle = (i + 1) * 2 * math.pi / 3.
            self.hLegs.append(vp.cylinder(display=display, frame=self,
                                          pos=(0, 0, -0.025-0.005-0.400-0.350+0.012),
                                          axis=(0.240 * math.cos(angle), 0.240 * math.sin(angle), 0),
                                          radius=0.012,
                                          color=vp.color.white))

        self.vLegs = []
        for i in xrange(3):
            angle = (i + 1) * 2 * math.pi / 3.
            self.vLegs.append(vp.cylinder(display=display, frame=self,
                                        pos=(0.040 * math.cos(angle), 0.040 * math.sin(angle), -0.025-0.005-0.400-0.010),
                                        axis=(0.550 * math.cos(angle), 0.550 * math.sin(angle), -0.900),
                                        radius=0.012,
                                        color=vp.color.white))

        self.pos = (0, 0, -0.210)


class World3D(Object3D):
    """ World.
    """
    def __init__(self, display, frame=None):
        """ Init World3D object.
        """
        super(World3D, self).__init__(display=display, frame=frame)

        #im = PIL.Image.open("world.jpg") # Load texture image
        #im = im.rotate(90)
        #data = vp.array(list(im.getdata()), vp.ubyte) # read pixel data into flat Numeric array
        #data = vp.reshape(data, (512, 1024, 3)) # reshape for rgb texture
        #im = data[::-1].copy() # copy() is necessary to make array contiguous in memory
        #texture = vp.texture(data=im, type="rgb")

        self.ground = vp.cylinder(display=display, frame=self,
                             pos=(0, 0, 0), axis=(0, 0, -0.1), radius=100,
                             color=(0, 0.1, 0))

        self.sky = vp.sphere(display=display, frame=self,
                             pos=(0, 0, 0), radius=100,
                             color=(0.5, 0.5, 1)) #, texture=texture)

        self.pos = (0, 0, -0.210-0.025-0.005-0.400-0.900)


class Head3D(Object3D):
    """ 3F Head representation.

    Class generating the state of the 3D scene of the head and changing it's state.
    """
    def __init__(self, display, frame=None):
        """ Init of Head3D object.
        """
        super(Head3D, self).__init__(display=display, frame=frame)

        self.body = Body3D(display=display, frame=self)

        self.arm = Arm3D(display=display, frame=self.body)

        self.apn = Apn3D(display=display, frame=self.arm)

        self.fov = Fov3D(display=display, frame=self.apn)

        self.tripod = Tripod3D(display=display, frame=self)


class View3D(vp.display):
    """ Main 3D view.
    """
    def __init__(self, title, width=600, height=400, forward=(-1, 1, -0.3), fov=math.pi/3., scale=(0.1, 0.1, 0.1)):
        """ Init View3D object.
        """
        vp.display.__init__(self, title=title, width=width, height=height, center=(0, 0, 0), fov=fov, scale=scale,
                            background=vp.color.black, up=(0, 0, 1), forward=forward)

        self.lights = [1 * vp.vector(0, 2, 1).norm(),
                       0.1 * vp.vector(0, -1, 3).norm(),
                       #0.1 * vp.vector(0, 1, 3).norm(),
                       #0.1 * vp.vector(1, 0, 3).norm(),
                       0.1 * vp.vector(-1, 0, 3).norm()
                       ]
        self.ambient = 0.5

        #self.stereo = 'redblue'

        self.__prevYaw = 0
        self.__prevPitch = 0

        self.head3D = Head3D(self)
        self.coords3D = Coords3D(self)
        self.world3D = World3D(self)

    def viewFromCamera(self, yaw, pitch):
        """ View from camera position.
        """
        yaw *= math.pi / 180.
        pitch *= math.pi / 180.
        l = config.VIEW3D_HEAD_FOV_LENGTH
        self.center = (l * math.sin(yaw), l * math.cos(yaw), l * math.sin(pitch))
        self.forward = vp.vector(l * math.sin(yaw), l * math.cos(yaw), l * math.sin(pitch))

    def pov(self, filename='papywizard.pov', xy_ratio=4./3.):
        """ Export the view as povray file.
        """
        povexport.export(display=self, filename=filename, xy_ratio=xy_ratio)


    def draw(self, yaw, pitch, hFov=30, vFov=20):
        """ Redraw the view according to new position.

        @param yaw: yaw angle (°)
        @type yaw: float

        @param pitch: pitch angle (°)
        @type pitch: float

        @param hFov: lens horiz. fov angle (°)
        @type hFov: float

        @param vFov: lens vert. fov angle (°)
        @type vFov: float
        """
        yaw *= math.pi / 180.
        pitch *= math.pi / 180.
        self.head3D.body.rotate(angle=-(yaw-self.__prevYaw), axis=(0, 0, 1))
        self.head3D.arm.rotate(angle=-(pitch-self.__prevPitch), axis=(1, 0, 0))
        self.__prevYaw = yaw
        self.__prevPitch = pitch

        self.head3D.fov.draw(hFov, vFov)
