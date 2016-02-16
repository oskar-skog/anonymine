#!/usr/bin/python

# Copyright (c) Oskar Skog, 2016
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1.  Redistributions of source code must retain the above copyright notice,
#     this list of conditions and the following disclaimer.
#
# 2.  Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions and the following disclaimer in the documentation
#     and/or other materials provided with the distribution.
#
# This software is provided by the copyright holders and contributors "as is"
# and any express or implied warranties, including, but not limited to, the
# implied warranties of merchantability and fitness for a particular purpose
# are disclaimed. In no event shall the copyright holder or contributors be
# liable for any direct, indirect, incidental, special, exemplary, or
# consequential damages (including, but not limited to, procurement of
# substitute goods or services; loss of use, data, or profits; or business
# interruption) however caused and on any theory of liability, whether in
# contract, strict liability, or tort (including negligence or otherwise)
# arising in any way out of the use of this software, even if advised of the
# possibility of such damage.

'''This module provides the engine of Anonymine

Copyright (c) Oskar Skog, 2016
Released under the FreeBSD license.

The engine of Anonymine
=======================

    The class `game_engine` contains the field, initializes it and
    manipulates it during a game.
    The documentation for `game_engine` will describe the coordinate
    system for the different field types, methods used to manipulate
    it, and the actual gluing of engine and interface.

'''

import os
import time
import signal
import sys

# Allow module names to be changed later.
import anonymine_solver as solver
import anonymine_fields as fields

