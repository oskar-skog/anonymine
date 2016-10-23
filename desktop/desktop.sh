#!/bin/sh

# Create the .desktop file for freedesktop.org (Linux) desktops.

if [ $# -ne 4 ]; then
    echo 'Usage: desktop/desktop.sh outfile cmd_name \
"Real name" "Description"' >> /dev/stderr
    exit 1
fi

out=$1
name=$2
Name=$3
description=$4

# NOTICE: $name is also used for the icon.

cat > $out << __EOF__
[Desktop Entry]
Categories=Game;
GenericName=Minesweeper
Type=Application
Name=$Name
Description=$Name
Comment=$description
Exec=$name
Terminal=true
Icon=$name
__EOF__
