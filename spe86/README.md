This directory has an implementation of my 1986 Software -- Practice & Experience paper.

That code was originally written in a PL/I-like programming language called [PL.8](https://en.wikipedia.org/wiki/PL/8), and was embedded inside a its optimizing compiler.

Sometime around 1983 or so, I was working in that compiler group when my manager Marty Hopkins told me that there was some code Victor Miller wrote to do multiplications that none of the others in the compiler group understood well. So I was told to talk to Victor, figure out how it works, and adapt it for the instruction-costs of the other CPU architectures that the PL.8 compiler supported. I did that, adapted it in various ways.

One change I made was to add alpha-beta cutoffs in its instruction sequence-searching. However at the time I didn't know that this is what I had done. I didn't explain that well in my SP&E paper.

The code here starts with V. Lefèvre's implementation, for which I am grateful. In addition to the alpha-beta searching mentioned above, the original code I wrote handled negative numbers as well as even number which were omitted Lefèvre's last implimenation. I've added that back in here.
