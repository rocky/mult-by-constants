#ifndef SPE_MULT_H
#define SPE_MULT_H

#include <stdio.h>
#include <errno.h>
#include <stdlib.h>
#include <limits.h>

#define PROGRAM "mult-spe-86"
#define VERSION "1.0.0"

#ifndef COST
typedef float COST;
#define COSTFMT "g"

/*
   INFINITE_COST is the larger than the largest cost we expect to see.
   We use it to indicate that an operation is not available.

   We don't worry too much about having that big a value here since,
   numbers that require this cost would be on the order of two to that
   power.
*/

#define INFINITE_COST ((COST) INT_MAX)
#endif

#ifdef LONGLONG
typedef unsigned long long int VALUE;
#define VALUEFMT "llu"
#define STRTOVALUE(S) strtoull(S, (char **) NULL, 0)
#else
typedef unsigned long int VALUE;
#define VALUEFMT "lu"
#define STRTOVALUE(S) strtoul(S, (char **) NULL, 0)
#endif

#ifndef ADD_COST
#define ADD_COST ((COST) 1)
#endif

/* Note:
   If you want to disallow subtraction, set SUB_COST to INFINITE_COST
*/
#ifndef SUB_COST
#define SUB_COST ((COST) 1)
#endif

#ifndef SHIFT_COST
#define SHIFT_COST ((COST) 1)
#endif

/* The cost of multiplication by 0. */
#ifndef MAKEZERO_COST
#define MAKEZERO_COST ((COST) 1)
#endif

/* The cost of a multiplication by 1. */
#ifndef BYONE_COST
#define BYONE_COST ((COST) 0)
#endif

#ifndef HASH_SIZE
#define HASH_SIZE 16383
#endif

#ifndef MAXNON
#define MAXNON 65536
#endif

#ifndef MAXNON
#define MAXNON 65536
#endif

#define PLIMIT , &limit

#define odd(n) ((n) & 1)
#define even(n) (!odd(n))

typedef enum { INVALID, NOOP, ADD1, SUB1, FADD, FSUB } OP;

extern const char *OP2NAME[FSUB+1];

typedef struct node {
  struct node *parent;  /* node used to generate the current node  */
  VALUE value;          /* value of the current node (odd integer) */
  COST cost;            /* cost of the value, or lower bound       */
  OP opcode;            /* operation                               */
  unsigned int shift;   /* shift count                             */
  struct node *next;    /* next node having the same hash code     */
} NODE;

extern void init_hash(void);

extern unsigned int make_odd(VALUE *n);
extern unsigned int make_even(VALUE *n);


/* Returns the cost and operation sequence using the binary
   representation of the number.

   In this approach, each one bit other than the
   highest-order one bit is a "shift" by the number of
   consecutive zeros followed by an addition.

   If the number is even and not zero, then there is a final "shift".

   If subtraction is available, then each run of 1's in the
   binary representation is replaced by a shift of that amount
   followed by a subtraction.

   Since we generally prefer addition over subtraction:

   x = (x << 1) + x

   is preferable to:

   x = (x << 2) - x

   Examples:
   ---------

   We'll assume cost one for "add", "subtract", and "shift" by
   any amount.

   number  cost  remarks
   ------  ----  ------
   0:      0     do nothing; load constant zero
   1:      0     do nothing, load operand
   10:     1     shift one
   11:     2     shift one; add
   101:    2     shift two; add
   110     3     shift one; add; shift one
   111:    2     shift three; subtract one      - if subtract is available
   111:    4     shift one; add; shift one; add - if subtract is not available
*/

/* FIXME: for now we just do the cost. Later add the instructions... */
extern COST binary_mult_cost (VALUE n);


extern COST spe_mult(VALUE n, /*out*/ NODE *node, /*out*/ unsigned int *initial_shift);
extern void print_cost(VALUE n, COST cost);
extern void print_binary_value(VALUE n);

extern void
print_sequence(VALUE n, NODE *node, COST cost,
               long unsigned int initial_shift, int verbosity);



/* Number of multiplier-numbers sequences. Setting this to -1 forces
   hash initialization on a spe_mult() call.
*/
extern long int non;

extern int verbosity;  /* verbosity level, 0..3 */
extern NODE *hash_table[HASH_SIZE];


enum { EXIT_OK, EXIT_MEMORY, EXIT_USAGE, EXIT_BADMODE, EXIT_BADCONST,
       EXIT_INTERROR, EXIT_OVERFLOW };

unsigned int emit_code(NODE *node);


#endif /* SPE_MULT_H */


/*
 * Local variables:
 *  c-file-style: "gnu"
 *  tab-width: 8
 *  indent-tabs-mode: nil
 * End:
 */
