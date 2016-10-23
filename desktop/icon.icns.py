#!/usr/bin/python
# -*- encoding: utf-8 -*-

'''
Build the Mac OS X icon from a bunch of PNGs.

$(srcdir)desktop/icon.icns.py <icons.icns> <png_name_root>

${png_name_root}-16x16.png
${png_name_root}-32x32.png
${png_name_root}-64x64.png
${png_name_root}-256x256.png
'''

import sys

outfile = sys.argv[1]
basename = sys.argv[2]

def be32(x):
    s = bytes()
    for i in range(4):
        if sys.version_info[0] == 3:
            s = chr(x%256).encode('iso-8859-1') + s
        else:
            s = chr(x%256) + s
        x //= 256
    return s


PNGs = [
    ('icp4', '-16x16.png'),     #    Since Mac OS X 10.7
    ('icp5', '-32x32.png'),     #    Since Mac OS X 10.7
    ('icp6', '-64x64.png'),     #    Since Mac OS X 10.7
    ('ic08', '-256x256.png'),   # ** Since Mac OS X 10.5
]

data = bytes()

def noynoynoy():
    data = bytes()
    msg = '\n\n\nJåo nåo e ja jåo YOLO ja nåo!\n\n\n'
    if sys.version_info[0] == 3:
        msg = msg.encode('utf-8')
    # file(1) may echo the first type it sees.
    data += 'PNGs'.encode('us-ascii')
    data += be32(len(msg) + 8)
    data += msg
    return data

data += noynoynoy()
for PNG in PNGs:
    new_file = open(basename + PNG[1], 'rb').read()
    data += PNG[0].encode('us-ascii')
    data += be32(len(new_file) + 8)
    data += new_file
data += noynoynoy()

f = open(outfile, 'wb')
f.write('icns'.encode('us-ascii'))
f.write(be32(len(data) + 8))
f.write(data)
f.close()
