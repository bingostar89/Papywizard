#!/bin/sh

python -c "import sys; sys.argv[0] = \"Papywizard\"; from papywizard.scripts.simulator import main; main()" $@
