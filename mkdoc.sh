#!/bin/sh
epydoc --html -o html/ --name Papywizard --inheritance listed \
       --url http://trac.gbiloba.org/papywizard --graph all -v \
       papywizard.common papywizard.controller papywizard.hardware \
       papywizard.model papywizard.view papywizard.view3D
