#!/usr/bin/python
# -*- coding: utf-8 -*-

import anonymine_fields
import anonymine_solver
import sys
import time
import random
import pprint
import traceback


def main():
    def mk_bug_file():
        f = open(time.strftime('BUG_%Y-%m-%dT%H:%M:%S', time.gmtime()), 'w')
        d = {
            'start': start,
            'mines': mines[:99],
            'post-solve': str(field.field),
            'exception': ''.join(traceback.format_exception(*sys.exc_info()))
        }
        f.write(pprint.pformat(d))
        f.close()
    field = anonymine_fields.generic_field([30, 16])
    solver = anonymine_solver.solver()
    solver.field = field
    mines = field.all_cells()
    fields = wins = games = bugs = 0
    while True:
        fields += 1
        random.shuffle(mines)
        field.clear()
        field.fill(mines[:99])
        for mine in mines[99:]:
            for neighbour in field.get_neighbours(mine):
                if neighbour in mines[:99]:
                    break
            else:
                field.reveal(mine)
                start = mine
                break
        else:
            assert False, "No startpoint"
        # Hopefully, the bug is above.
        try:
            win, ignore = solver.solve()
            games += 1
            if win:
                wins += 1
        except KeyboardInterrupt:
            try:
                sys.stdout.write('Press enter to continue, ^C again to quit.\n')
                sys.stdin.readline()
            except KeyboardInterrupt:
                sys.exit(0)
        except AssertionError as e:
            mk_bug_file()
            bugs += 1
            sys.stdout.write('\n{}/{}\n'.format(bugfiles, fields))
        except:
            mk_bug_file()
            raise
        sys.stdout.write(
            '{}/{} games won ({}‰);\t'
            '{}/{} fields trigger the bug ({} ppm)\n'.format(
                wins, games, int(1000.0 * float(wins)/games + 0.5),
                bugs, fields, int(1000000.0 * float(bugs)/fields + 0.5),
            )
        )
     

if __name__ == '__main__':
    main()
