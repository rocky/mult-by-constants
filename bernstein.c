/*
 * Multiplication by a Constant -- Bernstein's Algorithm
 *
 * Usage: bernstein <mode> [ <constant> ... ]
 */

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
#define HASH_SIZE 511
#endif


#define odd(n) ((n) & 1)
#define even(n) (!odd(n))

enum { EXIT_OK, EXIT_MEMORY, EXIT_USAGE, EXIT_BADMODE, EXIT_BADCONST };

typedef enum { NOOP, ADD1, SUB1, FADD, FSUB } OP;
static char opsign[] = { ' ', '+', '-', '+', '-' };

typedef struct node {
  struct node *parent;  /* node used to generate the current node  */
  VALUE value;          /* value of the current node (odd integer) */
  unsigned int cost;    /* cost of the value                       */
  OP opcode;            /* operation                               */
  unsigned int shift;   /* shift count                             */
  struct node *next;    /* next node having the same hash code     */
} NODE;


static NODE *hash_table[HASH_SIZE];
static int mode;

void init_hash(void);
VALUE get_cst(char *s);
NODE *get_node(VALUE n);
NODE *make_node(VALUE n);
void try(VALUE n, NODE *node, OP opcode,
    unsigned int cost, unsigned int shift);
void bernstein(VALUE n);
unsigned int emit_code(NODE *node);


int main(int argc, char **argv)
{
  if (argc < 2)
  {
    fprintf(stderr, "Usage: bernstein <mode> [ <constant> ... ]\n");
    exit(EXIT_USAGE);
  }

  mode = atoi(argv[1]);
  if (errno)
  {
    fprintf(stderr, "bernstein: bad mode\n");
    exit(EXIT_BADMODE);
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
    while (scanf("%63s", buffer) == 1)
      bernstein(get_cst(buffer));
  }

  return EXIT_OK;
}


void init_hash(void)
{
  unsigned int i;
  for (i = 0; i < HASH_SIZE; i++)
    hash_table[i] = NULL;
}


VALUE get_cst(char *s)
{
  VALUE n;
  n = STRTOVALUE(s);
  if (errno || n == 0 || even(n))
  {
    fprintf(stderr, "bernstein: bad constant '%s'\n", s);
    exit(EXIT_BADCONST);
  }
  return n;
}


NODE *get_node(VALUE n)
{
  unsigned int hash;
  NODE *node;

  hash = n % HASH_SIZE;
  node = hash_table[hash];

  while (node)
  {
    if (node->value == n)
      return node;
    node = node->next;
  }

  node = make_node(n);
  node->next = hash_table[hash];
  hash_table[hash] = node;
  return node;
}


NODE *make_node(VALUE n)
{
  NODE *node;

  node = malloc(sizeof *node);
  if (!node)
  {
    fprintf(stderr, "bernstein: out of memory!\n");
    exit(EXIT_MEMORY);
  }
  node->parent = NULL;
  node->value = n;

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
    while (d <= dsup)
    {
      if (n % (d - 1) == 0)
        try(n / (d - 1), node, FSUB, SHIFT_COST + SUB_COST, shift);
      if (n % (d + 1) == 0)
        try(n / (d + 1), node, FADD, SHIFT_COST + ADD_COST, shift);
      d <<= 1;
      shift++;
    }
    try(n - 1, node, ADD1, SHIFT_COST + ADD_COST, 0);
    try(n + 1, node, SUB1, SHIFT_COST + SUB_COST, 0);
  }

  return node;
}


void try(VALUE n, NODE *node, OP opcode,
    unsigned int cost, unsigned int shift)
{
  NODE *tmp_node;

  while(even(n))
  {
    n >>= 1;
    shift++;
  }

  tmp_node = get_node(n);
  cost += tmp_node->cost;
  if (!node->parent || cost < node->cost)
  {
    node->parent = tmp_node;
    node->cost = cost;
    node->opcode = opcode;
    node->shift = shift;
  }
}

void bernstein(VALUE n)
{
  NODE *node;

  node = get_node(n);
  printf("Cost(%" VALUEFMT ") = %u\n", n, node->cost);
  if (mode)
    emit_code(node);
}

unsigned int emit_code(NODE *node)
{
  unsigned int i;

  if (node == NULL)
    return 0;

  i = emit_code(node->parent);
  printf("u%u = ", i);
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


/* $Id: bernstein.c 1.2 2000/11/21 15:18:21 lefevre Exp lefevre $ */
