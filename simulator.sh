#!/bin/sh

python -c "import sys; sys.argv[0] = \"simulator.sh\"; from papywizard.scripts.simulator import main; main()" $@
