# NOTICE: This has not been tested!!

# Ugh PowerShell.

# NOTICE: Keep python_pkg up to date!
$cygwin_dir = "C:\Cygwin"
$cygwin_setup = "$cygwin_dir\setup.exe"
$python_pkg = "python-2.7.10-1"
$src64 = "https://cygwin.com/setup-x86_64.exe"
$src32 = "https://cygwin.com/setup-x86.exe"

# Procedures:
    # 1. Install Cygwin if needed.
    # 2. Install the dependencies of the game.
    # 3. Start a Cygwin environment.
    # 4. Install the game.
# Information:
    # https://cygwin.com/cgi-bin2/package-grep.cgi
    # http://ss64.com/ps/bits.txt
    # http://ss64.com/ps/
    # https://cygwin.com/faq/faq.html#faq.setup.cli

#Set-ExecutionPolicy -ExecutionPolicy bypass
$ErrorActionPreference = "Stop"
Import-Module BitsTransfer

if (Test-Path -Path $cygwin_dir)
    Write-Host "Cygwin appears to be pre-installed."
else
{
    # 64/32
    if ( Test-Path -Path "C:\Windows\SysWOW64" )
        $src = $src64
    else
        $src = $src32
    
    Write-Host "Downloading $src"
    Start-BitsTransfer "$src" cygwin.exe
    
    Write-Host "Installing Cygwin"
    .\cygwin.exe -R "$cygwin_dir"
    Move-Item -path cygwin.exe -destination "$cygwin_setup"
}

Write-Host "Installing $python_pkg and the game"
$cygwin_setup -R "$cygwin_dir" -P $python_pkg
"$cygwin_dir\bin\bash" -c "./configure -v; make; make install"
