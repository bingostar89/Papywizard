#!/bin/sh
# $Id$

modules="papywizard.common papywizard.controller papywizard.hardware \
         papywizard.model papywizard.view papywizard.plugins"

epydoc --html -o api/ --name Papywizard --inheritance listed \
       --url http://www.papywizard.org --graph all -v \
       --exclude papywizard.common.i18n \
       --exclude papywizard.common.pixmaps \
       --exclude papywizard.view.icons \
       $modules

#epydoc --pdf -o tmp/papywizard.pdf --name Papywizard --inheritance listed \
       #--url http://trac.gbiloba.org/papywizard --graph all -v \
       #$modules

