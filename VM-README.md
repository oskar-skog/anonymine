Anonymine VM
============

The scripts vmsetup, addplayer, update-anonymine and calibrate-anonymine
are intended to be run on a virtual machine dedicated for playing Anonymine
over SSH.

This README is a work in progress.



Installation (premade VM)
=========================

1. Create a virtual machine using the downloaded hard drive image.
2. Boot it up and login as 'sysop' with the password 'sysop'.
3. Configure the network of the virtual machine to allow access to
   the virtual machine's TCP port number 22.



Pre-installed commands
======================

vmsetup
-------

Run this the first time.


update-anonymine
----------------

Run this whenever you want to update to the newest version of Anonymine.

NOTICE: This will overwrite the system-wide configuration.


addplayer
---------

Run this to add a new account for playing Anonymine over SSH.


calibrate-anonymine
-------------------

**Overwrite** `/etc/anonymine/enginecfg` with a configuration appropriate
for the virtual machine.
This expects to be run as a user with permission to overwrite that file.
