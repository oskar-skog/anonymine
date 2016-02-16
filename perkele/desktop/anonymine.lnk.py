#!/usr/bin/python
# -*- encoding: utf-8 -*-


# In a nutshell: PERKELE


# desktop/anonymine.lnk.py link description bash command icon

'''
http://fileanalysis.net/lnk/
http://stackoverflow.com/questions/6161776/convert-windows-filetime-to-second-in-unix-linux
https://github.com/libyal/liblnk/blob/master/documentation/Windows%20Shortcut%20File%20%28LNK%29%20format.asciidoc
http://packages.altlinux.org/en/Sisyphus/srpms/liblnk/sources/Windows_Shortcut_File_%28LNK%29_format.pdf/download

HasLinkInfo     0x00000002      The LNK file contains location information
HasName         0x00000004      The StringData section contains the NAME_STRING field
HasRelativePath 0x00000008      The StringData section contains the RELATIVE_PATH field
HasArguments    0x00000020      The StringData section contains the COMMAND_LINE_ARGUMENTS field
HasIconLocation 0x00000040      The LNK file contains a custom icon location
IsUnicode       0x00000080      UTF-16 LE instead of ASCII in data strings

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
import os

def mklnk(outfile, description, bash_path, command, icon_path):
    if sys.version_info[0] == 2:
        import locale
        encoding = locale.getdefaultlocale()[1]
    
    use_unicode = False
    for arg in (description, bash_path, command, icon_path):
        try:
            if sys.version_info[0] == 2:
                arg.decode('us-ascii')
            else:
                arg.encode('us-ascii')
        except:
            use_unicode = True
            break
    
    f = open(outfile, 'wb')
    def write(s):
        if sys.version_info[0] == 3:
            f.write(s.encode('iso-8859-1'))
        else:
            f.write(s)
    
    def le32(x):
        for i in range(4):
            write(chr(x%256))
            x//=256
    
    le32(76)                            # Header length
    write('\x01\x14\x02\x00\x00\x00\x00\x00\xc0\x00\x00\x00\x00\x00\x00\x46')
    le32(0x66 | 0x80*use_unicode)       # Flags
    #write('\xe6\x00\x00\x00')     # HasLinkInfo|HasName|HasArguments|HasIconLocation|IsUnicode
    le32(0x80)                          # Normal file attribute

    # Unix time to 64 bit LE x*100ns since 1601-01-01
    def addtime(unix_time):
        value = int((unix_time + 11644473600) * 10**7)
        # 11644473600 doesn't seem to work.
        for i in range(8):
            write(chr(value%256))
            value//=256
    addtime(time.time())            # Creation: 64bit LE 100ns since 1601-01-01
    addtime(time.time())            # Access:   64bit LE 100ns since 1601-01-01
    addtime(time.time())            # Write:    64bit LE 100ns since 1601-01-01

    le32(0)                     # Target size = meaningless for Anonymine.
    le32(0)                     # Icon index = ?
    le32(1)                     # Show window in normal way.
    write('\0\0')               # No hotkey
    write(10*'\0')              # Reserved
    
    # Location information
    diskname = 'The drive on which Cygwin is installed'
    if sys.version_info[0] == 2:
        bash_path = bash_path.decode(encoding)
        bash_path += unichr(0)
    else:
        bash_path += chr(0)
    if use_unicode:
        bash_path = bash_path.encode('utf-16-le')
        head_length = 49 + len(diskname)
    else:
        bash_path = bash_path.encode('us-ascii')
        head_length = 45 + len(diskname)
    le32(head_length + len(bash_path))   # Total size
    le32(32)                    # Header length
    le32(1)                     # Flags: local
    #le32(28)                    # Offset to volume information
    if use_unicode:
        le32(32)                    # Offset to volume information
        #le32(head_length - 1)   # Use the terminating NUL of diskname as ASCII path.
        le32(0)
    else:
        le32(28)                    # Offset to volume information
        le32(head_length)       # Offset to ASCII local path
    le32(0)                     # Not used: Network share information
    le32(0)                     # Not used: Common path ASCII
    if use_unicode:
        le32(head_length)       # Offset to UTF-16-LE path
    # Volume information
    le32(16 + len(diskname) + 1)  # size of volume information
    le32(0)             # Unknown, probably fixed
    write('ABCD')       # Bogus drive serial number
    le32(16)            # Offset to ASCII label relative to volume information.
    write(diskname)
    write('\0')
    # Local path
    f.write(bash_path)
    
    def stringdata(s):
        write(chr(len(s)%256))
        write(chr(len(s)//256))
        if use_unicode:
            f.write(s.encode('utf-16-le'))
        else:
            f.write(s.encode('us-ascii'))
    
    if sys.version_info[0] == 3:
        stringdata(description)
        #stringdata(bash_path)
        stringdata('-lc ' + command)
        stringdata(icon_path)
    else:
        stringdata(description.decode(encoding))
        #stringdata(bash_path.decode(encoding))
        stringdata('-lc ' + command)
        stringdata(icon_path.decode(encoding))
    
    # Just because I can.
    msg = '\nJåo nåo e ja jåo YOLO ja nåo!\n'
    if sys.version_info[0] == 3:
        msg = msg.encode('utf-8')
    le32(len(msg) + 8)                          # length
    write('\n42\n')                             # magic
    f.write(msg)
    write('\0\0\0\0')
    
    # write('\0\0\0\0')           # Extra data terminal block
    # Needed ?
    
    f.close()

if __name__ == '__main__':
    if len(sys.argv) != 6:
        sys.stderr.write(
            'Usage: '
            'desktop/anonymine.lnk.py link description bash command icon\n'
        )
    else:
        mklnk(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
