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

'''Field classes for Anonymine

Copyright (c) Oskar Skog, 2016
Released under the FreeBSD license.

Field classes for Anonymine
===========================

    generic_field           multidimensional with either Moore or von
                            Neumann neighbourhoods.
    hexagonal_field         Two dimensional with 6 neighbours per cell.
'''

class generic_field():
    '''
    Rectangular multidimensional minesweeper field with Moore or
    von Neumann neighbourhoods.
    
    Methods provided
    ================
        
        __init__(self, dimensions, moore=True, flagcount=True)
            `dimensions` is a list of the dimensions of the
            multidimensional rectangle.
        
        get(self, coordinate)
            What is there at `coordinate`.
            'F' (flag), 'X' (revealed mine), None (free), int number
        
        flag(self, coordinate)
        unflag(self, coordinate)
            (un)Flag the cell at `coordinate` and de-/increase the flag
            count.
        
        reveal(self, coordinate)
            Reveal the free cell at `coordinate`
        
        get_callback(self, function_name)
        set_callback(self, function_name, function, argument)
            function(self, argument)
            Set various callbacks.
            
        fill(self, mines)
            Place all mines.
        
        clear(self)
            Reinitialize the field.  All cells will be free cells and
            all mines will be removed.
        
        get_neighbours(self, coordinate)
        all_cells(self)
        
        flags_left
            Actually an attribute.
    
    
    Coordinate system
    =================
    
        The coordinate is a tuple of natural numbers representing the
        cells position along each axis. (Starting from zero.)
        
        coordinate = (p[n] ...) where p is the position in the nth
        dimension.
        
        2D example
        ----------
        
            (0, 0) (0, 1) (0, 2)
            (1, 0) (1, 1) (1, 2)
            (2, 0) (2, 1) (2, 2)
    
    
    Internal
    ========
    
        The field is one dimensional on the inside
        ==========================================
        
            self.field = [...]
                Single dimensional field.
                List of raw cells.
                The coordinates in the multidimensional fields
                are interpreated as numbers of an irregular base.
                Ex
                    width = 60 (minutes), heihgt = 24 (hours)
                    one_dimensional_coordinate = 60*hour + minute
            
            self.K_VISIBLE, self.K_FLAG, self.K_MINE, self.K_NUMER,
            self.K_CACHE_N1, self.K_VALUE
                Constants; indices for the items in the raw cell
                lists.
            
            _set_raw(coordinate, index, value)
            _get_raw(coordinate)
                PFO
            
            This system is used instead of the old one with the
            `_deref` method.  The `_deref` method had the disadvantage
            that things got weird if was used more than once per
            function.
            
            self.dimensions
                size
            
            self.N_DIMENSIONS
            self.dimension_multiplier = [...]
                These are generated for performance reasons.
        

    '''
    
    def __init__(self, dimensions, moore=True, flagcount=True):
        '''
        `dimensions` is a list of the sizes for each dimension.
        Eg. [width, height, depth, fourth] or [width, height]
        
        There is no limitation on the amount of dimensions,
        you are expected to not choose something ridiculous.
        
        If `moore` is True, Moore neighbourhoods will be used.
            (Neighbours at both sides and corners in 2D, and neighbours
            at surfaces, sides and corners in 3D, etc.)
            neighbours = 3^dimensions - 1
        If `moore` is False, von Neumann neighbourhoods will be used.
            (Neighbours only at the sides in 2D, and only at the
            surfaces in 3D, etc.)
            neighbours = 2*dimensions
        '''
        self.K_VISIBLE = 0      # bool
        self.K_FLAG = 1         # bool
        self.K_MINE = 2         # bool
        self.K_NUMBER = 3       # int
        self.K_CACHE_N = 4      # None or list
        self.K_VALUE = 5        # See `get`.
        
        self.dimensions = dimensions
        self.moore = moore
        self.flagcount = flagcount
        
        self.callbacks = {
            'input': (None, None),
            'lose': (None, None),
            'win': (None, None),
        }
        
        self.N_DIMENSIONS = len(dimensions)
        self.dimension_multiplier = []
        product = 1
        for x in dimensions:
            product *= x
        for x in dimensions:
            product /= x
            self.dimension_multiplier.append(product)
        
        self.clear()
    
    def clear(self):
        '''Clear the field and reset the flags left count.
        '''
        # NOTICE: This function MUST work when self.field and self.flags_left
        # are undefined.
        self.free_cells = 1
        for size in self.dimensions:
            self.free_cells *= size
        self.field = []
        for i in range(self.free_cells):
            self.field.append(list((False, False, False, 0, None, None)))
        if self.flagcount:
            self.flags_left = 0
        else:
            self.flags_left = None
    
    def _get_raw(self, coordinate):
        '''Return the internal values of a cell.
        
        `coordinate` is an external (multidimensional) coordinate.
        
        Return a list of 6 elements:
        self.K_VISIBLE = 0      # bool
        self.K_FLAG = 1         # bool
        self.K_MINE = 2         # bool
        self.K_NUMBER = 3       # int
        self.K_CACHE_N = 4      # None or list
        self.K_VALUE = 5        # See `get`.
        '''
        i = index = 0
        while i < self.N_DIMENSIONS:
            index += coordinate[i] * self.dimension_multiplier[i]
            i += 1
        return self.field[int(index)]
    
    def _set_raw(self, coordinate, element, value):
        '''Set an internal value of a cell and recompute its value.
        
        See `_get_raw`.
        '''
        def internal_get():
            cell = self._get_raw(coordinate)
            assert not (cell[self.K_VISIBLE] and cell[self.K_FLAG])
            if cell[self.K_FLAG]:
                return 'F'
            if cell[self.K_VISIBLE]:
                if cell[self.K_MINE]:
                    return 'X'
                else:
                    return cell[self.K_NUMBER]
            else:
                return None
        i = index = 0
        while i < self.N_DIMENSIONS:
            index += coordinate[i] * self.dimension_multiplier[i]
            i += 1
        index = int(index)
        self.field[index][element] = value
        self.field[index][self.K_VALUE] = internal_get()
    
    def _call(self, function_name):
        if function_name == 'win':
            # Double check that the game was won.
            for cell in self.all_cells():
                _a, flagged, is_mine, _d, _e, _f = self._get_raw(cell)
                if flagged ^ is_mine:
                    function_name = 'lose'
                    break
        function, argument = self.callbacks[function_name]
        if function is not None:
            function(self, argument)
    
    def set_callback(self, function_name, function, argument):
        '''
        `function_name`
        ===============
        
            'input'     The field has just been modified.
            'lose'      A mine has just been revealed.
            'win'       All cells have been revealed or flagged.
        
        `function` is either None or a function that takes two
        arguments: the field object followed by the user specified
        `argument`.
        
        WARNING: Using the "input" callback to initialize a field
        (fill with mines) when the game starts could easily turn
        a minesweeper game a bit more realistic,
        **by using real fork()bombs.**
        '''
        self.callbacks[function_name] = function, argument
    
    def get_callback(self, function_name):
        '''
        function, argument = field.get_callback(function_name)
        
        See `set_callback`.
        '''
        function, argument = self.callbacks[function_name]
        return function, argument
    
    def get(self, coordinate):
        '''Return the external value of the cell at `coordinate`.
        
        `coordinate` is an external (multidimensional) coordinate.
        
        The return value is:
            A non-negative integer,     The number of mines around
                including zero:         this cell.
            
            'F'                         This cell has been flagged.
            
            None                        This is a free cell.
            
            'X'                         This cell is a revealed mine.
                                        Game over.
        '''
        i = index = 0
        while i < self.N_DIMENSIONS:
            index += coordinate[i] * self.dimension_multiplier[i]
            i += 1
        return self.field[int(index)][self.K_VALUE]
    
    def flag(self, coordinate, unflag=False):
        '''
        Flag the cell at `coordinate` and decrement
        `self.flags_left`, unless the cell already is flagged or is
        unflaggable.
        '''
        cell = self._get_raw(coordinate)
        # Only invisible (free or flagged) cell can be flagged or unflagged.
        if not cell[self.K_VISIBLE]:
            # No double-flag or double-unflag.
            if cell[self.K_FLAG] == bool(unflag):
                # Don't unflag too many.
                if self.flags_left or unflag or self.flags_left is None:
                    self._set_raw(coordinate, self.K_FLAG, not unflag)
                    if unflag:
                        self.free_cells += 1
                        if self.flagcount:
                            self.flags_left += 1
                    else:
                        self.free_cells -= 1
                        if self.flagcount:
                            self.flags_left -= 1
                    self._call('input')
        if not self.free_cells:
            self._call('win')
    
    def unflag(self, coordinate):
        '''
        Unflag the cell at `coordinate` and increment
        `self.flags_left`, unless the cell already is not flagged.
        '''
        self.flag(coordinate, True)
    
    def get_neighbours(self, coordinate):
        '''
        Return a list of coordinates that are the neighbours to the
        cell at `coordinate`.
        '''
        
        v = self._get_raw(coordinate)[self.K_CACHE_N]
        if v is not None: return v
        
        # Do some sanity checks on the coordinate.
        assert len(coordinate) == len(self.dimensions)
        for index in range(len(coordinate)):
            assert 0 <= coordinate[index] < self.dimensions[index]
        
        # Generate neighbour indices for each axis.
        axis_neigbours = []
        for index, position in enumerate(coordinate):
            # What directions are possible?
            negative = position > 0
            positive = position < self.dimensions[index] - 1
            # What will the relative indices be?
            if positive and negative:
                axis_neigbours.append((position - 1, position, position + 1))
            elif positive:
                axis_neigbours.append((              position, position + 1))
            elif negative:
                axis_neigbours.append((position - 1, position              ))
            else:
                axis_neigbours.append((              position              ))
            
        # List the neighbours.
        # neighbours = []
        if self.moore:
            # Calculating Moore neighbourhoods requires recursion.
            def moore(i):
                out = []
                for position in axis_neigbours[i]:
                    if i:
                        for head in moore(i - 1):
                            out.append(head + [position])
                    else:
                        out.append([position])
                return out
            # Filter out the center cell.
            # Remember that the coordinates are not yet of the proper type.
            neighbours = list(filter(
                lambda x: tuple(x) != tuple(coordinate),
                moore(len(coordinate) - 1)
            ))
        else:
            # von Neumann neighbours only differ on one axis at a time.
            neighbours = []
            for axis_index, axis in enumerate(axis_neigbours):
                for position in axis:
                    if position != coordinate[axis_index]:
                        # All other axes are unchanged.
                        neighbour = []
                        for i in range(len(coordinate)):
                            if i == axis_index:
                                neighbour.append(position)
                            else:
                                neighbour.append(coordinate[i])
                        neighbours.append(neighbour)
        
        # Transform the coordinates into a proper form before returning.
        proper = list(map(tuple, neighbours))
        self._set_raw(coordinate, self.K_CACHE_N, proper)
        return proper
    
    def all_cells(self):
        '''Return a list of all coordinates.
        '''
        def list_cells(dimensions):
            out = []
            for i in range(dimensions[0]):
                if len(dimensions) == 1:
                    out.append([i])
                else:
                    for tail in list_cells(dimensions[1:]):
                        out.append([i] + tail)
            return out
        return list(map(tuple, list_cells(self.dimensions)))
    
    def reveal(self, coordinate):
        '''"Click" on the free cell at `coordinate`.
        
        It will automatically reveal an area when a zero has been
        revealed.
        
        It will call the "lose" callback if a mine is revealed.
        '''
        coordinate_list = [coordinate]
        lose = False
        while coordinate_list:
            coordinate = coordinate_list.pop()
            cell = self._get_raw(coordinate)
            if cell[self.K_FLAG]:
                continue        # Not continuing now would be a terrible idea.
            if not cell[self.K_VISIBLE]:
                self._set_raw(coordinate, self.K_VISIBLE, True)
                self.free_cells -= 1
                if cell[self.K_MINE]:
                    lose = True
                    # break not needed, because only the first revealed
                    # cell can possibly be a mjne.  There are not other
                    # coordinates on the list.
                # Field of zeroes.
                if cell[self.K_NUMBER] == 0:
                    coordinate_list.extend(self.get_neighbours(coordinate))
        # Final callbacks
        self._call('input')
        if lose:
            self._call('lose')
        elif not self.free_cells:
            self._call('win')
    
    def fill(self, mines):
        '''Fill the field with mines and generate the numbers.
        
        `mines` is a list of coordinates of the mines.
        '''
        # Sanity checking.
        for index, mine in enumerate(mines):
            for another_index, another_mine in enumerate(mines):
                if another_index != index:
                    assert another_mine != mine
        # Place the mines.
        if self.flagcount:
            self.flags_left = len(mines)
        for mine in mines:
            self._set_raw(mine, self.K_MINE, True)
        # Generate the numbers.
        for coordinate in self.all_cells():
            count = 0
            for neighbour in self.get_neighbours(coordinate):
                 if self._get_raw(neighbour)[self.K_MINE]:
                     count += 1
            self._set_raw(coordinate, self.K_NUMBER, count)
    
    def __str__(self):
        '''Generate a simple text version of a two dimensional field for
        debugging purposes.
        '''
        if len(self.dimensions) != 2:
            return "<String representation is only available in 2D fields.>\n"
        
        trans = {
            None: ' ',  'F': 'F',       'X': 'X',       0: '-',
            1: '1',     2: '2',         3: '3',         4: '4',
            5: '5',     6: '6',         7: '7',         8: '8'
        }
        
        pre_post = '#' * (self.dimensions[0] + 2) + '\n'
        
        out = pre_post
        for y in range(self.dimensions[1]):
            out += '#'
            for x in range(self.dimensions[0]):
                out += trans[self.get((x, y))]
            out += '#\n'
        out += pre_post
        out += 'Flags left: {0}\n'.format(self.flags_left)
        
        return out


