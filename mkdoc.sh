#!/bin/sh

modules="papywizard.common papywizard.controller papywizard.hardware \
         papywizard.model papywizard.view papywizard.view3D"

epydoc --html -o html/ --name Papywizard --inheritance listed \
       --url http://trac.gbiloba.org/papywizard --graph all -v \
       $modules

#epydoc --pdf -o papywizard.pdf --name Papywizard --inheritance listed \
       #--url http://trac.gbiloba.org/papywizard --graph all -v \
       #$modules

