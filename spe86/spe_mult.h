#ifndef SPE_MULT_H
#define SPE_MULT_H

#include <stdio.h>
#include <errno.h>
#include <stdlib.h>

#define PROGRAM "mult-spe-86"
#define VERSION "1.0.0"

#ifndef COST
typedef float COST;
#define COSTFMT "g"
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

#ifndef SUB_COST
#define SUB_COST ((COST) 1)
#endif

// FIXME: this should be one and we should remove the doubling in spe_mult().
#ifndef SHIFT_COST
#define SHIFT_COST ((COST) 0)
#endif

#ifndef HASH_SIZE
#define HASH_SIZE 16383
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

extern COST spe_mult(VALUE n, /*out*/ NODE *node);

extern long int non;   /* number of nodes */
extern int verbosity;  /* verbosity level, 0..2 */
extern NODE *hash_table[HASH_SIZE];


static int errexit(const char* msg, int exit_code) {
  fprintf(stderr, "%s: %s\n", PROGRAM, msg);
  exit(exit_code);
}

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
