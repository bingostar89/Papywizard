#/bin/sh

TMP_DIR="tmp"
POT_FILE="papywizard.pot"

# Extract strings from python files
python_files="scripts/papywiz.py"
python_files="$python_files `find papywizard -type f -name \"*.py\"`"
xgettext --language=Python --from-code=utf-8 --keyword=_ --output=$TMP_DIR/$POT_FILE $python_files

# Extract strings from glade files
glade_files=`ls papywizard/view/*.glade`
for file in $glade_files; do
    intltool-extract -l --type=gettext/glade $file
done
xgettext --language=Python --from-code=utf-8 --keyword=_ --keyword=N_ --output=$TMP_DIR/$POT_FILE $python_files $TMP_DIR/*.h

# Generate PO files
msginit --input=$TMP_DIR/$POT_FILE --locale=en_US --no-translator --no-wrap --output=$TMP_DIR/en_US.po
msginit --input=$TMP_DIR/$POT_FILE --locale=fr_FR --no-translator --no-wrap --output=$TMP_DIR/fr_FR.po

