/*
 *
 * Multiplication by a Constant -- Rocky Bernstein's 1986 Software Practice and Expereince paper
 *
 * Usage: mult-spe86 <verbosity={0 | 1 | 2} [ <constant> ... ]
 *
 * Compile with -DPRUNE to prune the tree.
 * Compile with -DNCALLS to get the number of get_node() and try() calls.
 */

#define PROGRAM "mult-spe-86"
#define VERSION = "1.0.0"

#include <stdlib.h>
#include <stdio.h>
#include <errno.h>

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
#define ADD_COST 1
#endif

#ifndef SUB_COST
#define SUB_COST 1
#endif

#ifndef SHIFT_COST
#define SHIFT_COST 0
#endif

#ifndef HASH_SIZE
#define HASH_SIZE 16383
#endif

#ifndef MAXNON
#define MAXNON 65536
#endif

#ifdef PRUNE
#define PLIMIT , &limit
#else
#define PLIMIT
#endif

#define odd(n) ((n) & 1)
#define even(n) (!odd(n))

enum { EXIT_OK, EXIT_MEMORY, EXIT_USAGE, EXIT_BADMODE, EXIT_BADCONST,
       EXIT_INTERROR, EXIT_OVERFLOW };

typedef enum { INVALID, NOOP, ADD1, SUB1, FADD, FSUB } OP;
static char opsign[] = { ' ', ' ', '+', '-', '+', '-' };

typedef struct node {
  struct node *parent;  /* node used to generate the current node  */
  VALUE value;          /* value of the current node (odd integer) */
  unsigned int cost;    /* cost of the value, or lower bound       */
  OP opcode;            /* operation                               */
  unsigned int shift;   /* shift count                             */
  struct node *next;    /* next node having the same hash code     */
} NODE;

static NODE *hash_table[HASH_SIZE];
static long int non = 0;  /* number of nodes */
static int verbosity;
#ifdef NCALLS
static unsigned long int ngn = 0, ntry = 0, nmalloc = 0;
#endif

void init_hash(void);
VALUE get_cst(char *s);
#ifdef PRUNE
NODE *get_node(VALUE n, unsigned int limit);
void try(VALUE n, NODE *node, OP opcode,
    unsigned int cost, unsigned int shift, unsigned int *limit);
#else
NODE *get_node(VALUE n);
void try(VALUE n, NODE *node, OP opcode,
    unsigned int cost, unsigned int shift);
#endif
void bernstein(VALUE n);
unsigned int emit_code(NODE *node);

static int errexit(const char* msg, int exit_code) {
  fprintf(stderr, "%s: %s\n", PROGRAM, msg);
  exit(exit_code);
}

int main(int argc, char **argv)
{
  if (argc < 2)
    {
      fprintf(stderr, "Usage: %s <verbosity-level> [ <constant> ... ]\n"
              "  verbosity-level 0,1,2\n"
              "  num: a positive integer\n", PROGRAM);
      exit(EXIT_USAGE);
    }

  verbosity = atoi(argv[1]);
  if (errno)
    {
      static char buf[30] = "";
      snprintf(buf, sizeof(buf), "bad verbosity level '%s'", argv[1]);
      errexit(buf, EXIT_BADMODE);
    }

  init_hash();

  if (argc > 2)
    {
      unsigned int i;
      for (i = 2; i < argc; i++)
        bernstein(get_cst(argv[i]));
    }
  else
    {
      char buffer[64];
      while (1) {
	  printf("Enter a a positive number (or Ctrl-d to exit): ");
	  if (scanf("%63s", buffer) == 1)
	    bernstein(get_cst(buffer));
	  else
	    break;
      };
    }

  return EXIT_OK;
}

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

VALUE get_cst(char *s)
{
  VALUE n;
  n = STRTOVALUE(s);
  if (errno || n == 0)
    {
      static char buf[30] = "";
      snprintf(buf, sizeof(buf), "bad constant '%s'", s);
      errexit(buf, EXIT_BADCONST);
      exit(EXIT_BADCONST);
    }
  return n;
}

#ifdef PRUNE
NODE *get_node(VALUE n, int unsigned limit)
#else
NODE *get_node(VALUE n)
#endif
{
  unsigned int hash;
  NODE *node;

#ifdef NCALLS
  if (++ngn == 0)
    {
      errexit("ngn overflow", EXIT_OVERFLOW);
    }
#endif

  if (verbosity >= 2)
#ifdef PRUNE
    printf("get_node %" VALUEFMT " %u\n", n, limit);
#else
    printf("get_node %" VALUEFMT "\n", n);
#endif

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
      fprintf(stderr, "bernstein: nmalloc overflow\n");
      exit(EXIT_OVERFLOW);
    }
