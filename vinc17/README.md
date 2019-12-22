This is a copy of the software in V. Lefèvre's [Multiplication by Integer Constants](http://www.vinc17.net/research/mulbyconst/index.en.html#software).

However the `bernstein.c` from Software, Practice and Experience code has been copied, and put in its own directory, [_spe_](../spe86).

Raphaël Rigo's implementation in C of V. Lefèvre's latest algorithm is in directory [_rigo_](./rigo).

Possibly other code will be beefed up and split out as well.

Vincent's interested in this problem was multiple precision (up to a few hundreds of bits) multiplication for evaluating polynomials. That's motivates why `rigo.c` uses
[The GNU Multiple Precision Arithmetic Library](https://gmplib.org/) (GMP). In contrast, `bernstein.c` can work only with integers limited to the a number that can fit in an `unsigned long`, which is reasonable for its intended application, replacing a CPU's multiplication instruction. See [README.md](../spe86/README.md) in the [_spe86_](../spe86) directory for more information on the differences.


In Vincent's scenario, the constants he is interested in were not arbitrary integers but rather the binomial coefficients of the kinds certain polynomials. However Vincent did not want to restrict his research to just these constants.

Vincent also had simplify the model to see what could be done.

Another operation in this scenario that one might also take into account, is a word-word multiplication instruction. That's not done here and would make the problem more complex.

[Vincent's Ph.d thesis](https://www.vinc17.net/research/papers/these.ps.gz) explains the context of the problem that he was solving.
See also [Radix-2r Arithmetic for Multiplication by a Constant](https://hal.archives-ouvertes.fr/hal-01002468) by Abdelkrim K. Oudjida and Nicolas Chaillet.
