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

'''Algorithm for solving and measuring the difficulty of minesweepers

Copyright (c) Oskar Skog, 2016
Released under the FreeBSD license.

Algorithm for solving and measuring the difficulty of minesweepers
==================================================================

    If you just want to use this and not understand it, see the
    documentation for the `solver` class, and fast forward through this
    doc-string all the way to
    "11  Implementation considerations/the field object".
    
    
    Definitions
    ===========
    
        Field
            ...
        Cell
            ...
        Neighbour
            ...
        Number cell/neighbour
            Zero is also a number, it is usually rendered as
            blank while playing.  And causes a chain reaction
            when revealed.
        Flag(ged) cell/neighbour
            ...
        Free cell/neighbour
            A cell that hasn't been revealed yet.
            These can become EITHER flagged cells or number cells.
        Deserted cell
            A free cell that does not have any number neighbour.
        
        To reveal
            The solver reveals cells ~=~ the player clicks on them.
            Cause a transition from free cell to number cell.
        To flag/mark
            The cell should be a mine, unless a bad mistake has been
            made...  Cause a transition from free cell to flag cell.
        
        Possibility
            A combination of coordinates that will fulfill the flag
            count for a selected number cell.
            Direct conflicts will never be included.
            (These can linguistically ironically be proven to be
            impossible later on... :)
        Primary possibilities
            The possibilities for THE cell to be solved.
        Secondary possibilities
            Following the chain of consequences from each primary
            possibility.
        Parent possibility and parent cell
            Generalization of primary possibility and "THE cell".
        Child possibility
            Generalization of secondary possibility.
        
        TODO: Learn the alphabet?
    
    
    Brief view on the idea
    ======================
    
        <- Unsolved cell
            Possibilities
                Possibility
                    Consequences?:
                        Neighbours to the potential flags
                            Possibilities (ALL neighbours MUST have \\
                              at least one possibility)
                                    recurse back to consequences
                    Too many flags?
        -> One possibility
        -> Constant mines or numbers in the remaining possibilities
        -> A need for more recursions of consequences
        -> Rule 9 is the only hope
    
    
    "Rules" for solving a minesweeper
    =================================
    
    Rule 0:     Primary possibilities
    Rule 1:     Exclusion of direct conflicts
    Rule 2:     Limitation to constants
    Rule 3:     Exclusion by mine count
    Rule 4:     Chain of consequences/Secondary possibilities
    Rule 5:     Chain of consequences/Chain of consequences
    Rule 6:     Measurement of difficulty
    Rule 7:     Main loop
    Rule 8:     Deserted cells/solved fields
    Rule 9:     Deserted cells/unsolved fields
    Rule 10:    Implementation considerations/internal
    Rule 11:    Implementation considerations/the field object
    
    
    0   The primary possibilities for a cell are the combinations of
        the needed amount of flags on the free coordinates.
        nCr(free coordinates, needed flags)
    
    
    1   A possibility is in conflict (an impossibility) when any number
        neighbour of any of the mines in the possibility is in
        conflict.
        A number cell is in conflict if it has too many flags
        surrounding it, or not enough free coordinates for the
        remaining flags.
        
        Illustration of the rule:
            a b c
            1(2)1
            - - -
        The cell in the middle (2) must place two flags on a, b and c.
        There are three possibilities
            a and b     The left 1 will be in conflict.
            a and c     OK
            b and c     The right 1 will be in conflict.
    
    
    2   When there are multiple possibilities, perhaps some coordinates
        are numbers or flags in every possibility.
        This is the next level of difficulty.
        Level = 1
        Illustration of the rule:
            a b c
            1(2)2
            - - -
        The cell in the middle (2) must place two flags on a, b and c.
        There are two of three possibilities
            a and b     The 1 will be in conflict.
            a and c     OK
            b and c     OK
        The cell c will be flagged in every possibility.
    
    
    3   Near the end, impossible primary possibilities could be
        eliminated by a comparison against the number of flags
        available.
        ** Any possibility with too many mines is impossible.
        
        Illustration of the rule:
            #####
            #abcF
            #2deF
            #F23F
            #----
        1 of d and e
        1 of a, b and d
        c cannot be known and will never be included in any
        possibility.
        
        Possibilities:
            1: d
            2: e+a
            3: e+b
        If there are less than two mines left, only the first
        possibility is possible.
    
    
    4   Each action (primary possibility) will have consequences
        (eliminating secondary possibilities).
        
        Each number neighbour to all (any-form-of) neighbours to the
        parent cell has secondary possibilities.
        
        The possibilities of these number neighbours interfere with the
        primary possibilities (the possibilities of the parent cell).
        
        tree of possibilities {
        Cell to be solved
            One of the primary possibilities
                One of the neighbours
                    One of the number neighbours
                        One of the secondary possibilities
                        ...
                    ...
                ...
            ...
        }
        
        If all secondary possibilities are impossible for any of the
        number neighbours, the primary possibility is impossible as
        well.
        
        Illustration of the rule:
            - - - -
            - a b c
            - 1(1)-
            - - - -
        The 1 to the right has three possibilities (primary
        possibilities):
            a   No direct conflict
            b   No direct conflict
            c   No direct conflict
        Rules 1 and 2 are not useful, the secondary possibilities must
        be considered.  When a flag has been placed on a, b or c, where
        can the 1 to the left place a flag without causing a conflict?
        The cell c is out of reach from the 1 to the left.
            primary     secondary
            a           a               No conflict
            a           b               Conflict
            b           a               Conflict
            b           b               No conflict
            c           a               Conflict
            c           b               Conflict
        The c cell is not a mine.
    
    
    5   The fourth rule can be recursed to form tertiary possibilities,
        and quaternary, etc.
        
        Rule 4 will be implemented as a recursive function that when
        ordered to recurse zero times, will take one primary
        possibility as an argument and tell if it is possible when
        considering the secondary possibilities.  When ordered to
        recurse one time, the function will recurse to test that all
        secondary possibilities are possible.
        
        The variable i used for determining the level of difficulty
        tells how many times the fourth rule has been used.
        i = 0   Only primary possibilities.
        i = 1   Primary and secondary possibilities.
        i = 2   Even tertiary possibilities are included.
    
    
    6   The algorithm will collect statistics of how difficult the
        minesweeper was to solve.
        Each level of difficulty will have a certain frequency.
        The levels of difficulty do not only represent the actual level
        of difficulty, but also why cells were difficult to solve.
        
        Level 4i:       After having followed the chain of consequences
                        of the actions (rules 4 and 5), there was only
                        one possible possibility.
        
        Level 4i + 1:   After having followed the chain, some
                        neighbouring cells have been proven to be or
                        not to be mines according to rule 2.
        
        Level 4i + 2:   After eliminating possibilities with too many
                        mines (rule 3) there were only one possibility
                        left.
        
        Level 4i + 3:   Combination of rule 2 and rule 3.
        
        The levels of difficulty do not perfectly match what a neural
        network would have experienced.
        
        The special level (-1) is used by rule 8 and the special level
        (-2) is used by rule 9.  A frequency on these mean that the
        rules were actually needed.
        
        The special level ('T') is the time it took in seconds.
        NOTICE: This will vary between machines.
    
    
    7   The solve loop will scan the field for unsolved cells (number
        cell with free neighbours) and send them to a solver function
        as the main argument.
        
        It will try with the "most solvable" cell first, ie the one
        with the most clues (number neighbours) in the surrounding area
        (2i + 1 by 2i + 1), to keep the game as easy as possible.
        
        The actual solver function will also take a second argument
        that specifies the level of difficulty.  The return value of
        the function specifies if
            (C): the cell was solved at this difficulty. -> Start with
                    the next, most solvable cell at the easiest level.
            (P): the cell was NOT solved at this difficulty. -> Try to
                    solve another cell at the same level.  When no more
                    cells can be solved at the current level, advance
                    to the next.
            (B): the cell cannot be solved at a higher value of i as it
                    relies on more clues. -> Try to solve some other
                    cells.
                    If all calls to the solve function in the range
                    [i, i+3] have resulted in this case, then there is
                    no hope of solving them at a higher level.
        
        pseudocode {
        solve loop (while unsolved cells):
            Dloop: i = 0 to infinity:
                am_I_screwed = currently True
                for j = 0 to 3:
                    For each unsolved cell, most solvable first:
                        switch solvable(selected cell, 4i + j):
                            case 'C':
                                collect difficulty statistics
                                jump to Dloop
                            case 'P':
                                continue looping over cells
                                am_I_screwed = False
                If am_I_screwed is True:
                    LOSE
        WIN
        }
    
    
    8   When the main loop has been left, there may still be some free
        cells in the field.
        If the minefield was impossible to solve or if the solved area
        is perfectly surrounded by flags, there can be deserted cells
        that have no neighbouring number cells.
        
        Illustration of the smallest possible partially solved field:
            ######
            #FFF?#
            #F8F?#
            #FFF?#
            ######
        
        If the minesweeper was "solved" and there are NO flags left:
            The deserted cells are obviously all numbers (including
            "zeros").
            See the illustration:
                There are no mines left, the deserted cells must be
                numbers.
            DEFINITIVELY SOLVABLE
        
        Elif the minesweeper was "solved" and there ARE flags left, but
        not enough to flag every deserted cell:
            See the illustration:
                There are one or two mines left, but three deserted
                cells.  It is impossible to know which are mines and
                which are numbers.
            DEFINITIVELY UNSOLVABLE
        
        Elif the minesweeper was "solved" and there ARE exactly as many
        flags left as there are deserted cells:
            See the illustration:
                All deserted cells must be mines.
            DEFINITIVELY SOLVABLE
        
        Else:
            See rule 9.
            PROBABLY UNSOLVABLE
        
        If this rule is needed, the frequency of the difficulty (-1)
        will be increased.
    
    
    9   If the field was not solved and there are deserted cells, the
        lowest possible number of mines for the potential possibilities
        must be equal to the number of flags left.
        
        When (min == flags) there cannot exist any mines among the
        deserted cells and they can therefore be revealed to give more
        clues.
        
        Not much of the algorithm can be reused to count the min value
        of the potential possibilities because:
            a: It doesn't count the flags (except for rule 3).
            b: It operates on single cells rather than all remaining
               cells.
        
        However, a brute-force on the non-deserted cells with rules 1
        and 3 would be simple to implement and would probably not be
        ridiculously inefficient.
        
        Rule 3 will automatically be included when checking if
        (min == flags).
        
        pseudocode {
        main loop:
            solve loop
            if deserted and not solved:
                if rule9():
                    goto solve loop
                else:
                    solved = False
            if deserted and solved:
                if flags == 0:
                    reveal_all_deserted()
                elif flags == deserted():
                    flag_all_deserted()
                else:
                    solved = False
        }
        
        If this rule is needed, the frequency of the difficulty (-2)
        will be increased.
    
    
    10  Implementation considerations (Python)
        =============================
        
        The field the solver operates on will be an object
        (can be modified in another function).
        
        The solver will be implemented as a class with methods to:
            * load and store the field
            * solve a loaded field, returning if it was solvable or not
            * retrieve the difficulty level frequencies and the number
                of solvable and unsolvable fields
        
        The field object must have methods to:
            * retrieve the value of a cell at a certain coordinate
                free, flag, zero, number
            * list all neighbours as a list of coordinates
            * flag a certain free cell and decrease the flags left
                count
            * reveal a certain free cell
            * retrieve the number of flags left (attribute rather than
                method)
            * list all coordinates
        
        The solver object will have certain functions:
            * possibility combinator
            * general conflict checker
            * recursive consequence detector
            * cell solver function
            * solver loop
            * rule 9 brute-forcer
            * main loop
    
        The consequence checker is the only function that could also
        check if increasing the variable i would make any difference.
        
        The consequence checker would in that case return a tuple of:
            * a boolean that specifies if a parent possibility is
                Impossible after considering the child possibilities
            * and an integer that specifies the deepest recursion
                detected.
        And it will take three arguments:
            * the coordinate of the parent cell,
            * one of the parent possibilities
            * and a recursion count-down integer (i).
        
    
    11 The field object
       ================

        The field object is what will be manipulated by the algorithm.
        There are a few demands on certain methods and attributes.
        
        A coordinate is a coordinate to a cell in the field, it can be
        any type that:
            * can be hashed and
            * can be checked for equality and
            * can be put in a list. (Are there any that can't?)
        But it doesn't have to be a coordinate in the traditional sense
        of (x, y).
            * Hexagonal grid? No problem.
            * 3-dimensional? No problem.
            * Von-Neumann neighbourhood? No problem.
            * Something weird? Also, no problem.
        
        Because of the very generic coordinate data type, the field
        object MUST provide certain methods:
            field.all_cells() MUST return a list of the coordinates for
                each and every cell.
            
            field.get_neighbours(coordinate) MUST return a list of
                coordinates for each neighbour to `coordinate`.
        
        Obviously, it has to provide I/O to the field.
            field.get(coordinate) MUST return:
                'F' if the cell at coordinate is a flagged cell.
                None if the cell at coordinate is a free cell.
                A non-negative integer if the cell is a number cell.
                    (Zero is a number, but it is usually rendered as
                    blank on the screen.)
                This method MAY return 'X' if it is a mine that has
                been revealed.  Doing so will cause the solver to crash
                due to an AssertionError.
            
            field.flag(coordinate) MUST flag the cell at coordinate if
                it was a free cell.
                If the field does count the number of flags left, this
                method MUST also decrease the flags left count.
            
            field.reveal(coordinate) MUST reveal (click) the free cell
                at coordinate.  Ie the value returned by `get` will
                become an integer when the cell has been revealed.
                This method SHOULD automatically expand the area if a
                zero was revealed, because:
                    0. It's probably faster than letting the solver do
                        it.
                    1. It would mess up the difficulty measurement.
                    2. The same function is usually used by the actual
                        game.
        
        Apart from the actual field, there is also the optional flags
        left count.  field.flags_left is an integer if it is available,
        but `None` if it is not.
'''

