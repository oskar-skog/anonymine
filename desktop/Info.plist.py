#!/usr/bin/python

# Info.plist.py outfile human_name description_name version tech_name

import sys

f = open(sys.argv[1], 'w')
f.write('''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key>             <string>{2}</string>
    <key>CFBundleDisplayName</key>      <string>{3}</string>
    <key>CFBundleVersion</key>          <string>{4}</string>
    <!-- -->
    <key>CFBundleSignature</key>        <string>boom</string>
    <key>CFBundlePackageType</key>      <string>APPL</string>
    <key>CFBundleExecutable</key>       <string>{5}-wrapper</string>
    <key>CFBundleIconFile</key>         <string>icon.icns</string>
    <key>LSApplicationCategoryType</key><string>public.app-category.puzzle-games</string>
    <!-- -->
    <key>NSHumanReadableCopyright</key>
    <string>
        Copyright (c) 2016, Oskar Skog
        This software is released under the FreeBSD license (2-clause BSD).
    </string>
</dict>
</plist>
'''.format(*sys.argv))
f.close()
