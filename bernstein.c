/*
 * Multiplication by a Constant -- Bernstein's Algorithm
 *
 * Usage: bernstein <constant>
 */

#include <stdlib.h>
#include <stdio.h>
#include <errno.h>


#ifdef LONGLONG
typedef unsigned long long int VALUE;
#define STRTOVALUE(S) strtoull(S, (void *) NULL, 0)
#else
typedef unsigned long int VALUE;
#define STRTOVALUE(S) strtoul(S, (void *) NULL, 0)
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

typedef enum { NOOP, ADD1, SUB1, FADD, FSUB } OP;

typedef struct node {
  struct node *parent;  /* node used to generate the current node  */
  VALUE value;          /* value of the current node (odd integer) */
  unsigned int cost;    /* cost of the value                       */
  OP opcode;            /* operation                               */
  unsigned int shift;   /* shift count                             */
  struct node *next;    /* next node having the same hash code     */
} NODE;


static NODE *hash_table[HASH_SIZE];

void init_hash(void);
NODE *get_node(VALUE n);
NODE *make_node(VALUE n);
void try(VALUE n, NODE *node, OP opcode, unsigned int cost);
void bernstein(VALUE n);


int main(int argc, char **argv)
{
  VALUE n;

  if (argc != 2)
  {
    fprintf(stderr, "Usage: bernstein <constant>\n");
    exit(1);
  }

  n = STRTOVALUE(argv[1]);
  if (errno || n == 0 || even(n))
  {
    fprintf(stderr, "bernstein: bad constant '%s'\n", argv[1]);
    exit(2);
  }

  init_hash();
  bernstein(n);

  return 0;
}


void init_hash(void)
{
  unsigned int i;
  for (i = 0; i < HASH_SIZE; i++)
    hash_table[i] = NULL;
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
    exit(3);
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
    dsup = n >> 1;
    while (d <= dsup)
    {
      if (n % (d - 1) == 0)
        try(n / (d - 1), node, FSUB, SHIFT_COST + SUB_COST);
      if (n % (d + 1) == 0)
        try(n / (d + 1), node, FADD, SHIFT_COST + ADD_COST);
      d <<= 1;
    }
    try(n - 1, node, ADD1, SHIFT_COST + ADD_COST);
    try(n + 1, node, SUB1, SHIFT_COST + SUB_COST);
  }

  return node;
}


void try(VALUE n, NODE *node, OP opcode, unsigned int cost)
{
  NODE *tmp_node;
  unsigned int shift = 0;

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
  printf("Cost = %u\n", node->cost);
}


/* $Id$ */
