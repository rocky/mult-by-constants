This is a copy of the software in V. Lefèvre's [Multiplication by Integer Constants](http://www.vinc17.net/research/mulbyconst/index.en.html#software).

However the Software, Practice and Experience code has been split out and put in its own directory, [_spe_](../spe86).

Raphaël Rigo's implementation (in C using GMP) of V. Lefèvre's latest algorithm is in directory [_rigo_](./rigo).

Possibly other code will be beefed up and split out as well.

Vincent's interested in this problem was multiple precision (up to a few hundreds of bits) multiplication for evaluating polynomials. Here, the constants
are the binomial coefficients of the polynomial, rather than an arbitrary integer. However Vincent did not want to restrict the work to just these constants.

Vincent also had simplify the model to see what could be done.

In this scenario, another operation one could also take into account, is a word-word multiplication instruction. That's not done here and would make the problem more complex.

[Vincent's Ph.d thesis](https://www.vinc17.net/research/papers/these.ps.gz) explains the context of the problem that he was solving.
See also [Radix-2r Arithmetic for Multiplication by a Constant](https://hal.archives-ouvertes.fr/hal-01002468) by Abdelkrim K. Oudjida and Nicolas Chaillet.
