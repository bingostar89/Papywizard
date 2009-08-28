#!/bin/sh

# python -c "import sys; sys.argv[0] = \"Papywizard\"; from papywizard.scripts.main import main; main()" $@
python -c "from papywizard.scripts.main import main; main()" $@