#endif
  node = malloc(sizeof *node);
  if (!node)
    {
      fprintf(stderr, "bernstein: out of memory (%ld nodes)!\n", non);
      exit(EXIT_MEMORY);
    }
  non++;
  node->parent = NULL;
  node->value = n;
  node->next = hash_table[hash];
  hash_table[hash] = node;
#ifdef PRUNE
  node->opcode = INVALID;
 validate_node:
#endif

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
#ifdef PRUNE
      node->cost = limit + 1;  /* Lower bound on the cost in case the
                                  following calls to try would fail.  */
#endif
      while (d <= dsup)
        {
          if (n % (d - 1) == 0)
            try(n / (d - 1), node, FSUB, SHIFT_COST + SUB_COST, shift PLIMIT);
          if (n % (d + 1) == 0)
            try(n / (d + 1), node, FADD, SHIFT_COST + ADD_COST, shift PLIMIT);
          d <<= 1;
          shift++;
        }
      try(n - 1, node, ADD1, SHIFT_COST + ADD_COST, 0 PLIMIT);
      try(n + 1, node, SUB1, SHIFT_COST + SUB_COST, 0 PLIMIT);
    }

  return node;
}

#ifdef PRUNE
void try(VALUE n, NODE *node, OP opcode,
         unsigned int cost, unsigned int shift, unsigned int *limit)
#else
void try(VALUE n, NODE *node, OP opcode,
         unsigned int cost, unsigned int shift)
#endif
{
  NODE *tmp_node;

#ifdef NCALLS
  if (++ntry == 0)
    {
      fprintf(stderr, "bernstein: ntry overflow\n");
      exit(EXIT_OVERFLOW);
    }
#endif

  while(even(n))
    {
      n >>= 1;
      shift++;
    }

#ifdef PRUNE
  if (cost > *limit)
    return;
  tmp_node = get_node(n, *limit - cost);
  if (tmp_node->opcode == INVALID)
    return;
#else
  tmp_node = get_node(n);
#endif

  cost += tmp_node->cost;
#ifdef PRUNE
  if (cost > *limit)
    return;
#endif
  if (!node->parent || cost < node->cost)
    {
      node->parent = tmp_node;
      node->cost = cost;
      node->opcode = opcode;
      node->shift = shift;
#ifdef PRUNE
      *limit = cost - 1;
#endif
      if (verbosity >= 2)
        printf("node %" VALUEFMT ": parent %" VALUEFMT ", opcode %d, "
               "shift count %u, cost %u\n", node->value,
               node->parent->value, node->opcode, node->shift, node->cost);
    }
}

unsigned int make_odd(VALUE *n) {

  unsigned int shift = 0;
  while(even(*n))
    {
      *n >>= 1;
      shift++;
    }
  return shift;
}

void bernstein(VALUE n)
{
  NODE *node;
#ifdef PRUNE
  VALUE p;
  unsigned int limit = 0;
#endif

  VALUE orig_n = n;
  long unsigned initial_shift = make_odd(&n);

  if (non > MAXNON)
    init_hash();

#ifdef PRUNE
  p = n >> 1;
  while (p)  /* count the number of 1's in p */
    {
      limit += SHIFT_COST + ADD_COST;
      p &= p-1;
    }
  node = get_node(n, limit);
#else
  node = get_node(n);
#endif

  unsigned int cost = node->cost * 2;
  if (initial_shift > 0) {
    cost += 1;
  }

  printf("Cost(%" VALUEFMT ") = %u\n", orig_n, cost);
  if (verbosity) {
    unsigned int i = emit_code(node);
    if (initial_shift > 0) {
      printf("%9lu: u%u = u%u << %lu\n", orig_n, i, i-1, initial_shift);
    }
  }
#ifdef NCALLS
  printf("%lu calls to get_node()\n", ngn);
  printf("%lu calls to try()\n", ntry);
  printf("%lu calls to malloc()\n", nmalloc);
#endif
  fflush(stdout);
}

unsigned int emit_code(NODE *node)
{
  unsigned int i;

  if (node == NULL)
    return 0;

  i = emit_code(node->parent);
  printf("%9lu: u%u = ", node->value, i);
  if (node->opcode == NOOP)
    {
      printf("1");
    }
  else
    {
      printf("u%u << %u %c ", i-1, node->shift, opsign[node->opcode]);
      if (node->opcode == ADD1 || node->opcode == SUB1)
        printf("1");
      else
        printf("u%u", i-1);
    }
  printf("\n");

  return i+1;
}
