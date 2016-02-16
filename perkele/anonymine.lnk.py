#!/usr/bin/python2

'''
http://fileanalysis.net/lnk/
http://stackoverflow.com/questions/6161776/convert-windows-filetime-to-second-in-unix-linux
https://github.com/libyal/liblnk/blob/master/documentation/Windows%20Shortcut%20File%20%28LNK%29%20format.asciidoc
http://packages.altlinux.org/en/Sisyphus/srpms/liblnk/sources/Windows_Shortcut_File_%28LNK%29_format.pdf/download

HasName         0x00000004      The StringData section contains the NAME_STRING field
HasRelativePath 0x00000008      The StringData section contains the RELATIVE_PATH field
HasArguments    0x00000020      The StringData section contains the COMMAND_LINE_ARGUMENTS field
HasIconLocation 0x00000040      The LNK file contains a custom icon location

0x00:   Length=76               4C 00 00 00
0x04:   Magic                   01 14 02 00 00 00 00 00 c0 00 00 00 00 00 00 46
0x14    Flags=0x2c              2c 00 00 00
0x18    Flags=0x80              80 00 00 00
0x1c    1601-01-01 00:00        00 00 00 00 00 00 00 00
0x24    1601-01-01 00:00        00 00 00 00 00 00 00 00
0x2c    1601-01-01 00:00        00 00 00 00 00 00 00 00
0x34    target size=42          2a 00 00 00
0x38    icon index=42           2a 00 00 00
0x3c    show=normal=1           01 00 00 00
0x40    hotkey=2 0x00           00 00
0x42    10 0x00                 00 00
                                00 00 00 00
                                00 00 00 00
stringdata Name/description
stringdata rel path
stringdata args
stringdata icon path
'''

import time
import sys

def mklnk(outfile, bash_path, icon_path):
    #f = open('anonymine.lnk', 'w')
    f = open(outfile, 'w')
    f.write('\x4c\x00\x00\x00')     # Header length 76
    f.write('\x01\x14\x02\x00\x00\x00\x00\x00\xc0\x00\x00\x00\x00\x00\x00\x46')
    f.write('\x6c\x00\x00\x00')     # HasName|HasRelativePath|HasArguments|HasIconLocation
    f.write('\x80\x00\x00\x00')     # Normal file attributes

    # Unix time to 64 bit LE x*100ns since 1601-01-01
    def addtime(unix_time):
        value = int((unix_time + 11644477200) * 10**7)
        # 11644473600 doesn't seem to work.
        for i in range(8):
            f.write(chr(value%256))
            value//=256
    addtime(time.time())            # Creation: 64bit LE 100ns since 1601-01-01
    addtime(time.time())            # Access:   64bit LE 100ns since 1601-01-01
    addtime(time.time())            # Write:    64bit LE 100ns since 1601-01-01

    f.write('\0\0\0\0')             # Target size = meaningless for Anonymine.
    f.write('\0\0\0\0')             # Icon index = ?
    f.write('\x01\x00\x00\x00')     # Show window in normal way.
    f.write('\0\0')                 # No hotkey
    f.write(10*'\0')                # Reserved

    def stringdata(s):
        f.write(chr(len(s)%256))
        f.write(chr(len(s)//256))
        f.write(s)
    stringdata('Anonymine - minesweeper without guessing')
    #stringdata('C:\\Cygwin\\bin\\bash.exe')
    stringdata(bash_path)
    stringdata('-lc anonymine')
    #stringdata('C:\\Cygwin\\usr\\share\\pixmaps\\anonymine.ico')
    stringdata(icon_path)

    f.close()

if __name__ == '__main__':
    if len(sys.argv) != 4:
        sys.stderr.write('Usage: ./anonymine.lnk.py link bash icon\n')
    else:
        mklnk(sys.argv[1], sys.argv[2], sys.argv[3])
