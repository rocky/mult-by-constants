/*
 * $Id$
 *
 * Calculate f_m(n): [[-m,+m]] -> N such that
 *   1) f_m(n) = 0 for n in E = {0, +2^k, -2^k}, k integer
 *   2) f_m(a+b) <= f_m(a) + f_m(b) + 1
 *   3) f_m(ab) <= f_m(a) + f_m(b)
 *   4) for each n not in E, there exist a and b such that
 *        _ n = a+b and (2) is an equality, or
 *        _ n = ab with |a| > 1 and |b| > 1, and (3) is an equality.
 */

#include <stdio.h>
#include <stdlib.h>
#include <limits.h>

#ifdef RESULTS

#define EMIT(a, b, n, c, o) emit(a, b, n, c, o)

void emit(long a, long b, long n, int c, int o)
{
  printf("Cost %d: %8ld %c %8ld -> %8ld\n", c, a, o, b, n);
}

#else

#define EMIT(a, b, n, c, o)

#endif

struct cell
{
  int cost;
  long a, b;
  long next;
};

typedef struct cell CELL;

int main(int argc, char **argv)
{
  long h, i, m, r;
  int c;
  CELL *t;
  long *first;

  if (argc != 2)
  {
    fprintf(stderr, "Usage: qtree <m>\n");
    exit(1);
  }

  m = atol(argv[1]);
  if (m < 1)
  {
    fprintf(stderr, "qtree: m must be at least 1\n");
    exit(2);
  }

  if (m >= (1UL << 31) || m >= LONG_MAX / sizeof(CELL) - 1)
  {
    fprintf(stderr, "qtree: m too large\n");
    exit(3);
  }

  t = malloc((m+1) * sizeof(CELL));
  if (t == NULL)
  {
    fprintf(stderr, "qtree: out of memory!\n");
    exit(4);
  }

  for (i = 2; i <= m; i++)
    t[i].cost = -1;  /* not valid yet */

  t[0].cost = 0;
  r = m;  /* number of unitialized cells */
  for (h = 0, i = 1, c = 0; i <= m; h = i, i <<= 1, c++)
  {
    t[i].cost = 0;
    t[h].next = i;
    r--;
  }
  t[h].next = -1;  /* last element in list */

  first = malloc(c * sizeof(*first));
  if (first == NULL)
  {
    fprintf(stderr, "qtree: out of memory!\n");
    exit(5);
  }
  first[0] = 0;

  for (c = 1; r; c++)
  {
    /* find all the positive integers n such that f_m(n) = c */

    long next = -1;
    long a, b;
    int ca, cb;

    for (ca = 0, cb = c - 1 - ca; cb >= ca; ca++, cb--)
      for (a = first[ca]; a >= 0; a = t[a].next)
        for (b = first[cb]; b >= 0; b = t[b].next)
        {
          long n;

          n = a+b;
          if (n <= m && t[n].cost < 0)
          {
            EMIT(a, b, n, c, '+');
            t[n].cost = c;
            t[n].a = a;
            t[n].b = b;
            t[n].next = next;
            next = n;
            r--;
          }

          n = abs(a-b);
          if (n <= m && t[n].cost < 0)
          {
            EMIT(a, b, n, c, '-');
            t[n].cost = c;
            t[n].a = a;
            t[n].b = -b;
            t[n].next = next;
            next = n;
            r--;
          }
        }

    for (ca = 1, cb = c - ca; cb >= ca; ca++, cb--)
      for (a = first[ca]; a >= 0; a = t[a].next)
        for (b = first[cb]; b >= 0; b = t[b].next)
        {
          unsigned long long n;
          n = (unsigned long long) a * (unsigned long long) b;
          if (n <= m && t[n].cost < 0)
          {
            EMIT(a, b, (long) n, c, '*');
            t[n].cost = c;
            t[n].a = -a;
            t[n].b = b;
            t[n].next = next;
            next = n;
            r--;
          }
        }

    for (b = next; b >= 0; b = t[b].next)
    {
      unsigned long n;
      for (n = b, a = 2; (n <<= 1) <= m; a <<= 1)
        if (t[n].cost < 0)
        {
          EMIT(a, b, n, c, '*');
          t[n].cost = c;
          t[n].a = -a;
          t[n].b = b;
          t[n].next = next;
          next = n;
          r--;
        }
    }

    first[c] = next;
  }

  return 0;
}
