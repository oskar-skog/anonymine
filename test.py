#!/usr/bin/python

'''
`runmoore`, `runhex` and `runneumann` are demos to be played in a
80x24 terminal.  The `output` function sets the output frequency.
    runmoore(x=78, y=18, m=225)
    runhex(x=39, y=18, m=112)
    runneumann(x=78, y=18, m=225)

`slomobug` simulates a field known to trigger the bug discovered in
0.0.24 (fixed since 0.0.25).

`run623` is a generic field of 6x6x6 with 22 mines.

`run10` appears to be collecting some statistics of a 16x16 with 40 mines.

`bug1` should be explained in the file "BUGS".
'''

import time
import sys
import anonymine_fields
import anonymine_solver
import anonymine_engine
import random
import signal
import pprint
import cProfile

def output(field, argument):
    print(field)
    time.sleep(.04)     # 25 Hz

def slomobug():
    print('A')
    mines = [(28,5),(4,8),(16,3),(0,1),(25,4),(5,13),(12,6),(22,2),(15,6),
(14,5),(7,9),(22,4),(29,4),(14,14),(8,10),(24,0),(15,12),(8,15),(24,9),(13,3),
(2,13),(14,4),(6,1),(27,8),(6,6),(20,9),(2,8),(23,4),(22,11),(24,1),(5,2),
(0,3),(9,3),(29,7),(11,0),(11,8),(14,10),(14,11),(12,7),(7,8),(4,0),(5,15),
(22,12),(28,10),(0,12),(22,10),(6,10),(6,3),(26,2),(20,15),(2,12),(28,6),
(13,11),(23,9),(16,5),(26,6),(12,0),(16,15),(11,9),(26,12),(22,8),(4,1),(28,7),
(6,4),(16,11),(17,13),(2,7),(5,6),(0,11),(0,15),(21,7),(27,10),(28,9),(0,2),
(6,5),(27,9),(17,1),(25,8),(4,14),(2,6),(6,15),(26,11),(18,15),(9,4),(15,13),
(20,4),(18,9),(15,7),(2,9),(24,2),(16,7),(28,0),(5,14),(21,14),(29,5),(23,0),
(23,10),(9,2),(20,7)]
    start = (9, 13)
    field = anonymine_fields.generic_field([30, 16], True, True)
    solver = anonymine_solver.solver()
    solver.field = field
    field.fill(mines)
    field.reveal(start)
    field.set_callback('input', output, None)
    print(field)
    print(solver.solve())

def runmoore(x=78, y=18, m=225):
    field = anonymine_fields.generic_field([x, y])
    field.set_callback('input', output, None)
    print(field)
    mines = field.all_cells()
    random.shuffle(mines)
    field.fill(mines[:m])
    
    for mine in mines[m:]:
        for neighbour in field.get_neighbours(mine):
            if neighbour in mines[:m]:
                break
        else:
            field.reveal(mine)
            break
    
    solver = anonymine_solver.solver()
    solver.field = field
    
    print(solver.solve())

def run623():
    field = anonymine_fields.generic_field([6, 6, 6])
    
    mines = field.all_cells()
    random.shuffle(mines)
    field.fill(mines[:22])
    
    field.reveal(mines[22])
    
    solver = anonymine_solver.solver()
    solver.field = field
    ret = solver.solve()
    if ret[0]:
        print(field.field)
    print(ret)

def runneumann(x=78, y=18, m=225):
    field = anonymine_fields.generic_field([x, y], False)
    field.set_callback('input', output, None)
    
    mines = field.all_cells()
    random.shuffle(mines)
    field.fill(mines[:m])
    
    for mine in mines[m:]:
        for neighbour in field.get_neighbours(mine):
            if neighbour in mines[:m]:
                break
        else:
            field.reveal(mine)
            break
    
    solver = anonymine_solver.solver()
    solver.field = field
    print(solver.solve())

def runhex(x=39, y=18, m=112):
    field = anonymine_fields.hexagonal_field(x, y)
    field.set_callback('input', output, None)
    
    mines = field.all_cells()
    random.shuffle(mines)
    field.fill(mines[:m])
    
    for mine in mines[m:]:
        for neighbour in field.get_neighbours(mine):
            if neighbour in mines[:m]:
                break
        else:
            field.reveal(mine)
            break
    
    solver = anonymine_solver.solver()
    solver.field = field
    print(solver.solve())

def run10():
    solver = anonymine_solver.solver()
    field = anonymine_fields.generic_field([16, 16])
    solver.field = field
    
    times = []
    ttimes = []
    
    while solver.need_more_data(2, 2, 5, 12):
        mines = field.all_cells()
        random.shuffle(mines)
        field.fill(mines[:40])
        for mine in mines[40:]:
            for neighbour in field.get_neighbours(mine):
                if neighbour in mines[:40]:
                    break
            else:
                field.reveal(mine)
                break
        
        start = time.time()
        solver.solve()
        this_time = time.time() - start
        
        times.append(this_time)
        if this_time < 3:
            ttimes.append(this_time)
        
        field.clear()
    print(solver.chance())
    print(solver.cumulated_levels_total())
    print(solver.cumulated_levels_success())
    print(min(times), sum(times)/len(times), max(times), len(times))
    print(min(ttimes), sum(ttimes)/len(ttimes), max(ttimes), len(ttimes))

def bug1():
    # BUG:
    #       sys.stdin.readline() in `ask` dies with IOError and
    #       errno=EINTR when the terminal gets resized after curses has
    #       been de-initialized.
    #       1: SIGWINCH is sent by the terminal when the screen has been
    #           resized.
    #       2: curses forgot to restore the signal handling of SIGWINCH
    #           to the default of ignoring the signal.
    #           NOTE: signal.getsignal(signal.SIGWINCH) incorrectly
    #               returns signal.SIG_DFL. (Default is to be ignored.)
    #       3: Python fails to handle EINTR when reading from stdin.
    # REFERENCES:
    #       Issue 3949: https://bugs.python.org/issue3949
    #       PEP 0457: https://www.python.org/dev/peps/pep-0475/
    def handler(foo, bar):
        print("Resized")
    signal.signal(signal.SIGWINCH, handler)
    while True:
        sys.stdin.readline()
    