import time

class solver():
    '''
    The reason why this is a class rather than a function is quite
    simple:  I didn't want to send the same argument (field) to
    a big bunch of functions.
    
    
    solve
    =====
    
        In order to solve one or more fields, you'll need a solver
        object.
            s = minesweeper_solve.solver()
        
            field = minesweeper.generic_field([10, 10])
            # Place the mines.
        
        The `solve` method can't solve a field from scratch, you MUST
        reveal some starting cells.
            field.reveal(a_good_coordinate)
        
        To solve a field, you first need to load it (OR A COPY),
            s.field = field
        and then you call the `solve` method.
            success, difficulty_levels = s.solve()
        
        NOTICE:  The `solve` method will manipulate the field object,
        it will literally solve it (or fail to do so).
        
        If `success` is True, the entire field has been COMPLETELY
        solved without guessing.
        
        If `success` is False, the field has been PARTIALLY solved.
        (Or in rare and stupid cases, NOT AT ALL.)
        
        The return values will also be appended as a tuple in
        `s.statistics`.
    
    
    measure
    =======
    
            success, difficulty_levels = s.solve()
        `difficulty_levels` is a dictionary whose keys are the
        different levels of difficulty in solving the field, and their
        values are the frequency of the levels.
        
        The special level 'T' is the time it took.
        
        NOTICE:  The levels do not match the levels of difficulty that
        a neural network would experience.
        
        NOTICE:  The levels -1 and -2 have special meanings.  And
        especially -2 does NOT mean "ridiculously" easy.
    
    '''
    
    def __dir__(self):
        return [
            '__init__',
            '__dir__',
            'field',
            'statistics',
            'solve',
        ]
    
    def __hash__(self):
        return id(self)
    
    def __init__(self):
        '''
        (You need to use a `solver` OBJECT.)
        '''
        self.field = None
        self.statistics = []
    
    def combinator(self, elements, n):
        '''
        List of combinations of `n` elements from `elements`.
        
        (Each returned combination is a list.)
        '''
        n -= 1
        if n:
            combinations = []
            for i in range(len(elements)):
                for tail in self.combinator(elements[i + 1:], n):
                    combinations += [[elements[i]] + tail]
        else:
            combinations = [[element] for element in elements]
        return combinations
    
    def number_neighbours(self, cells):
        '''
        Return a list of the coordinates for the number neighbours to
        every cell.  (Not for each cell, but as one common bunch.)
        '''
        neighbours = []
        for cell in cells:
            for neighbour in self.field.get_neighbours(cell):
                assert self.field.get(neighbour) != 'X'
                if self.field.get(neighbour) not in (None, 'F'):
                    if neighbour not in neighbours:
                        neighbours.append(neighbour)
        return neighbours
    
    def conflict(self, new_flags, exact=False):
        '''
        Check if there is a conflict with the flag count.
        
        `new_flags` is a list of coordinates for the flags that might
        cause a conflict.
        
        Returns True if there would be a conflict,
        and False if there wouldn't be.
        
        The function will return True if `exact` is True and there are
        too few flags. (Doesn't care about the count of free
        neighbours.)
        
        '''
        # Find number neighbours to all new flags.
        neighbours = self.number_neighbours(new_flags)
        # Iterate over each neighbour.
        for neighbour in neighbours:
            # Count the flags and frees and target.
            target = self.field.get(neighbour)
            flag_count = free_count = 0
            for maybe_flag in self.field.get_neighbours(neighbour):
                derefed_maybe_flag = self.field.get(maybe_flag)
                if maybe_flag in new_flags or derefed_maybe_flag == 'F':
                    flag_count += 1
                if derefed_maybe_flag is None:
                    free_count += 1
            # Check for conflict. Too many or not room for enough.
            if flag_count > target or free_count < target - flag_count:
                return True
            if flag_count < target and exact:
                return True
        # Hopefully reached.
        return False
    
    def possibilities(self, cell, parent_possibility, count_flags=False):
        '''
        Return a list of combinations of coordinates where the
        remaining mines around the `cell` can be.
        
        `parent_possibility` can provide additional
        (imaginary/planning) flags.
        
        If `count_flags` is True, any possibility with too many mines
        will be eliminated.
        '''
        # BUG: This function behaves differently in PyPy
        #print(cell, parent_possibility, count_flags)
        neighbours = []
        flags = 0
        for neighbour in self.field.get_neighbours(cell):
            if neighbour in parent_possibility:
                flags += 1
            else:
                if self.field.get(neighbour) is None:
                    neighbours.append(neighbour)
                if self.field.get(neighbour) is 'F':
                    flags += 1
        # How many are needed?
        needed = self.field.get(cell) - flags
        if needed:
            # Place the flags.
            all_possibilities = self.combinator(
                neighbours,
                needed
            )
        else:
            all_possibilities = [[]]
        # Eliminate direct conflicts.
        filtered =  list(filter(
            lambda x: not self.conflict(parent_possibility + x),
            all_possibilities
        ))
        if count_flags:
            if self.field.flags_left is not None:
                filtered = list(filter(
                    lambda x: len(parent_possibility + x) <= self.field.flags_left,
                    filtered
                ))
        #print(filtered)        # Differs
        return filtered
    
    def bad_consequences(self, parent_cell, parent_possibility, i, count_flags):
        '''
        `parent_possibility` is one of the primary possibilities for
        `parent_cell`.
        
        `i` is the number of recursions. This function will do nothing
        if `i` is zero.
        
        Returns (impossible, depth)
        `impossible` is a boolean that tells about the
        `parent_possibility`.
        `depth` is a counter that indicates if the value of `i` is
        unnecessarily high.  If `depth` is not zero, `impossible`
        will not become True for a higher value of `i`.
        
        If `count_flags` is True, any possibility with too many mines
        will be eliminated.
        '''
        if i == 0:
            return False, 0
        
        i -= 1
        deepest = i
        
        # All number neighbours to all (any-form-of) neighbours to the parent
        # cell are relevant.
        child_cells = self.field.get_neighbours(parent_cell)
        child_cells = self.number_neighbours(child_cells)
        child_cells = list(filter(lambda x: x != parent_cell, child_cells))
        # If the parent cell itself could be included, it would allow a
        # secondary possibility to be identical to the primary
        # possibility, forcing it to be possible.
        
        # If ANY child has NO possibilities,
        # the parent possibility is impossible.
        for child in child_cells:
            child_possibilities = self.possibilities(
                child,
                parent_possibility,
                count_flags
            )
            if not child_possibilities:
                return True, deepest
            if i:
                # Recurse? (for each child possibility)
                for child_possibility in child_possibilities:
                    impossible, depth = self.bad_consequences(
                        child,
                        parent_possibility + child_possibility,
                        i,
                        count_flags
                    )
                    # Track the depth.
                    if depth > deepest:         # Seems to be correct.
                        deepest = depth
                    if not impossible:
                        break
                else:
                    # All were impossible
                    return True, deepest
        return False, deepest
    
    def cell_solver(self, cell, difficulty):
        '''
        `cell` is the cell to be solved.
        
        difficulty = 4*i + mode
        
        `i` is the number of recursions made to check if a possibility
        has unwanted consequences.
        i = 0: Do not check the consequences at all.
        
        `mode`
        ------
        
            0           Solve iff there is ONE possibility
            1           Flag and reveal only the neighbours that are
                        certain to be flags and numbers.
            2           Solve iff there is one possibility after
                        eliminating those that had tooo many mines.
            3           1 + 2 = 3
        
        Returns
        -------
            Confirmed/plausible/busted
            'C'         if the cell is solved
            'P'         if the cell could be solved at a
                        higher level of difficulty
            'B'         if the cell can't be solved
        '''
        # i is the level of recursion
        # j is the mode
        #       0       single possibility
        #       1       constants
        #       2       limited by flagcount
        #       3       1 + 2
        
        i = difficulty >> 2
        j = difficulty & 3
        
        # Find possibilities, do the recursions and detect recursion max-outs.
        possibilities = []
        recursion_maxout = True
        for possibility in self.possibilities(cell, []):
            impossible, depth = self.bad_consequences(
                cell, possibility, i, j & 2
            )
            if not impossible:
                possibilities.append(possibility)
            if not depth:
                recursion_maxout = False
        
        # Generate a list of flags to be marked and numbers to be revealed.
        flags = []
        numbers = []
        if (j & 1):
            assert len(possibilities) > 1, """
                Cell already solved?? {}
            """.format(possibilities)
            
            # Find constant cells.
            # Find all neighbours.
            # Values
            #   None: unassigned
            #   'F': flag
            #   'N': number
            #   'U': uncertain
            constants = {}
            for neighbour in self.field.get_neighbours(cell):
                constants[neighbour] = None
            
            # Assign 'F', 'N' and 'U'
            for possibility in possibilities:
                for neighbour in constants:
                    if neighbour in possibility:
                        # Flag.
                        if constants[neighbour] is None:
                            constants[neighbour] = 'F'
                        if constants[neighbour] == 'N':
                            constants[neighbour] = 'U'
                    else:
                        # Number.
                        if constants[neighbour] is None:
                            constants[neighbour] = 'N'
                        if constants[neighbour] == 'F':
                            constants[neighbour] = 'U'
            
            # Find 'F's and 'N's.
            for neighbour in constants:
                if constants[neighbour] == 'F':
                    flags.append(neighbour)
                if constants[neighbour] == 'N':
                    numbers.append(neighbour)
                
        elif len(possibilities) == 1:
            # There is only one possibility left.
            for neighbour in self.field.get_neighbours(cell):
                if neighbour in possibilities[0]:
                    flags.append(neighbour)
                else:
                    numbers.append(neighbour)
        
        # Filter out pre-existing numbers.
        numbers = list(filter(lambda x: self.field.get(x) is None, numbers))
        
        # Mark flag cells and reveal number cells.
        for flag in flags:
            self.field.flag(flag)
        for number in numbers:
            self.field.reveal(number)
        
        # Return confirmed/plausible/busted
        if len(flags) + len(numbers):
            return 'C'
        elif recursion_maxout:
            return 'B'
        else:
            return 'P'
    
    def unsolved(self, cell):
        '''
        Is the `cell` unsolved? True/False
        '''
        if self.field.get(cell) not in ('F', None):
            for neighbour in self.field.get_neighbours(cell):
                if self.field.get(neighbour) is None:
                    return True
        return False
    
    def solver_loop(self):
        '''
        This will solve the field according to rules 0 to 7.
        
        This function returns True if the field was solved.
        There may still be deserted mines. -- See rule 8.
        
        This function returns a boolean that tells if the field was
        successfully solved and a dictionary for the difficulty levels.
        
        The keys in the dictionary are the levels of difficulty
        according to rule 6 and their values are the frequencies of the
        level of difficulty.
        
        There may still be deserted mines.  See rules 8 and 9.
        '''
        def rank_cell(cells, i):
            '''
            Count the number cells in the area 3 + 2*i by 3 + 2*i.
            
            When used to rank a cell, the cell to be ranked must be
            alone in a list.
            '''
            more_cells = cells + self.number_neighbours(cells)
            if i:
                return rank_cell(more_cells, i - 1)
            else:
                return len(more_cells)
        
        difficulty_levels = {}
        
        while True:
            i = -1      # The increment is in the beginning of the loop
                        # for readability.
            # Come back to this loop whenever a cell has been confirmed.
            confirmed = False
            while not confirmed:
                i += 1
                # As the value of `i` increases, the area of clues
                # increases too.
                # Recollect and re-sort the list of unsolved cells.
                unsolved_cells = []
                for cell in self.field.all_cells():
                    if self.unsolved(cell):
                        unsolved_cells.append((cell, rank_cell([cell], i)))
                unsolved_cells.sort(key=lambda x: x[1], reverse=True)
                # Check for success right here.
                if not unsolved_cells:
                    return True, difficulty_levels
                # If nothing succeeds before the j loop finishes,
                # the function will return False.
                fail = True
                for j in range(4):
                    for cell, ignored in unsolved_cells:
                        # It may have been solved already.
                        if self.unsolved(cell):
                            status = self.cell_solver(cell, 4*i + j)
                            if status != 'B':
                                fail = False
                            if status == 'C':
                                if (4*i + j) not in difficulty_levels:
                                    difficulty_levels[4*i + j] = 0
                                difficulty_levels[4*i + j] += 1
                                confirmed = True
                                fail = False
                                break
                    # Double break when confirmed.
                    if confirmed:
                        break
                if fail:
                    return False, difficulty_levels
    
    def rule9bf(self):
        '''
        Return True if the field can be solved according to rule 9.
        '''
