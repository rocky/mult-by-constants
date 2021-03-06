/*
 * $Id: gendags.c 1.5 2002/12/31 19:03:52 lefevre Exp lefevre $
 *
 * In order to find the possible results (in an interval) that can be
 * obtained with q shift-and-add operations, this program generates a
 * superset S(q) of the DAGs satisfying:
 *   * The DAG has q+1 nodes, denoted from 0 to q, the node 0 being called
 *     the source node, and the node q being called the target node.
 *   * Each node has one or two parents, except the source node,
 *     which has no parents.
 *   * From each node, there exists a path leading to the target node
 *     (i.e., there are no useless nodes): each node except the target
 *     node has at least one child.
 *
 * A node different from the source node will be represented by a pair of
 * integers (x,y) such that x >= y, where x and y are the parents (x = y
 * if there is only one parent). Since we seek to return DAGs up to an
 * isomorphism, nodes will be ordered in such a way that between nodes
 * (x,y) and (x',y'), the smaller one in the lexicographic order will
 * come first. Moreover a simple isomorphism search will be performed;
 * for instance, in each example, only the first DAG will be returned:
 *   * Example 1:
 *     (0,0) (0,0) (1,0) (3,2)
 *     (0,0) (0,0) (2,0) (3,1)
 *   * Example 2:
 *     (0,0) (0,0) (2,1) (3,1)
 *     (0,0) (0,0) (2,1) (3,2)
 *   * Example 3:
 *     (0,0) (0,0) (1,1) (3,2)
 *     (0,0) (0,0) (2,2) (3,1)
 *
 * Usage: gendags <level> <q>
 *   q: number of nodes + 1 (= number of elementary operations)
 *   level:
 *     0 -> pairs must be ordered.
 *     1 -> level 0 + simple isomorphism search.
 *   e.g.
 *     $ diff <(./gendags 0 4) <(./gendags 1 4)
 *     3d2
 *     < (0,0) (0,0) (2,0) (3,1)
 *     6d4
 *     < (0,0) (0,0) (2,1) (3,2)
 *     8d5
 *     < (0,0) (0,0) (2,2) (3,1)
 */

#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include <limits.h>
#include <errno.h>

#define odd(i) ((i) & 1)
#define even(i) (!odd(i))

int readint(char *value, char *var, int min, int max)
{
  long tmp;
  char *end;

  tmp = strtol(value, &end, 10);
  if (*end != '\0' || errno == ERANGE || tmp < min || tmp > max)
    {
      fprintf(stderr, "gendags: bad input value %s (must be in [%d,%d])\n",
              var, min, max);
      exit(2);
    }
  return (int) tmp;
}

int main(int argc, char **argv)
{
  int level;
  int q;
  int *dag;

  if (argc != 3)
    {
      fprintf(stderr, "Usage: gendags <level> <q>\n");
      exit(1);
    }

  level = readint(argv[1], "level", 0, INT_MAX);
  q = readint(argv[2], "q", 1, 31);
  if (q == 1)
    {
      printf("(0,0)\n");
      return 0;
    }

  dag = calloc(2*q, sizeof(int));
  if (dag == NULL)
    {
      fprintf(stderr, "gendags: out of memory!\n");
      exit(5);
    }

  while (1)
    {
      unsigned long u;

    nextdag:
      do
        {
          int i, j, x, y;

          i = 2*q - 1;
          do
            {
              assert(odd(i) && dag[i] <= dag[i-1]);
              if (dag[i] != dag[i-1])
                {
                  y = dag[i] + 1;
                  x = dag[--i];
                  goto inc_ok;
                }
              i--;
              assert(even(i) && dag[i] <= i/2);
              if (dag[i] != i/2)
                {
                  x = dag[i] + 1;
                  y = 0;
                  goto inc_ok;
                }
              i--;
            }
          while (i > 2);
          return 0;

        inc_ok:
          assert(even(i));
          u = (1UL << x) | (1UL << y);
          for (j = 0; j < i; j++)
            u |= 1UL << dag[j];
          while (i < 2*q)
            {
              dag[i] = x;
              dag[i+1] = y;
              i += 2;
            }
        }
      while (u != (1UL << q) - 1);

      if (level)
        {
          int i;

          for (i = 0; i < q-2; i++)
            {
              int j, x, y;

              x = dag[2*i];
              y = dag[2*i+1];
              j = i;
              do
                {
                  j++;
                  assert(j < q);  /* because the last pair contains q-1 and
                                     is different from the other ones */
                }
              while (dag[2*j] == x && dag[2*j+1] == y);
              if (j - i > 1)  /* number of identical pairs */
                while (j < q)
                  {
                    unsigned long v;
                    v = ( ((1UL << dag[2*j]) | (1UL << dag[2*j+1]))
                          >> (i+1) ) & 3;
                    if (v == 1)  /* 1st pair referenced, not the 2nd -> OK */
                      break;
                    if (v == 2)  /* 2nd pair referenced, not the 1st -> rej */
                      goto nextdag;
                    j++;
                  }
            }  /* loop i */
        }  /* if (level) */

      {
        int i;
        for (i = 0; i < q; i++)
          printf("(%d,%d)%s", dag[2*i], dag[2*i+1], i < q - 1 ? " " : "\n");
      }
    }
}
