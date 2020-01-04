Here we have some observations about the sequences.

RISC model (equal-cost adds, subtracts, shifts)
-----------------------------------------------

* A number and its +1 or -1 neighbor should differ by no more than one instruction.
* A negative number should differ by no more than one instruction more than its positive value, and many times it is the same number of instructions
* 7 is the lowest positive number where subtraction has a distinct advantage over sequences without subtraction. -3 is the lowest number where subtraction has an advantage over negation.
* 27 = 3 x 7 is the lowest number where factoring has an advantage over the binary method: 4 instructions vs. 6. 45 = 5 x 9 is the next number; again 4 vs 6 instructions
* In the first 100 numbers there are only 10 numbers where factoring helps over the binary method
* The average number of instructions for a multiplier goes from about 6 to 8 from 1,000 to 10,0000
* Combining factoring of simple numbers like a power of 2 plus or minus one reduces the average instruction sequence over the binary method by 40-50% overall, and greatly flattens the ups-and-down fluctuation of consecutive numbers.


Chained adds
------------

* 23 is the lowest number that reuses a previous product (3); 30 reusing 12 + 3 is the next lowest number
