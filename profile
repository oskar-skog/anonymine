Wed Jan  6 23:32:28 2016    test.run_prof-prof

         4817699751 function calls (4533179300 primitive calls) in 1738.699 seconds
50 fields in 1738.699 seconds.

   Ordered by: internal time

   ncalls               tottime         percall       cumtime           percall         filename:lineno(function)

293116847/74555208    334.113           0.000         404.386           0.000           anonymine_fields.py:295(moore)
 74555208             230.337           0.000         976.642           0.000           anonymine_fields.py:265(get_neighbours)
                                                                                            Implemented caching: speed *= 2.58

838570345             284.634           0.000         419.056           0.000           anonymine_fields.py:214(get)
                                                                                            Fixed along with _deref.

651197099             168.044           0.000         168.044           0.000           anonymine_fields.py:307(<lambda>)

  9176760             166.369           0.000        1463.178           0.000           anonymine_solver.py:643(conflict)
                                                                                            Won't fix.

838793260             134.458           0.000         134.458           0.000           anonymine_fields.py:173(_deref)
                                                                                            Fixed for other reasons.
                                                                                            Same performance.

  9572842             106.960           0.000         559.910           0.000           anonymine_solver.py:630(number_neighbours)
                                                                                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

83822126/19152728      90.339           0.000        1510.604           0.000           {filter}
1530093954             84.271           0.000          84.271           0.000           {method 'append' of 'list' objects}
 74562368              52.356           0.000          52.356           0.000           {map}

  9173571               6.170           0.000        1468.819           0.000           anonymine_solver.py:712(<lambda>)
  6183118              35.583           0.000        1642.744           0.000           anonymine_solver.py:679(possibilities)
                                                                                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

305845712              16.840           0.000          16.840           0.000           {len}
 75029175              11.158           0.000          11.158           0.000           {range}

347126/163945           5.480           0.000        1677.186           0.010           anonymine_solver.py:723(bad_consequences)
                                                                                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

  3402621               3.953           0.000          28.760           0.000           anonymine_solver.py:901(unsolved)
221898/7158             1.968           0.000           2.481           0.000           anonymine_fields.py:332(list_cells)
2056296/1178225         1.618           0.000           1.672           0.000           anonymine_solver.py:614(combinator)
  3379414               1.357           0.000           1.565           0.000           anonymine_solver.py:718(<lambda>)

       50               0.886           0.018        1735.778          34.716           anonymine_solver.py:911(solver_loop)
                                                                                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

  8000266               0.760           0.000           0.760           0.000           anonymine_solver.py:751(<lambda>)
    59421               0.430           0.000        1697.673           0.029           anonymine_solver.py:785(cell_solver)
       43               0.133           0.003           2.385           0.055           anonymine_solver.py:982(rule9bf)
     7158               0.130           0.000           2.830           0.000           anonymine_fields.py:328(all_cells)
180340/174285           0.126           0.000           5.844           0.000           anonymine_solver.py:927(rank_cell)
       50               0.083           0.002           0.439           0.009           anonymine_fields.py:376(fill)
     6922               0.045           0.000           0.057           0.000           {method 'sort' of 'list' objects}
   119206               0.035           0.000           0.101           0.000           anonymine_solver.py:885(<lambda>)
12511/6674              0.018           0.000           0.061           0.000           anonymine_fields.py:343(reveal)
   174285               0.012           0.000           0.012           0.000           anonymine_solver.py:956(<lambda>)
  1581/51               0.010           0.000           0.012           0.000           anonymine_fields.py:154(init_field)
       50               0.006           0.000           0.007           0.000           /usr/lib/python2.7/random.py:276(shuffle)
       50               0.006           0.000        1738.201          34.764           anonymine_solver.py:1052(solve)
     3054               0.005           0.000           0.006           0.000           anonymine_fields.py:232(flag)
        1               0.004           0.004        1738.699        1738.699           test.py:15(run_prof)
     9522               0.003           0.000           0.003           0.000           anonymine_fields.py:180(_call)
    23950               0.001           0.000           0.001           0.000           {method 'random' of '_random.Random' objects}
       51               0.001           0.000           0.012           0.000           anonymine_fields.py:148(clear)
       51               0.000           0.000           0.000           0.000           anonymine_solver.py:1179(need_more_data)
     1275               0.000           0.000           0.000           0.000           anonymine_solver.py:1194(<lambda>)
        2               0.000           0.000           0.000           0.000           anonymine_solver.py:1149(cumulate_levels)
        1               0.000           0.000           0.000           0.000           {open}
        1               0.000           0.000        1738.699           1738.699           <string>:1(<module>)
        1               0.000           0.000           0.000           0.000           {method 'close' of 'file' objects}
        3               0.000           0.000           0.000           0.000           {method 'format' of 'str' objects}
        3               0.000           0.000           0.000           0.000           {method 'write' of 'file' objects}
        1               0.000           0.000           0.000           0.000           anonymine_solver.py:1139(chance)
       50               0.000           0.000           0.000           0.000           anonymine_solver.py:1166(<lambda>)
        1               0.000           0.000           0.000           0.000           anonymine_fields.py:113(__init__)
       50               0.000           0.000           0.000           0.000           anonymine_solver.py:1174(<lambda>)
       50               0.000           0.000           0.000           0.000           anonymine_solver.py:1146(<lambda>)
        1               0.000           0.000           0.000           0.000           anonymine_solver.py:1168(cumulated_levels_success)
        1               0.000           0.000           0.000           0.000           anonymine_solver.py:607(__init__)
        7               0.000           0.000           0.000           0.000           anonymine_solver.py:1173(<lambda>)
        1               0.000           0.000           0.000           0.000           anonymine_solver.py:1162(cumulated_levels_total)
        1               0.000           0.000           0.000           0.000           {method 'disable' of '_lsprof.Profiler' objects}

