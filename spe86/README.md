This directory has an implementation of my 1986 Software -- Practice & Experience paper.

History
=======

Although the pseudo code in my paper was Ada-like, the code was originally written in a PL/I-like programming language called [PL.8](https://en.wikipedia.org/wiki/PL/8); it was embedded inside the PL.8 optimizing compiler.

Sometime around 1983 or so, I was working in that compiler group when my manager Marty Hopkins told me that there was some code Victor Miller wrote to do multiplications that none of the others in the compiler group understood well. So I was told to talk to Victor, figure out how it works, and adapt it for the instruction-costs of the other CPU architectures that the PL.8 compiler supported. I did that, and in the process adapted it in various ways.

One change I made was to add alpha-beta cutoffs to its instruction sequence-searching. However at the time I didn't know that this is what I had done. I didn't explain that well in my SP&E paper.

The C code here starts with V. Lefèvre's implementation, for which I am grateful. In addition to the alpha-beta searching mentioned above, my additions included handled negative numbers; and even numbers which accepted by Victor's code also accepted. These features were omitted Lefèvre's last implementation, so I've added that back in here.

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

The first parameter given above is a verbosity level. The levels are as follow:

* 0 just shows the cost
* 1 shows the above and the instruction sequence
* 2 shows the above and sub-values that get added the cache,
* 3 shows the above and calls to node searching

Run `--help` to get usage:

```
$ ./mult-spe86

Usage:
  mult-spe-86 <verbosity-level> [ <constant> ... ]
  mult-spe-86 -V | --version
  mult-spe-86 -h | | -? --help

<verbosity-level> is an integer from 0..3;
<constant> is a positive integer
```

As a subroutine
---------------

To search sequence inside C code, here is an example of using the API:

```C
#include "spe_mult.h"

...
    NODE *node = NULL; // Stores instruction sequence
    init_hash();       // Instruction cache sequences found
    VALUE n = 123455;  // Adjust this to the multilier you want an instruction sequence for
    COST cost = spe_mult(n, node); // Find a multiplication sequence!
```

Above, `node` will contain a pointer structure for the instruction sequence;
`cost` will have the instruction cost.


Building
========

A GNU `Makefile` is provided to build everything. To make the standalone program `mult-spe86` (for: multiplications using software, practice and experience '86).

To build everything, just run `make`.

If you have [`remake`](https://bashdb.sourceforge.net/remake) installed, you can get a list of targets that can be built using `remake --tasks`.
```
