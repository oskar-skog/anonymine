@echo off
:: ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

:: Where you want Cygwin to be installed:
set cygwin_dir=C:\Cygwin

:: Where you want the Cygwin installer to be placed, (including filename):
set cygwin_setup=%cygwin_dir%\setup.exe

:: Temporary, make sure this doesn't exist.
set dlroot=C:\Tmp-anonymine

:: ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

:: URLs and valid destination file names.
set src64=https://cygwin.com/setup-x86_64.exe
set src32=https://cygwin.com/setup-x86.exe
set dl64=%dlroot%\setup-x86_64.exe
set dl32=%dlroot%\setup-x86.exe

:: 64/32
if exist %systemroot%\SysWOW64\ set src=%src64%
if exist %systemroot%\SysWOW64\ set dl_setup=%dl64%
if not exist %systemroot%\SysWOW64\ set src=%src32%
if not exist %systemroot%\SysWOW64\ set dl_setup=%dl32%
:: http://stackoverflow.com/questions/9681863/windows-batch-variables-wont-set
:: Can't have these in the conditional that checks whether Cygwin exists or not.

:: Procedures:
    :: 1. Install Cygwin if needed.
    :: 2. Install the dependencies of the game.
    :: 3. Start a Cygwin environment.
    :: 4. Install the game.
:: Information:
    :: https://cygwin.com/cgi-bin2/package-grep.cgi
    :: http://ss64.com/nt/syntax.html
    :: http://ss64.com/nt/bitsadmin.html
    :: BITS is so retarded that the source file needs o have the same name
    :: as the destination file, and you also have to use an absolute path.

if exist %cygwin_dir% (
    echo Cygwin appears to be pre-installed.
) else (    
    echo Downloading %src%
    mkdir %dlroot%
    bitsadmin /CREATE Anonymine_Cygwin_DL
    bitsadmin /ADDFILE Anonymine_Cygwin_DL %src% %dl_setup%
    bitsadmin /TRANSFER Anonymine_Cygwin_DL %src% %dl_setup%
    echo Installing Cygwin
    %dl_setup% --wait -q -R %cygwin_dir%
    move %dl_setup% %cygwin_setup%
    rmdir %dlroot%
)

echo Installing %python_pkg% and the game
%cygwin_setup% --wait -q -M -R %cygwin_dir% -P python -P make

:: bash -l to use the Cygwin $PATH rather than the MS %PATH%.
:: Then you'll need to go back to $OLDPWD.
%cygwin_dir%\bin\bash -lc 'echo "(Workaround): Do not remove!"'
%cygwin_dir%\bin\bash -lc ^
    'cd $OLDPWD; ./configure -v && make && make install && ./cygwin-sshd rmssh'

