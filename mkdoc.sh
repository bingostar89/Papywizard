#!/bin/sh
epydoc --html -o html/ --name Papywizard --inheritance listed \
       --url http://trac.gbiloba.org/papywizard --graph all -v \
       papywizard