# Solved in 0.0.25, BUG is available in 0.0.24 and below:
#        A bug in anonymine_solver.py (solver.rule9bf) has been fixed,
#        the symptoms of this bug haven't occured since the fix.
#        (At least 717708 fields (30x16 with 99 mines) have been tested.)
#    Symptoms:
#        Of some reason, this function might reveal a mine.
#    Traceback:
#        Traceback (most recent call last):
#          File "<stdin>", line 1, in <module>
#          File "/usr/lib/python2.7/cProfile.py", line 29, in run
#            prof = prof.run(statement)
#          File "/usr/lib/python2.7/cProfile.py", line 135, in run
#            return self.runctx(cmd, dict, dict)
#          File "/usr/lib/python2.7/cProfile.py", line 140, in runctx
#            exec cmd in globals, locals
#          File "<string>", line 1, in <module>
#          File "test.py", line 39, in run_prof
#            won, levels = solver.solve()
#          File "anonymine_solver.py", line 1105, in solve
#            success, update_difficulty = self.solver_loop()
#          File "anonymine_solver.py", line 957, in solver_loop
#            unsolved_cells.append((cell, rank_cell([cell], i)))
#          File "anonymine_solver.py", line 934, in rank_cell
#            more_cells = cells + self.number_neighbours(cells)
#          File "anonymine_solver.py", line 638, in number_neighbours
#            assert self.field.get(neighbour) != 'X'
#        AssertionError
        
        # Sanity checking.
        if self.field.flags_left is None:
            return False
        # Find the unsolved cells.
        unsolved_cells = []
        for cell in self.field.all_cells():
            if self.unsolved(cell):
                unsolved_cells.append(cell)
        # Find the cells to be brute-forced.
        # They are free cells that are neighbours to the unsolved cells.
        # ### AND
        # Find the deserted cells.
        # As per definition: free cells that are not neighbours to
        # unsolved cells.
        bruteforce_cells = []
        deserted_cells = []
        for cell in self.field.all_cells():
            if self.field.get(cell) is None:
                for unsolved_cell in unsolved_cells:
                    if cell in self.field.get_neighbours(unsolved_cell):
                        bruteforce_cells.append(cell)
                        break # Fix another bug as well. # 0.0.25
                else:
                    # 0.0.25
                    # The BUG WAS here. The 'else' statement belonged to the
                    # 'if' statement rather than to the 'for' statement.
                    # Check the comment at the top of this function.
                    deserted_cells.append(cell)
        
        # Check that there are deserted cells. (Late sanity checking)
        if not len(deserted_cells):
            return False
        
        # Begin brute-forcing.
        lowest = None
        L = len(bruteforce_cells)
        # 1 <= n <= 2^L - 2
        # The real ends (0, 2^L - 1) are either impossible or obvious.
        n = 1
        stop = (1 << L) - 1
        # Check if it is even possible for any possibility to exist.
        if L - 1 < self.field.flags_left:
            return False
        while n < stop:
            # Assemble mines and numbers.
            possibility = []
            for i in range(L):
                if n & (1 << i):
                    possibility.append(bruteforce_cells[i])
            # Check if the possibility is possible.
            if not self.conflict(possibility, True):
                # Keep track of the min() value of all possibilities
                # in REAL TIME
                if lowest is None or len(possibility) < lowest:
                    lowest = len(possibility)
                    if lowest < self.field.flags_left:
                        # One/some of the deserted cells could be a mine.
                        return False
            # Next possibility:
            n += 1
        
        # Verifying that no possibility could allow mines among the
        # deserted cells, after brute forcing, was way too slow.
        
        assert lowest == self.field.flags_left
        
        # There is a chance if the function hasn't returned yet.
        for deserted_cell in deserted_cells:
            self.field.reveal(deserted_cell)
        return True
    
    def solve(self):
        '''
        NOTE to self:  This is copy-pasted.
        
        
        In order to solve one or more fields, you'll need a solver
        object.
            s = minesweeper_solve.solver()
        
            field = minesweeper.generic_field([10, 10])
            # Place the mines.
        
        The `solve` method can't solve a field from scratch, you MUST
        reveal some starting cells.
            field.reveal(a_good_coordinate)
        
        To solve a field, you first need to load it (OR A COPY),
            s.field = field
        and then you call the `solve` method.
            success, difficulty_levels = s.solve()
        
        NOTICE:  The `solve` method will manipulate the field object,
        it will literally solve it (or fail to do so).
        
        If `success` is True, the entire field has been COMPLETELY
        solved without guessing.
        
        If `success` is False, the field has been PARTIALLY solved.
        (Or in rare and stupid cases, NOT AT ALL.)
        
        The return values will also be appended as a tuple in
        `s.statistics`.
        
        
        NOTE to self:  This is copy-pasted.
        '''
        
        start_time = time.time()
        
        difficulty_levels = {}
        done = False
        while not done:
            # Use the ordinary solver loop at first.
            success, update_difficulty = self.solver_loop()
            # Use rules 8 and 9 if necessary.
            if self.field.flags_left is None:
                done = True
            else:
                # Find deserted cells.
                deserted_cells = []
                for cell in self.field.all_cells():
                    if self.field.get(cell) is None:
                        deserted_cells.append(cell)
                if success:
                    # Rule 8.
                    if len(deserted_cells):
                        update_difficulty[-1] = 1   # Key -1 has not been used.
                        if len(deserted_cells) == self.field.flags_left:
                            # All are mines.
                            for cell in deserted_cells:
                                self.field.flag(cell)
                        elif self.field.flags_left == 0:
                            # None are mines.
                            for cell in deserted_cells:
                                self.field.reveal(cell)
                        else:
                            success = False
                    done = True
                elif deserted_cells:
                    # Rule 9
                    update_difficulty[-2] = 1       # Key -2 has not been used.
                    if not self.rule9bf():
                        success = False
                        done = True
                else:
                    # Rare, but possible case.
                    success = False
                    done = True
            # Update the difficulty levels.
            for key in update_difficulty:
                if key in difficulty_levels:
                    difficulty_levels[key] += update_difficulty[key]
                else:
                    difficulty_levels[key] = update_difficulty[key]
        # Done.
        difficulty_levels['T'] = time.time() - start_time
        ret = success, difficulty_levels
        self.statistics.append(ret)
        return ret

import os
import sys
assert os.geteuid() or sys.platform.startswith('haiku'), "Gaming as root!"
assert __name__ != '__main__', "I'm not a script."
