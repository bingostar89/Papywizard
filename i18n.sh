#/bin/sh
# $Id$

APP_NAME="papywizard"
TMP_DIR="tmp"
POT_FILE="$APP_NAME.pot"
PO_FILE="$APP_NAME.po"
MO_FILE="$APP_NAME.mo"
LOCALE_DIR="locale"

mkdir -p $TMP_DIR

# Extract strings from python files
python_files="`find papywizard -type f -name \"*.py\"`"

echo xgettext --language=Python --from-code=utf-8 --default-domain=$APP_NAME --keyword=_ --no-wrap --output=$TMP_DIR/$APP_NAME $python_files
xgettext --language=Python --from-code=utf-8 --default-domain=$APP_NAME --keyword=_ --no-wrap --output=$TMP_DIR/$APP_NAME $python_files

# Extract strings from glade files
glade_files=`ls papywizard/view/*.glade`
for file in $glade_files; do
    echo intltool-extract -l --type=gettext/glade $file
    intltool-extract -l --type=gettext/glade $file
done

xgettext --language=Python --from-code=utf-8 --default-domain=$APP_NAME --keyword=_ --keyword=N_ --no-wrap --output=$TMP_DIR/$POT_FILE $python_files $TMP_DIR/*.h

# Generate PO and MO files
for lang in 'en' 'fr' 'pl' 'de' 'es' 'nl' 'it'; do
    mkdir -p $LOCALE_DIR/$lang/LC_MESSAGES
    if ! [ -e $LOCALE_DIR/$lang/LC_MESSAGES/$PO_FILE ]; then
        echo msginit --input=$TMP_DIR/$POT_FILE --locale=$lang --no-translator --no-wrap --output=$LOCALE_DIR/$lang/LC_MESSAGES/$PO_FILE
        msginit --input=$TMP_DIR/$POT_FILE --locale=$lang --no-translator --no-wrap --output=$LOCALE_DIR/$lang/LC_MESSAGES/$PO_FILE
    fi
    if [ $TMP_DIR/$POT_FILE -nt $LOCALE_DIR/$lang/LC_MESSAGES/$MO_FILE ]; then
        echo msgmerge -U $LOCALE_DIR/$lang/LC_MESSAGES/$PO_FILE $TMP_DIR/$POT_FILE
        msgmerge -U $LOCALE_DIR/$lang/LC_MESSAGES/$PO_FILE $TMP_DIR/$POT_FILE
        echo msgfmt -v --output-file=$LOCALE_DIR/$lang/LC_MESSAGES/$MO_FILE $LOCALE_DIR/$lang/LC_MESSAGES/$PO_FILE
        msgfmt -v --output-file=$LOCALE_DIR/$lang/LC_MESSAGES/$MO_FILE $LOCALE_DIR/$lang/LC_MESSAGES/$PO_FILE
    fi
done
