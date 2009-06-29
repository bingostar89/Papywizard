#!/bin/sh

# Sync api to remote site

rsync -e ssh -av --delete api www-data@kimsufi:/var/www/papywizard/htdocs/ $@
