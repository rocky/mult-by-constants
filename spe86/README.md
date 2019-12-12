This directory has an implementation of my 1986 Software -- Practice & Experience paper.

History
=======

That code was originally written in a PL/I-like programming language called [PL.8](https://en.wikipedia.org/wiki/PL/8), and was embedded inside a its optimizing compiler.

Sometime around 1983 or so, I was working in that compiler group when my manager Marty Hopkins told me that there was some code Victor Miller wrote to do multiplications that none of the others in the compiler group understood well. So I was told to talk to Victor, figure out how it works, and adapt it for the instruction-costs of the other CPU architectures that the PL.8 compiler supported. I did that, adapted it in various ways.

One change I made was to add alpha-beta cutoffs in its instruction sequence-searching. However at the time I didn't know that this is what I had done. I didn't explain that well in my SP&E paper.

The code here starts with V. Lefèvre's implementation, for which I am grateful. In addition to the alpha-beta searching mentioned above, the original code I wrote handled negative numbers as well as even number which were omitted Lefèvre's last implimenation. I've added that back in here.

To run the test program

Using
=====

As a command-line utility
-------------------------

A command-line program, `mult-spe86` (for multiplications via software, practice and experince '86) can be run. For example:

```
$ ./mult-spe86 1 1234
Cost(1234) = 9
        1: u0 = 1
        5: u1 = u0 << 2 + 1
       11: u2 = u1 << 1 + 1
       77: u3 = u2 << 3 - u2
      617: u4 = u3 << 3 + 1
     1234: u5 = u4 << 1
```

The first parameter is a verbosity level. To see just the cost in instructions, set the verbosity value to 0. To get searching information set the verbosity value to 1.

Run `--help` to get usage:

```
$ ./mult-spe86

Usage: mult-spe-86 <verbosity-level> [ <constant> ... ]
  verbosity-level 0,1,2
  num: a positive integer
```

As a subroutine
---------------

To search sequence inside C code, here is an example of using the API:

```C
#include "spe_mult.h"

...
    NODE *node;     // Stores instruction sequence
    init_hash();    // Instruction cache sequences found
    int n = 123455; // Adjust this to the multilier you want an instruction sequence for
    unsigned int cost = spe_mult(n, node); // Find a multiplication sequence!
```

Above, `node` will contain a pointer structure for the instruction sequence;
`cost` will have the instruction cost.


Building
========

A GNU `Makefile` is provided to build everything. To make the standalone program `mult-spe86` (for: multiplications using software, practice and experience '86).

To build everything, just run `make`.

If you have [`remake`](https://bashdb.sourceforge.net/remake) installed, you can get a list of targets that can be built using `remake --tasks`.
```
