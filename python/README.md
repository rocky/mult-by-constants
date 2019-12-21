[![Build Status](https://travis-ci.org/rocky/mult-by-constants.svg)](https://travis-ci.org/rocky/mult-by-constants)

<!-- markdown-toc start - Don't edit this section. Run M-x markdown-toc-refresh-toc -->
**Table of Contents**

- [Synopsis](#synopsis)
- [Introduction](#introduction)
    - [As a library](#as-a-library)
    - [As a command-line utility](#as-a-command-line-utility)
    - [Instruction Tables](#instruction-tables)
    - [Data Analysis](#data-analysis)
- [Examples](#examples)
    - [Instruction Sequences](#instruction-sequences)
    - [Alpha-beta pruning](#alpha-beta-pruning)
    - [Cache entries](#cache-entries)
- [References](#references)

<!-- markdown-toc end -->

![Instruction-Sequence Costs for the first 5,000 Integers](./graphs/5000-bin-vs-stdcost.svg)

Synopsis
========

Python API:

```Python
from mult_by_const import MultConst, load_yaml, dump, dump_csv, print_instructions

# Figure out a multiplication sequence for n
mconst = MultConst(debug=True)
cost, instrs = mconst.find_mult_sequence(n)
print_instructions(instrs, n, cost)

table_path = "tables/10000-stdcost.txt"
with open(table_path) as in:
	mcache = load_yaml(in)       # Read in YAML table
dump(mcache)                     # Display table

out_path = "tables/10000-stdcost.csv"
with open(out_path, "w") as out:
    dump_csv(mcache)             # Output as CSV for data analysis
```

See also the [_spe86_](./spe86) directory for a C API.

Command-line utility:

```console
$ mult-by-const 51  # Get instruction sequence to multiply by 51
$ mult-by-const -to 100  # Get instruction sequences for positive numbers up to 100
```

See also the directories [_spe86_](./spe86) and [_vinc17/rigo_](./vinc17/rigo) for C programs.

Introduction
============

This repository serves several purposes:

* As a Python library for getting sequences of instructions to perform integer multiplications
* As a command-line utility for doing the same
* As a place to store Optimal instruction-sequence tables, and
* for data analysis

We drill into each of these below.

As a library
------------

First, we have code to compute the mininum number of _shifts_, _adds_, _subtracts_, to multiply a number by a constant integer under different cost models.

The intention in coding is to be a bit flexible to allow for variation in machine architectures. In particular we allow for architectures that have a shift time that varies with the amount to be shifted. And we can handle architectures that don't have a "subtract" operation.

Given this, we can handle, for example, a machine with only the `add` operation, disallowing the `subtract` operation and using a custom shift cost function that varies by the amount shifted. Note: `y = x << 1` is the same as `y = x + x`, and `y = x << 2` would be the same thing as `z = x + x; y = z + z`.

_(Right now there is only a simple cost module where each of these takes unit time.)_

This code can be use as a (Python) library inside a compiler that wants generate efficient sequences of code for multiplication, since searching is pretty fast for smaller numbers: around 0.1 second for numbers under 5 digits. Note that as as numbers get larger the programs slows down combinatorially. For 10 digits, running time is about 5 seconds. But see below.

As a command-line utility
---------------------------

Of course, there may be need to use this outside of a Python library, so we have wrapped that to a command-line program `mult-by-const`. This may be especially useful if you just need compute a single value or a small number of values, possibly using a custom cost model.

The command-line program also allows for the internal cache values to be dumped and loaded in both JSON, and YAML formats. So for really large numbers you can start a computation, save the cache and then at some time later resume the search.

Finally the command-line programs allows you to iterate up to some value, starting from scratch or starting from a previously-computed table. And this leads into the next purpose...

Instruction Tables
-------------------

Instead of using our code to search for sequences, you can use tables that have been previously generatated. This is again suitable for use inside a compiler, or perhaps a general-purpose multiplication routine, which does a table lookup for "small" values. For larger ones a general-purpose routines can use this as a base table from which to do the standard multiplcation algorithm. For example, people learning multiplication learn by rote the multiplication table for pairs of numbers from 0 to 10.

Initially we built the tables using code here. If you find a way to improve entires in the table, please send them along an it will be incorporated into the table.

And having tables also allows us to improve sequences going in the other direction. Rather than start with a number and searching for a sequence as output, we can start with a table
and look numbers that will probably have short sequences and improve the table. We intend to write code for this as well.

Data Analysis
-------------

Having the tables in hand, we can then start analyzing how the optimum sequence grows with the value of a number.


Examples
========

Instruction Sequences
---------------------

First, a very simple example.

```
$ mult-by-const 41
------------------------------------------------------------
Instruction sequence for 41 = 101001, cost:  4:
op: shift(2),   	cost:  1,	value:   4
op: add(1),     	cost:  1,	value:   5
op: shift(3),   	cost:  1,	value:  40
op: add(1),     	cost:  1,	value:  41
============================================================
```

The above sequence consisting of only "shifts" (a multiplication by a power of 2) and "add"s. The number in parenthesis after "shift" gives the shift amount; so `shift(2)` is a multiplication by 2^2=4; `shift(3)` is 2^3=8.

The sequence above follows the "binary sequence" method for computing a multiplication: each 1-bit other than the leading 1-bit becomes a "shift" by some amount followed by an "add" of one; the "shifts" and "adds" alternate. If the number is even, there is also a final "shift" instruction. Since there are three one-bits and the number is odd, this gives 4=2*(3-1) instructions.

If we start out with _x_ in a variable, the sequence computed is x, 4x, (4+1)x=5x, (5x8)x=40x, (40+1)x=41x. Notice that we list these intermediate values at the right of the listing above.

Let's try another number to go deeper into the problem.


```
$ mult-by-const 95
------------------------------------------------------------
Instruction sequence for 95 = 1011111, cost:  4:
op: shift(1),   	cost:  1,	value:   2
op: add(1),     	cost:  1,	value:   3
op: shift(5),   	cost:  1,	value:  96
op: subtract(1),	cost:  1,	value:  95
============================================================
```

Even though we've multipled by a larger number, the number of instructions stays the same! Notice that in the binary representation of the number there were all of those 1-bits at the end. So rather than shifting and adding each one, we computed 96 (binary 1100000) and subtracted 1. Try the above using 495 (111101111 in binary) instead.

Even though we have added "subtract" to our repetoire, we still alternate between shift and a non-shift instruction. It makes sense not to have several consecutive shifts in this cost model where shifting by any amount can be done in a single instruction.

The binary method for numbers under 100 is pretty optimal. If you need a simple general method multiply method for small number, use this.

But the binary method isn't always optimum, even for numbers under 100. Consider for example 51. Using the binary method, which we can force by by using the `--binary-method` or `-b` flag:

```console
$ mult-by-const --binary-method 51
------------------------------------------------------------
Instruction sequence for 51 = 110011, cost:  6:
op: shift(1),   	cost:  1,	value:   2
op: add(1),     	cost:  1,	value:   3
op: shift(3),   	cost:  1,	value:  24
op: add(1),     	cost:  1,	value:  25
op: shift(1),   	cost:  1,	value:  50
op: add(1),     	cost:  1,	value:  51
============================================================
```
we get 6 instructions. But we can do better if we factor 51=17*3:
```console
$ mult-by-const 51
------------------------------------------------------------
Instruction sequence for 51 = 110011, cost:  4:
op: shift(4),   	cost:  1,	value:  16
op: add(1),     	cost:  1,	value:  17
op: shift(1),   	cost:  1,	value:  34
op: add(n),     	cost:  1,	value:  51
============================================================
```

Above, notice that the final instruction is `add(n)` rather than `add(1)` as we have seen before; `add(n)` means that we are adding value of the previous sum, here 17. In other words: 17+34=51.
`subtract(n)` is also possible. You'll see that used if you try a multiplication by 341.


I close this section with a mutiplication by a large number:
```console
$ mult-by-const 12345678
------------------------------------------------------------
Instruction sequence for 12345678 = 101111000110000101001110, cost: 13:
op: shift(6),   	cost:  1,	value:  64
op: add(1),     	cost:  1,	value:  65
op: shift(2),   	cost:  1,	value: 260
op: add(n),     	cost:  1,	value: 325
op: shift(2),   	cost:  1,	value: 1300
op: subtract(1),	cost:  1,	value: 1299
op: shift(5),   	cost:  1,	value: 41568
op: add(n),     	cost:  1,	value: 42867
op: shift(4),   	cost:  1,	value: 685872
op: subtract(1),	cost:  1,	value: 685871
op: shift(3),   	cost:  1,	value: 5486968
op: add(n),     	cost:  1,	value: 6172839
op: shift(1),   	cost:  1,	value: 12345678
============================================================
```

The above took under 0.5 seconds on my computer. A strictly binary method takes about 0.2 seconds but requires 17 instructions rather than 13 instructions: or 30% more.

Notice that there were a 3 factors used to get produced sequence: 5 (to go from 65 to 325),
33 (to go from 1299 to 42867) and 9 (to go from 685871 to 6172839).

The above calculation begins to show the combinatorial nature of the problem.

Alpha-beta pruning
-------------

The way the sequence-finding part of `mult-by-const` works is that it uses [alpha-beta pruning](https://en.wikipedia.org/wiki/Alpha%E2%80%93beta_pruning).

Fill in...

Cache entries
-------------

Fill in...

```console
$ mult-by-const --showcache 341
------------------------------------------------------------
Instruction sequence for 341 = 101010101, cost:  6:
op: shift(2),   	cost:  1,	value:   4
op: add(1),     	cost:  1,	value:   5
op: shift(1),   	cost:  1,	value:  10
op: add(1),     	cost:  1,	value:  11
op: shift(5),   	cost:  1,	value: 352
op: subtract(n),	cost:  1,	value: 341
============================================================
   0: cost:       1;	[constant 0]
   1: cost:       0;	[noop]
   2: cost:       1;	[<< 1]
   3: cost: (0,   2];	[<< 1, +1]
   4: cost:       1;	[<< 2]
   5: cost: (0,   2];	[<< 2, +1]
   6: cost: (1,inf ];	[]
   8: cost: (0,inf ];	[]
  10: cost:       3;	[<< 2, +1, << 1]
  11: cost: (0,   4];	[<< 2, +1, << 1, +1]
  12: cost:       3;	[<< 1, +1, << 2]
  16: cost:       1;	[<< 4]
  17: cost: (0,   2];	[<< 4, +1]
  18: cost: (1,inf ];	[]
  19: cost: (0,   4];	[<< 3, +1, << 1, +1]
  20: cost: (1,inf ];	[]
  21: cost: (0,   4];	[<< 2, +1, << 2, +1]
  22: cost: (1,inf ];	[]
  42: cost: (1,inf ];	[]
  43: cost: (0,   6];	[<< 2, +1, << 2, +1, << 1, +1]
  44: cost: (1,inf ];	[]
  56: cost: (1,inf ];	[]
  57: cost: (0,   4];	[<< 3, -1, << 3, +1]
  58: cost: (1,inf ];	[]
  84: cost: (3,   5];	[<< 2, +1, << 2, +1, << 2]
  85: cost: (0,   6];	[<< 2, +1, << 2, +1, << 2, +1]
  86: cost: (3,   7];	[<< 2, +1, << 2, +1, << 1, +1, << 1]
 170: cost: (3,   7];	[<< 2, +1, << 2, +1, << 2, +1, << 1]
 171: cost: (0,   8];	[<< 2, +1, << 2, +1, << 2, +1, << 1, +1]
 172: cost: (3,   7];	[<< 2, +1, << 2, +1, << 1, +1, << 2]
 340: cost: (5,   7];	[<< 2, +1, << 2, +1, << 2, +1, << 2]
 341: cost:       6;	[<< 2, +1, << 1, +1, << 5, -(n)]
 342: cost: (5,   9];	[<< 2, +1, << 2, +1, << 2, +1, << 1, +1, << 1]


Cache hits (finished):		   5
Cache hits (unfinished):	  56
Cache misses:			  31
============================================================
```

References
==========
* My _Software: Practice and Experience_ paper [Multiplication by integer constants](https://onlinelibrary.wiley.com/doi/pdf/10.1002/spe.4380160704) for details.
* Section 8-4 of Henry Warren's: Hacker's Delight (ISBN-13: 978-0321842688) has some updates and revisions.
* _The Art Computer Programming_, Vol 2, 2nd Edition; Section 4.6.3, page 441 of the 2nd Edition
* Vincent Lefèvre's [Multiplication by Integer Constant site](http://www.vinc17.net/research/mulbyconst/index.en.html)
* Yevgen Voronenko and Markus Püschel's [Spiral Multiplier Block Generator site](http://spiral.ece.cmu.edu/mcm/gen.html)
