One of the aspects that makes this problem interesting and challenging is that the kinds of available instructions or operations can vary, and the cost of executing each can vary.

In _The Art Computer Programming_, Vol 2, 2nd Edition; Section 4.6.3, Knuth introduces this topic via computing polynomials and specifically the exponent of a polynomial, like x^51.
A good way to compute this would e use use x^3 * x^17, rather than doing something based on the binary representation of 51.

Since x^a * x^b is the same thing as x^(a+b), the problem of raising a number, like 51, to a power is equivalent to multiplication by 51. In this situation though, we only have one operation: "add". You can think of "shift" being available as a single instruction, but only an doubling addition, or "shift by 1". So if you want to use the programs here to figure out efficient ways to raise a number to a power, it can be done, but we must be able to limit the instructions to just "add" and "shift 1" (or "double").

Similarly, although many CPU's computers have shift instructions, the time taken to perform the shift may be proportional to the amount shifted. And the time may differ from the time to peform an addition. Therefore on many CPUs, a doubling add is faster than a shift of one. And to multiply by 3, doing this via 2+1 (double and add) is often faster than via 4-1 (shift 2 and subtract), even though two _instructions_ would be used in either case.

Finally, some CPU's have instructions that combine "shift" and "add" that can be used here. The original IBM 801 CPU did, although it was later dropped in the POWER series. The IBM ROMP had a limited form of of this: "shift 1 and add". These were possible because the shifting unit and the adding unit on the CPU were somewhat independent.

Above we describe measuring the timing of instructions rather than just counting instructions. However there is another demension to consider: the number of registers or temporary values that need to be kept.

todo: 2 address vs 3 address instructions.