===========================================================================================================================================

    Cache neighbours?

Fri Jan  8 01:39:04 2016    test.run_prof-prof-cache-True

         36246812318 function calls (36219843769 primitive calls) in 13450.858 seconds

   Ordered by: cumulative time

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
     1000    0.130    0.000 13439.453   13.439 anonymine_solver.py:1064(solve)
1353018332  399.681    0.000  610.207    0.000 anonymine_fields.py:268(get_neighbours)

--------------------------------------------------------------------------------------------

Fri Jan  8 16:15:58 2016    test.run_prof-prof-cache-False

         92047907787 function calls (86625165200 primitive calls) in 34665.910 seconds

   Random listing order was used

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
      1000    0.135    0.000 34655.374   34.655 anonymine_solver.py:1064(solve)
1418074225 4693.391    0.000 19445.984    0.000 anonymine_fields.py:268(get_neighbours)

-----------------------------
2.58 times as fast with neighbour cache on.

        min     avg     median  max
Win     2.46    2.67    2.46    2.79
Lose    1.77    2.54    2.47    1.84

=========================================================================

Version 0.0.26 multiplies this by ~4, giving ~10 as fast in total.

==========================================================================================================

    Reimplement anonymine_fields.generic_fields.get?
        For other reasons. (_deref)
        Same performance

--------------------------------------------------------------------------------

Mon Jan 18 18:28:00 2016    test.py-prof_generic_field-old

         8695989750 function calls (8683673269 primitive calls) in 3057.403 seconds

   Random listing order was used

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
3927521227  586.175    0.000  586.175    0.000 anonymine_fields.py:193(_deref)
   628835    4.950    0.000    4.950    0.000 {map}
316908062   88.844    0.000  142.866    0.000 anonymine_fields.py:285(get_neighbours)
  4048000    1.088    0.000    1.088    0.000 anonymine_fields.py:334(<lambda>)
 99198740    4.487    0.000    4.487    0.000 {len}
4613885/148835   35.667    0.000   46.112    0.000 anonymine_fields.py:364(list_cells)
  6700101    1.200    0.000    1.200    0.000 {range}
260086/140750    0.327    0.000    0.591    0.000 anonymine_fields.py:375(reveal)
   148835    3.102    0.000   53.665    0.000 anonymine_fields.py:360(all_cells)
 39146888   18.318    0.000 2151.062    0.000 {filter}
404534085   22.576    0.000   22.576    0.000 {method 'append' of 'list' objects}
3605662471 1125.607    0.000 1661.883    0.000 anonymine_fields.py:234(get)
    63608    0.098    0.000    0.125    0.000 anonymine_fields.py:252(flag)
31031/1001    0.247    0.000    0.280    0.000 anonymine_fields.py:174(init_field)

-------------------------------------------------------------------------------------------

Mon Jan 18 21:35:57 2016    test.py-prof_generic_field-new2

         5330782165 function calls (5318277696 primitive calls) in 3070.355 seconds

   Random listing order was used

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
338248948  120.367    0.000  120.367    0.000 anonymine_fields.py:533(_get_raw)
   622914    4.820    0.000    4.820    0.000 {map}
333004257   89.416    0.000  213.501    0.000 anonymine_fields.py:662(get_neighbours)
249861/134120    0.431    0.000    1.182    0.000 anonymine_fields.py:748(reveal)
4430334/142914   34.595    0.000   44.637    0.000 anonymine_fields.py:737(list_cells)
  1365755    0.530    0.000    1.044    0.000 anonymine_fields.py:550(internal_get)
3797270768 1598.826    0.000 1598.826    0.000 anonymine_fields.py:615(get)
 96723970    4.349    0.000    4.349    0.000 {len}
    61075    0.138    0.000    0.310    0.000 anonymine_fields.py:629(flag)
  6568328    1.196    0.000    1.196    0.000 {range}
  4048000    1.090    0.000    1.090    0.000 anonymine_fields.py:709(<lambda>)
   142914    2.993    0.000   51.963    0.000 anonymine_fields.py:733(all_cells)
 40905534   18.529    0.000 2194.876    0.000 {filter}
  1365755    1.050    0.000    2.094    0.000 anonymine_fields.py:547(_set_raw)
412398222   23.008    0.000   23.008    0.000 {method 'append' of 'list' objects}
   191141    0.054    0.000    0.054    0.000 anonymine_fields.py:581(_call)
   139147    0.864    0.000    1.130    0.000 {method 'sort' of 'list' objects}
