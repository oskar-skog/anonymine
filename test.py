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
'''

import time
import sys
import anonymine_fields
import anonymine_solver
import anonymine_engine
import random
import signal
import pprint
import os

def output(field, argument):
    print(field)
    time.sleep(.04)     # 25 Hz

def pypybug():
    size = [5, 5]
    start = (1, 1)
    mines = [(3, 4), (4, 4), (4, 0)]
    field = anonymine_fields.generic_field(size, True, True)
    solver = anonymine_solver.solver()
    solver.field = field
    field.fill(mines)
    field.reveal(start)
    field.set_callback('input', output, None)
    print(field)
    print(solver.solve())

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

def profile_solver(x, y, m):
    field = anonymine_fields.generic_field([x, y])
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
    solver.solve()

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

def init_time(width, height, n_mines, runs=10):
    i = 0
    dellen = 0
    times = []
    while i < runs:
        i += 1
        e = anonymine_engine.game_engine(
            'testcfg',
            width=width, height=height, mines=n_mines
        )
        coord = random.randint(0, width - 1), random.randint(0, height - 1)
        start = time.time()
        try:
            e.init_field((coord))
        except anonymine_engine.security_alert as e:
            sys.stderr.write('\n{}\n'.format(e.message))
        x = time.time() - start
        del e
        times.append(x)
        times.sort()
        msg = '{}: {}  This: {}  Avg: {}  Median: {}  Min/Max: {}/{}'.format(
            '{}@{}x{}'.format(n_mines, width, height),
            '{}/{}'.format(i, runs),
            x,
            sum(times)/len(times),
            times[len(times)//2],
            times[0], times[-1],
        )
        #sys.stderr.write('\b' * dellen)
        sys.stderr.write('\x1b[2K\r')
        dellen = len(msg) + 1
        sys.stderr.write(msg)
        sys.stderr.flush()
    sys.stderr.write('\n')
    return times


def init_time_curve():
    data = eval(open('init-time.curve').read())[:90]
    for i in range(90, 121):
        x = init_time(20, 20, i, 100)
        data.append(x)
        f = open('init-time.curve', 'w')
        f.write(pprint.pformat(data))
        f.close()


def run2(path):
    f = open(path, 'w')
    data = {
         '20@10x10': init_time(10, 10,  20, 1000),
         '80@20x20': init_time(20, 20,  80, 1000),
        '180@30x30': init_time(30, 30, 180, 1000),
    }
    f.write(pprint.pformat(data))
    f.close()

def chance(width, height, n_mines, runs):
    spinner = '\\|/-'
    solver = anonymine_solver.solver()
    field = anonymine_fields.generic_field([width, height])
    solver.field = field
    
    starttime = time.time()
    
    i = 0
    success = 0.0
    while i < runs:
        i += 1
        mines = field.all_cells()
        random.shuffle(mines)
        field.clear()
        field.fill(mines[:n_mines])
        for mine in mines[n_mines:]:
            for neighbour in field.get_neighbours(mine):
                if neighbour in mines[:n_mines]:
                    break
            else:
                field.reveal(mine)
                break
        progress = int(40.0 * i/runs)
        success += solver.solve()[0]
        
        ETA = (runs - i) * (time.time() - starttime)/i
        
        sys.stderr.write('\x1b[2K\r{}@{}x{}:\t{}%\t[{}{}]{}\tETA: {}+{}'.format(
            n_mines, width, height,
            int(100.0 * success/i + 0.5),
            '=' * progress, ' ' * (40 - progress),
            spinner[i % len(spinner)],
            int(ETA/86400), time.strftime('%H:%M:%S', time.gmtime(ETA))
        ))
    sys.stderr.write('\n')
    return success/runs

def run3(path):
    os.system('clear')
    f = open(path, 'w')
    #data = {
        #'20@10x10':  chance(10, 10,  20, 1000),
        #'45@15x15':  chance(15, 15,  45, 1000),
        #'80@20x20':  chance(20, 20,  80, 1000),
        #'125@25x25': chance(25, 25, 125, 1000),
        #'180@30x30': chance(30, 30, 180, 1000),
        #'245@35x35': chance(35, 35, 245, 1000),
        #'320@40x40': chance(40, 40, 320, 1000),
        #'405@45x45': chance(45, 45, 405, 1000),
        #'500@50x50': chance(50, 50, 500, 1000),
    #}
    data = {}
    times = {}
    #for x in (20, 40, 80, 160):
    #for x in (120, 60, 30, 15):
    for x in (100, 50, 25):
        mines = int(.2 * x**2)
        key = '{}@{}x{}'.format(mines, x, x)
        start = time.time()
        #data[key] = chance(x, x, mines, 3000)
        data[key] = chance(x, x, mines, 2000)
        times[key] = time.time() - start
    
    f.write(pprint.pformat({'times': times, 'data': data}))
    f.close()
