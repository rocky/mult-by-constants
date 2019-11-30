"""Copyright (c) 2019 by Rocky Bernstein

A library for searching for short sequences of "add", "subtract", "shift" instructions to
multiply a number by a constant.

See my paper on this in _Software: Practice and Experience_, 1986
(https://onlinelibrary.wiley.com/doi/pdf/10.1002/spe.4380160704). This
is also described in section 8-4 of Henry Warren's: Hacker's
Delight. ISBN-13: 978-0321842688.
"""
__docformat__ = 'restructuredtext'
from mult_by_const.mult import *
from mult_by_const.instruction import *
from mult_by_const.cache import *
