/*
 * $Id$
 *
 * In order to find the possible results (in an interval) that can be
 * obtained with q shift-and-add operations, this program generates a
 * superset S(q) of the DAGs satisfying:
 *   * The DAG has q+1 nodes, the node 0 being called the source
 *     node, and the node q being called the target node.
 *   * Each node has one or two parents, except the source node,
 *     which has no parents.
 *   * From each node, there exists a path leading to the target
 *     node (i.e., there are no useless nodes).
 *
 * Usage: gendags <q>
 *   q: number of nodes + 1 (= number of elementary operations)
 */

#include <stdio.h>
#include <stdlib.h>
#include <assert.h>

#define odd(i) ((i) & 1)
#define even(i) (!odd(i))

int main(int argc, char **argv)
{
  int q;
  int *dag;

  if (argc != 2)
  {
    fprintf(stderr, "Usage: gendags <q>\n");
    exit(1);
  }

  q = atoi(argv[1]);
  if (q < 1)
  {
    fprintf(stderr, "gendags: q must be at least 1\n");
    exit(2);
  }
  if (q > 32)
  {
    fprintf(stderr, "gendags: q must be at most 32\n");
    exit(3);
  }
  if (q == 1)
  {
    printf("(0,0)\n");
    return 0;
  }

  dag = calloc(2*q, sizeof(int));
  if (dag == NULL)
  {
    fprintf(stderr, "sdags: out of memory!\n");
    exit(4);
  }

  while (1)
  {
    unsigned long u;

    do
    {
      int i, j, x, y;

      i = 2*q - 1;
      do
      {
        assert(odd(i) && dag[i] <= dag[i-1]);
        if (dag[i] != dag[i-1])
        {
          y = ++dag[i];
          x = dag[--i];
          goto inc_ok;
        }
        i--;
        assert(even(i) && dag[i] <= i/2);
        if (dag[i] != i/2)
        {
          x = ++dag[i];
          y = 0;
          goto inc_ok;
        }
        i--;
      }
      while (i > 2);
      return 0;

      inc_ok:
      assert(even(i));
      u = (1 << x) | (1 << y);
      for (j = 0; j < i; j++)
        u |= 1 << dag[j];
      while (i < 2*q)
      {
        dag[i] = x;
        dag[i+1] = y;
        i += 2;
      }
    }
    while (u != (1UL << q) - 1);

    {
      int i;
      for (i = 0; i < q; i++)
        printf("(%d,%d)%s", dag[2*i], dag[2*i+1], i < q - 1 ? " " : "\n");
    }
  }
}
