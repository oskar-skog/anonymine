#!/bin/sh

# check.sh $(srcdir) $(builddir)

cat > $2check.py << __EOF__
import anonymine_engine

for mode in ('moore', 'hex', 'neumann'):
    engine = anonymine_engine.game_engine(
        'enginecfg',
        width=10, height=10,
        mines=20,
        flagcount=True, guessless=True,
        gametype=mode
    )
    engine.init_field((3,4))
    assert 'X' not in str(engine.field)
__EOF__

cd $1

has_any=0
fail_any=0
assert_ver="import sys; assert sys.version_info[0] == 3 or sys.version_info[1] >= 6"
for interpreter in python2 python3 python; do
    if $interpreter -c "$assert_ver" 2>/dev/null ; then
        has_any=1
        if ! $interpreter $2check.py; then
            fail_any=1
        fi
    fi
done

if [ $has_any -eq 0 ]; then
    echo "No python interpreters found." >/dev/stderr
    exit 42
fi

if [ $fail_any -eq 1 ]; then
    exit 23
fi
