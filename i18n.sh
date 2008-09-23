#/bin/sh

TMP_DIR="tmp"
POT_FILE="papywizard.pot"
MO_FILE="papywizard.mo"
LOCALE_DIR="locale"

# Extract strings from python files
python_files="scripts/papywiz.py"
python_files="$python_files `find papywizard -type f -name \"*.py\"`"
xgettext --language=Python --from-code=utf-8 --keyword=_ --no-wrap --output=$TMP_DIR/$POT_FILE $python_files

# Extract strings from glade files
glade_files=`ls papywizard/view/*.glade`
for file in $glade_files; do
    intltool-extract -l --type=gettext/glade $file
done
xgettext --language=Python --from-code=utf-8 --keyword=_ --keyword=N_ --no-wrap --output=$TMP_DIR/$POT_FILE $python_files $TMP_DIR/*.h

# Generate PO files
for lang in 'en_US' 'fr_FR'; do
    mkdir -p $LOCALE_DIR/$lang/LC_MESSAGES
    if [ -e $TMP_DIR/$lang.po ]; then
        msgmerge -U $TMP_DIR/$lang.po $TMP_DIR/$POT_FILE
    else
        msginit --input=$TMP_DIR/$POT_FILE --locale=$lang --no-translator --no-wrap --output=$TMP_DIR/$lang.po
    fi
    msgfmt -v --output-file=$LOCALE_DIR/$lang/LC_MESSAGES/$MO_FILE $TMP_DIR/$lang.po
done