class game_engine():
    r'''
    This class creates game engine objects.
    
    This doc-string describes how the engine and the interface
    interacts.
    
    The engine:
        * Creates and initializes a field with the specified game
            parameters.
        * Has a play loop that will use the interface to do all IO.
        * Contains and manipulates the field object.
    
    The interface:
        * Makes a representation of the field for the player.
        * Contains IO methods that are used by the play loop.
        * Uses various important methods of the engine.
    
    
    (field-) Coordinates (non-hexagonal fields)
    ===========================================
    
        Each coordinate is a tuple of (x, y).
        Where x and y are integers and
            0 <= x < width
            0 <= y < height
        
        (0, 0)  (1, 0)  (2, 0)  (3, 0)  (4, 0)
        (0, 1)  (1, 1)  (2, 1)  (3, 1)  (4, 1)
        (0, 2)  (1, 2)  (2, 2)  (3, 2)  (4, 2)
        (0, 3)  (1, 3)  (2, 3)  (3, 3)  (4, 3)
        (0, 4)  (1, 4)  (2, 4)  (3, 4)  (4, 4)
        
        The Moore neighbours are
            (x-1, y-1)  (x, y-1)  (x+1, y-1)
            (x-1, y)              (x+1, y)
            (x-1, y+1)  (x, y+1)  (x+1, y+1)
        And the Neumann neighbours are:
                        (x, y-1)
            (x-1, y)              (x+1, y)
                        (x, y+1)
    
    
    (field-) Coordinates (hexagonal fields)
    =======================================
    
        Each coordinate is a tuple of (x, y).
        Where x and y are integers and
            0 <= x < width
            0 <= y < height
        
        What makes this different from square fields is that odd lines
        are indented (a half step) on the screen so that it looks like.
        
         / \ / \ / \ / \ / \ / \ / \
        |0,0|1,0|2,0|3,0|4,0|5,0|6,0|
         \ / \ / \ / \ / \ / \ / \ / \
          |0,1|1,1|2,1|3,1|4,1|5,1|6,1|
         / \ / \ / \ / \ / \ / \ / \ /
        |0,2|1,2|2,2|3,2|4,2|5,2|6,2|
         \ / \ / \ / \ / \ / \ / \ / \
          |0,3|1,3|2,3|3,3|4,3|5,3|6,3|
           \ / \ / \ / \ / \ / \ / \ /
        
        The neighbourhoods are similar to Moore neighbourhoods, but
        these have no "corners" on the right for even rows, and no
        "corners" on the left on odd rows
        
        The hexagonal neighbours are:
            (x - 1 + y%2,  y - 1)       (x + y%2,  y - 1)
            (x - 1,  y)                 (x + 1,  y)
            (x - 1 + y%2,  y + 1)       (x + y%2,  y + 1)
    
    
    Important parts of the engine object
    ====================================
    
        `engine.game_status` is a string that has the value:
            'pre-game'  when the field hasn't been initialized
                        (every cell is free).
            'play-game' while the game has been initialized but not
                        won or lost.
            (INTERNAL): 'game-won'
            (INTERNAL): 'game-lost'
        
        `engine.field` is the actual field object.  The interface will
            need to use the `get` method of the field.  A modifying
            method (of the field object) can safely be used AFTER
            initialization.
        
        `engine.flag(coordinate)` is a simple wrapper that flags free
            cells and unflags flagged cells.
        
        `engine.reveal(coordinate)` is a simple wrapper that reveals
            cells after initialization, OR initializes the field.
            (Let the player choose the starting point by playing.)
        
        `engine.init_field(startpoint)` is the method that will place
            the mines and reveals the starting point, from which the
            game CAN be won.
    
    
    Required methods of the interface object
    ========================================
    
        `interface.input(engine)`
            Receive input from the user and manipulate the field.
        
        `interface.output(engine)`
            "Show" the user a representation of the field.
            To do this, you are probably going to need to know how
            the coordinate system used by the field works.
        
        `interface.anykey_cont()`
            "Press any key to continue..."
            Let the user see the last screen before returning from
            `engine.play_game`.
            This method is actually not required.
    '''
    def __init__(self, cfgfile, **parameters):
        '''
        `cfgfile` is the path to the "enginecfg" configuration file.
        
        Recognised keyword arguments are:
            width=              # int >= 4
            height=             # int >= 4
            mines=              # int; Only integers are allowed here.
            gametype=           # str; 'moore', 'hex' or 'neumann'
            flagcount=          # bool; Count how many flags are left?
            guessless=          # bool; Must be possible to solve without
                                #       guessing?
        
        As of version 0.0.20, no parameters are mandatory; they all
        have default values.  This may change in the future.
        '''
        # Define some constants.
        self.gametypes = ('moore', 'hex', 'neumann')
        
        # Handle parameters.
        default = {
            'width':     10,
            'height':    10,
            'mines':     10,
            'gametype':  'moore',
            'flagcount': True,
            'guessless': True,
        }
        for key in default:
            if key not in parameters:
                parameters[key] = default[key]
        assert parameters['gametype'] in ('neumann', 'hex', 'moore')
        
        # Begin initialization.
        self.cfg = eval(open(cfgfile).read())
        self.gametype = parameters['gametype']
        self.n_mines = parameters['mines']
        self.guessless = parameters['guessless']
        if self.gametype == 'hex':
            self.field = fields.hexagonal_field(
                parameters['width'],
                parameters['height'],
                parameters['flagcount']
            )
        else:
            self.field = fields.generic_field(
                [parameters['width'], parameters['height']],
                self.gametype == 'moore',
                parameters['flagcount']
            )
        
        self.game_status = 'pre-game' # play-game game-won game-lost
        
        self.solver = solver.solver()
        self.solver.field = self.field
    
    #def init_field1(self, startpoint):
        # Available in versions 0.0.28 to 0.0.35.
        # Available as just "init_field" in versions prior to 0.0.28.
    
    def init_field2(self, startpoint):
        '''(Internal use.)  Uses enginecfg.
        
        Uses multiple processes to test random fields to find a
        solvable one.  Each process will have a limited amount of time
        for each field, if it fails in the limited time it will start
        over.  When a process finds a solvable field, it will store the
        coordinates of the mines in a tempfile which will then be read
        by the master process.
        
        enginecfg['init-field']
            'procs'     int: Number of slaves.
            'maxtime'   float: Start over after having tried one field
                        for this long.
            'filename'  string: tempfile, filename.format(x)
        '''
        # Difference from the old version:
        #       * Use signal.setitimer (unix) in the child processes rather
        #         than having the parent killing them.
        #         -> This sets a time limit on each field rather
        #         than all fields together.
        #       * Because of the above, the parent code can be simplified.
        def child():
            # The startpoint and its neighbours MUST NOT be mines.
            safe = self.field.get_neighbours(startpoint) + [startpoint]
            cells = list(filter(
                lambda x: x not in safe,
                self.field.all_cells()
            ))
            # Raise Exception when too much time has been spent.
            if 'setitimer' in dir(signal):
                maxtime = self.cfg['init-field']['maxtime']
                def handler(ignore1, ignore2):
                    raise Exception('<Caught SIGALRM>')
                def die(ignore1, ignore2):
                    os._exit(0)
                signal.signal(signal.SIGALRM, handler)
                signal.signal(signal.SIGCONT, die)      # see BUG#6
            solved = False
            while not solved:
                try:
                    # Choose self.n_mines randomly selected mines.
                    cells.sort(key=lambda x: os.urandom(1))
                    mines = cells[:self.n_mines]
                    self.field.clear()
                    self.field.fill(mines)
                    self.field.reveal(startpoint)
                    # Try to solve the field in a limited time.
                    # NOTICE:   ITIMER_REAL     SIGALRM
                    #           ITIMER_VIRTUAL  SIGVTALRM
                    #           ITIMER_PROF     SIGPROF
                    if 'setitimer' in dir(signal):
                        signal.setitimer(signal.ITIMER_REAL, maxtime)
                        solved = self.solver.solve()[0]
                        signal.setitimer(signal.ITIMER_REAL, 0.0)
                    else:
                        solved = self.solver.solve()[0]
                except Exception:
                    pass
            # Store the mine coordinates in the tempfile.
            filename = self.cfg['init-field']['filename'].format(os.getpid())
            try:
                if sys.version_info[0] == 2:
                    f = open(filename, 'wx')
                else:
                    f = open(filename, 'x')
                assert not os.path.islink(filename)
            except:
                raise Exception('Break-in attempt!')
            for x, y in mines:
                f.write('{0} {1}\n'.format(x, y))
            f.close()
            os._exit(0)
        # FUNCTION STARTS HERE.
        # Clean up after whatever may have called us.
        self.field.clear()
        # Compatibility for non-unix systems.
        if 'fork' not in dir(os):
            child()
            return
        # Create slaves.
        children = []
        for i in range(self.cfg['init-field']['procs']):
            pid = os.fork()
            if pid:
                children.append(pid)
            else:
                try:
                    child()
                except KeyboardInterrupt:
                    # Kill the python interpreter on ^C.
                    os._exit(1)
        # Wait for the first child to finish.
        success_pid = 0
        while success_pid not in children:
            pid, status = os.wait()
            if os.WIFEXITED(status):
                success_pid = pid
            else:
                print(pid)
        # Kill all remaining children.
        # Delete potential left-over tempfiles.
        filename = self.cfg['init-field']['filename']
        for child in children:
            if child != success_pid:
                try:
                    os.kill(child, signal.SIGCONT)      # See BUG#6
                    os.waitpid(child, 0)    # Destroy the zombie.
                    os.remove(filename.format(child))
                except OSError:
                    pass
        # Parse the tempfile.
        f = open(filename.format(success_pid))
        lines = f.read().split('\n')[:-1]
        os.remove(filename.format(success_pid))
        mines = []
        for line in lines:
            mine = list(map(int, line.split(' ')))
            mines.append(mine)
        # Fill the field with the mines.
        self.field.fill(mines)
        self.field.reveal(startpoint)
    
    def init_field(self, startpoint):
        '''Place the mines and reveal the starting point.
        
        Internal details:
            It will wrap in `init_field2` in guessless mode.
            It will place the mines by itself when not in guessless
            mode.
        '''
        if self.guessless:
            # Wrap in the best version.
            self.init_field2(startpoint)
        else:
            safe = self.field.get_neighbours(startpoint) + [startpoint]
            cells = list(filter(
                lambda x: x not in safe,
                self.field.all_cells()
            ))
            # Choose self.n_mines randomly selected mines.
            cells.sort(key=lambda x: os.urandom(1))
            mines = cells[:self.n_mines]
            self.field.clear()
            self.field.fill(mines)
            self.field.reveal(startpoint)
    
    def flag(self, coordinate):
        '''Automatic flag/unflag at `coordinate`.
        '''
        if self.field.get(coordinate) == 'F':
            self.field.unflag(coordinate)
        else:
            self.field.flag(coordinate)
    
    def reveal(self, coordinate):
        '''Automatic initialization/reveal at `coordinate`.
        '''
        if self.game_status == 'pre-game':
            # # Let the player choose the starting point.
            self.init_field(coordinate)
            self.start = time.time()
            self.game_status = 'play-game'
        elif self.game_status == 'play-game':
            self.field.reveal(coordinate)
        else:
            assert False, "game_status not in ('play-game', 'in-game')"
    
    def play_game(self, interface):
        '''bool_won, float_time_spent = play_game(interface)
        
        Attach the interface to the engine and play the game.
        
        See the doc-string for the class as a whole for (more)
        information.
        '''
        def win(field, engine):
            engine.game_status = 'game-won'
            field.set_callback('win', None, None)
            field.set_callback('lose', None, None)
        def lose(field, engine):
            engine.game_status = 'game-lost'
            field.set_callback('win', None, None)
            field.set_callback('lose', None, None)
        
        self.field.clear()
        # Enter the main loop.
        self.start = time.time()        # FIXME
        self.field.set_callback('win', win, self)
        self.field.set_callback('lose', lose, self)
        while self.game_status in ('pre-game', 'play-game'):
            interface.output(self)
            interface.input(self)
        if self.game_status == 'game-lost':
            for cell in self.field.all_cells():
                self.field.reveal(cell)
        interface.output(self)
        try:
            interface.anykey_cont()         # ANY key
        except NameError:
            pass
        
        return self.game_status == 'game-won', time.time() - self.start

assert os.geteuid(), "Why the-fuck(7) are you playing games as root?"
assert __name__ != '__main__', "I'm not a script."
