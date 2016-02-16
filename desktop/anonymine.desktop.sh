#!/bin/sh

out=$1
name=$2
Name=$3
description=$4

cat > $out << __EOF__
[Desktop Entry]
Type=Application
Name=$Name
Description=$4
Exec=$name
Terminal=true
Categories=Game;
Icon=$name
__EOF__
