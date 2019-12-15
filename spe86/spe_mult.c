/*
 *
 * Multiplication by a Constant -- Rocky Bernstein's 1986 Software Practice and Expereince paper
 *
 * A library for finding multiplication sequences.
 *
 * Compile with -DNCALLS to get the number of get_node() and try() calls.
 */

#include <assert.h>
#include "spe_mult.h"
#include "util.h"

static char opsign[] = { ' ', ' ', '+', '-', '+', '-' };

NODE *hash_table[HASH_SIZE];

long int non = -1;

int verbosity = 1;

static int call_nesting = 0;

const char *OP2NAME[FSUB+1] =
  {
   "INVALID", "NOOP", "add(1)", "subtract(1)", "add(n)", "subtract(n)"
  };

NODE *get_node(VALUE n, COST limit);
void try(VALUE n, NODE *node, OP opcode,
    COST cost, unsigned int shift, COST *limit);

#ifdef NCALLS
static unsigned long int ngn = 0, ntry = 0, nmalloc = 0;
#endif

extern void
print_sequence(VALUE n, NODE *node, COST cost,
               long unsigned int initial_shift, int verbosity)
{

  if (verbosity > -1)
    {
      print_cost(n, cost);
      if (verbosity > 0) {
        unsigned int i = emit_code(node);
        if (initial_shift > 0) {
          printf("%9lu: r%u = r%u << %lu\n", n, i, i-1, initial_shift);
        }

      }

#ifdef NCALLS
      printf("%lu calls to get_node()\n", ngn);
      printf("%lu calls to try()\n", ntry);
      printf("%lu calls to malloc()\n", nmalloc);
#endif
      fflush(stdout);
    }
}

extern
void init_hash(void)
{
  unsigned int i;
  for (i = 0; i < HASH_SIZE; i++)
    {
      NODE *node;
      node = hash_table[i];
      while (node)
        {
          NODE *next;
          next = node->next;
          if (non-- == 0)
            {
              errexit("internal error ('non' too low)!", EXIT_INTERROR);
            }
          free(node);
          node = next;
        }
      hash_table[i] = NULL;
    }
  if (non == 0)
    return;
  errexit("internal error ('non' too high)!", EXIT_INTERROR);
}

#define TRY_MSG(msg, value)                     \
  if (verbosity >= 3) {                         \
    for (int i=0; i < 2*call_nesting; i++) {    \
      putchar(' ');                             \
    }                                              \
    printf("Trying " msg " %" VALUEFMT "\n", value);    \
  }


NODE *get_node(VALUE n, COST limit)
{
  unsigned int hash;
  NODE *node;

#ifdef NCALLS
  if (++ngn == 0)
    {
      errexit("ngn overflow", EXIT_OVERFLOW);
    }
#endif

  if (verbosity >= 3) {
    for (int i=0; i < 2*call_nesting; i++) {
      putchar(' ');
    }
    printf("get_node %" VALUEFMT " with max cost: %" COSTFMT "\n", n, limit);
  }

  hash = n % HASH_SIZE;
  node = hash_table[hash];

  while (node)
    {
      if (node->value == n)
        {
#ifdef PRUNE
          if (node->opcode == INVALID && node->cost <= limit)
            goto validate_node;
#endif
          return node;
        }
      node = node->next;
    }

#ifdef NCALLS
  if (++nmalloc == 0)
    {
      fprintf(stderr, "%s: nmalloc overflow\n", PROGRAM);
      exit(EXIT_OVERFLOW);
    }
#endif
  node = malloc(sizeof *node);
  if (!node)
    {
      fprintf(stderr, "%s: out of memory (%ld nodes)!\n", PROGRAM, non);
      exit(EXIT_MEMORY);
    }
  non++;
  node->parent = NULL;
  node->value = n;
  node->next = hash_table[hash];
  hash_table[hash] = node;
  node->opcode = INVALID;
#ifdef PRUNE
 validate_node:
#endif


  call_nesting++;

  if (n == 1)
    {
      node->cost = 0;
      node->opcode = NOOP;
    }
  else
    {
      VALUE d = 4, dsup;
      int shift = 2;
      dsup = n >> 1;
      node->cost = limit + 1;  /* Lower bound on the cost in case the
                                  following calls to try would fail.  */

      while (d <= dsup)
        {
          if (n % (d - 1) == 0) {
            TRY_MSG("factor", d-1)
            try(n / (d - 1), node, FSUB, SHIFT_COST + SUB_COST, shift, &limit);
          }
          if (n % (d + 1) == 0) {
            for (int i=0; i < 2*call_nesting; i++) {
              putchar(' ');
            }
            TRY_MSG("factor", d+1)
            try(n / (d + 1), node, FADD, SHIFT_COST + ADD_COST, shift, &limit);
          }
          d <<= 1;
          shift++;
        }
      TRY_MSG("lower neighbor", n-1)
      try(n - 1, node, ADD1, ADD_COST, 0, &limit);
      TRY_MSG("upper neighbor", n+1)
      try(n + 1, node, SUB1, SUB_COST, 0, &limit);
    }

  call_nesting--;

  return node;
}

