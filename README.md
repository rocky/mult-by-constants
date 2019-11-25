Code to compute the mininum number of shifts, adds, subtracts, under different cost models).

See my _Software: Practice and Experience_ paper [Multiplication by integer constants](https://onlinelibrary.wiley.com/doi/pdf/10.1002/spe.4380160704) for details.

Section 8-4 of Henry Warren's: Hacker's Delight (ISBN-13: 978-0321842688) has some updates and revisions.

The intention in coding is to be a bit flexible to allow for variation in machine architectures. In particular we allow for architectures that have a shift time that varies with the amount to be shifted. And we can handle architectures that don't have a "subtract" operation.

Given this, we can handle, for example, a machine with only the `add` operation, disallowing the `subtract` operation and using a custom shift cost function that varies by the amount shifted. Note: `y = x << 1` is the same as `y = x + x`, and `y = x << 2` would be the same thing as `z = x + x; y = z + z`.
