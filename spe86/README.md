This directory has an implementation of my 1986 Software -- Practice & Experience paper.

History
=======

Although the pseudo code in my paper was Ada-like, the code was originally written in a PL/I-like programming language called [PL.8](https://en.wikipedia.org/wiki/PL/8); it was embedded inside the PL.8 optimizing compiler.

Sometime around 1983 or so, I was working in that compiler group when my manager Marty Hopkins told me that there was some code Victor Miller wrote to do multiplications that none of the others in the compiler group understood well. So I was told to talk to Victor, figure out how it works, and adapt it for the instruction-costs of the other CPU architectures that the PL.8 compiler supported. I did that, and in the process adapted it in various ways.

Adjusting for instruction-sequence costs were important. On the Motorola 6800, the shift cost took time proportional to the amount shifted. And it was never faster than an "add" operations. Therefore to multiply by 2, an "add" was preferable to a "shift". And to multiply by three, you would build on the multiplication by 2 using another "add", rather than start from 4 and subtracting one. On the other hand if you needed to multiply by _negative_ 3, then using the subtraction with the operand flipped from the positive multiplication case was a win.

Another change I made was to add alpha-beta cutoffs to its instruction sequence-searching. However at the time I didn't know that this is what I had done. This and caching make the program go very fast. I didn't explain that well in my SP&E paper. Lastly, in contrast to the booth-encoding methods, like those of V. Lefèvre, at most 3 registers are used in the entire computation, for number under 100 where the binary method works, two registers suffices. This too was important since we were worried about "register pressure" in our optimizing compiler which made use of a global register allocation, done via a simple and elegant graph-coloring algorithm and expertly implemented by Greg Chaitin.

The C code here starts with V. Lefèvre's implementation, for which I am grateful. In addition to the alpha-beta searching mentioned above, my additions included handled negative numbers; and even numbers which Victor's code also accepted. Since features were omitted Lefèvre's last implementation, I've added that back in here. There are still a couple of bugs in my code which I hope to fix.

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
  mult-spe-86 -h | -? | --help

<verbosity-level> is an integer from 0..3;
<constant> is a positive integer
```

As a subroutine
---------------

To search sequence inside C code, here is an example of using the API:

```C
#include "spe_mult.h"

...
    /* The following are returned as a result of searching for a multiplication sequence. */
    NODE *node = NULL;
	unsigned int intial_shift = 0;

    VALUE n = 123455;  // Adjust this to the multilier you want an instruction sequence for
    COST cost = spe_mult(n, node, &initial_shift); // Find a multiplication sequence!

    print_sequence(n, node, initial_shift, 1); // Print instruction sequence.
```

Above, `node` will contain a pointer structure for the instruction sequence;
`cost` will have the instruction cost.


Building
========

A GNU `Makefile` is provided to build everything. To make the standalone program `mult-spe86` (for: multiplications using software, practice and experience '86).

To build everything, just run `make`.

If you have [`remake`](https://bashdb.sourceforge.net/remake) installed, you can get a list of targets that can be built using `remake --tasks`.
```