void try(VALUE n, NODE *node, OP opcode,
         COST cost, unsigned int shift, COST *limit)
{
  NODE *tmp_node;
  unsigned int shift_amount = make_odd(&n);

  /* This was not called via factoring.
     FIXME: there must be a better way to structure this.
  */
  if (shift == 0)
    shift = shift_amount;

#ifdef NCALLS
  if (++ntry == 0)
    {
      fprintf(stderr, "%s: ntry overflow\n", PROGRAM);
      exit(EXIT_OVERFLOW);
    }
#endif

  if (shift_amount) cost += SHIFT_COST;

  if (cost > *limit)
    return;
  tmp_node = get_node(n, *limit - cost);
  if (tmp_node->opcode == INVALID)
    return;

  cost += tmp_node->cost;
  if (cost > *limit)
    return;

  if (!node->parent || cost < node->cost)
    {
      node->parent = tmp_node;
      node->cost = cost;
      node->opcode = opcode;
      node->shift = shift;

      *limit = cost - 1;

      if (verbosity >= 2) {
        for (int i=0; i < 2*call_nesting; i++) {
          putchar(' ');
        }
        printf("node %" VALUEFMT ": parent %" VALUEFMT ", %s, "
               "shift count %u, cost %" COSTFMT "\n", node->value,
               node->parent->value, OP2NAME[node->opcode], node->shift, node->cost);
      }
    }
}

extern
unsigned int make_odd(VALUE *n) {

  unsigned int shift;
  for (shift=0 ; even(*n); shift ++)
    *n >>= 1;
  return shift;
}

extern
unsigned int make_even(VALUE *n) {
  unsigned int shift;
  for (shift=0 ; odd(*n); shift ++)
    *n >>= 1;
  return shift;
}


/* FIXME: This doesn't handle subtractions or varying
   by shifting larger amounts.
*/
extern
COST binary_mult_cost(VALUE n)
{
  if (n == (VALUE) 0) return MAKEZERO_COST;
  if (n == (VALUE) 1) return BYONE_COST;

  assert(n > (VALUE) 0);

  {
    COST cost = even(n) ? SHIFT_COST : (VALUE) 0;
    VALUE p = n;

    while (p > 1) {

      unsigned int shift_amount = make_odd(&p);

      if (p == 1)
        break;

      /* Handle low-order 1's via "adds", and also "subtracts" if
         subtracts are available.
       */

      {
        VALUE old_p = p;
        unsigned int one_count = make_even(&p);
        /* FIXME: When we have more flexible costs,
           change HAVE_SUBTRACT_OP to something more specific .
        */
        if (HAVE_SUBTRACT_OP && one_count > 1) {
          cost += SHIFT_COST + SUB_COST;
          p = old_p + 1;
        } else {
          cost += SHIFT_COST + ADD_COST;
          p = old_p - 1;
        }
      }
    }
    return cost;
  }
}

extern
COST spe_mult(VALUE n, NODE *node, unsigned int *initial_shift)
{
  VALUE p;
  COST limit = 0;

  VALUE orig_n = n;

  *initial_shift = make_odd(&n);

  /* Initial/reset cache, if needed */
  if (non > MAXNON || non == -1) {
    if (non == -1)
      non = 0;
    init_hash();
  }

  /* Use the binary method to get a limit on the multiplication sequence.
     Until we have a routine that actually gets the binary method, tack on an additional
     cost so that searching will update with the binary method if no other method is available.
  */
  limit  = binary_mult_cost(n) + ADD_COST;
  node = get_node(n, limit);

  COST cost = node->cost;
  if (*initial_shift > 0) {
    cost += SHIFT_COST;
  }

  print_sequence(orig_n, node, cost, *initial_shift, verbosity);
  return cost;
}

extern
unsigned int emit_code(NODE *node)
{
  /* Note currently we use register_number, since we need at most 2 registers in the
     current chaining scheme.

     However in the future, as we try to reduce sequences by using more arbitrary
     partial products this can change. So we still keep this variable around
     and return a register number.
  */
  unsigned int register_number;
  char regnum[] = "r1";

  if (node == NULL)
    return 0;

  register_number = emit_code(node->parent);

  if (node->opcode == NOOP)
    {
      printf("%9lu: r0 = <initial value>", node->value);
    }
  else
    {
      printf("%9lu: r1 = ", node->value);
      if (node->shift) {
        printf("r1 << %u", node->shift);
      }
      if (node->opcode == ADD1 || node->opcode == SUB1)
        printf(" %c r0", opsign[node->opcode]);
      else if (node->opcode == FADD || node->opcode == FSUB)
        printf(" %c r1", opsign[node->opcode]);
      else {
        printf("Uknown opcode\n");
      }
    }
  printf("\n");

  return ++register_number;
}


/*
 * Local variables:
 *  c-file-style: "gnu"
 *  tab-width: 8
 *  indent-tabs-mode: nil
 * End:
 */