class hexagonal_field(generic_field):
    r'''
    Coordinate system
    =================
    
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
    
    
    See the doc-string for `generic_field` for everything else.
    Notice that `__init__` accepts different arguments.
        __init__(self, width, height, flagcount=True)
    '''
    def __init__(self, width, height, flagcount=True):
        self.flagcount = flagcount
        self.dimensions = [width, height]
        
        self.K_VISIBLE = 0
        self.K_FLAG = 1
        self.K_MINE = 2
        self.K_NUMBER = 3
        self.K_CACHE_N = 4
        self.K_VALUE = 5
        
        # self.cache_N = cache_N
        
        self.callbacks = {
            'input': (None, None),
            'lose': (None, None),
            'win': (None, None),
        }
        
        self.N_DIMENSIONS = 2
        self.dimension_multiplier = [height, 1]
        
        self.clear()
    
    def get_neighbours(self, coordinate):
        v = self._get_raw(coordinate)[self.K_CACHE_N]
        if v is not None: return v
        
        x, y = coordinate
        if y % 2:
            neighbours = [
                    (x, y-1), (x+1, y-1),
                (x-1, y),               (x+1, y),
                    (x, y+1), (x+1, y+1)
            ]
        else:
            neighbours = [
                    (x-1, y-1), (x, y-1),
                (x-1, y),               (x+1, y),
                    (x-1, y+1), (x, y+1)
            ]
        v = list(filter(
            lambda coord: 0 <= coord[0] < self.dimensions[0],
            list(filter(
                lambda coord: 0 <= coord[1] < self.dimensions[1],
                neighbours
            ))
        ))
        self._set_raw(coordinate, self.K_CACHE_N, v)
        return v
    
    
    def __str__(self):
        trans = {
            None: ' ',  'F': 'F',       'X': 'X',       0: '0',
            1: '1',     2: '2',         3: '3',         4: '4',
            5: '5',     6: '6',         7: '7',         8: '8'
        }
        
        pre_post = '#' * (2*self.dimensions[0] + 2) + '\n'
        
        out = pre_post
        for y in range(self.dimensions[1]):
            out += '#'
            for x in range(self.dimensions[0]):
                if y % 2:
                    out += '-' + trans[self.get((x, y))]
                else:
                    out += trans[self.get((x, y))] + '-'
            out += '#\n'
        out += pre_post
        out += 'Flags left: {0}\n'.format(self.flags_left)
        
        return out


import os
import sys
assert __name__ != '__main__', "I'm not a script."

try:
    assert os.geteuid() or sys.platform.startswith('haiku'), "Gaming as root!"
except AttributeError:
    pass
