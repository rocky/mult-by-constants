/*
 * $Id: qtree.c 1.6 2001/02/01 12:56:33 lefevre Exp lefevre $
 *
 * Calculate f_m(n): [[-m,+m]] -> N such that
 *   1) f_m(n) = 0 for n in E = {0, +2^k, -2^k}, k integer
 *   2) f_m(a+b) <= f_m(a) + f_m(b) + 1
 *   3) f_m(ab) <= f_m(a) + f_m(b)
 *   4) for each n not in E, there exist a and b such that
 *        _ n = a+b and (2) is an equality, or
 *        _ n = ab with |a| > 1 and |b| > 1, and (3) is an equality.
 *
 * Compile options:
 *   -DPARENTS   save the parents a and b in the structure (not useful
 *               for the moment)
 *   -DRESULTS   write information to stdout each time a value is found
 *   -DSORT      sort the linked lists (should be faster)
 *
 * Usage: qtree <m> [<dest_file>]
 *   m: value of m (decimal number)
 *   dest_file: if present, file where the values of f_m are stored
 */

#include <stdio.h>
#include <stdlib.h>
#include <limits.h>

#ifdef PARENTS
#define ADDPARENTS(A, B) \
  t[n].a = (A); \
  t[n].b = (B);
#else
#define ADDPARENTS(A, B)
#endif

#ifdef SORT
#define ADDNEXT
#else
#define ADDNEXT \
  t[n].next = next; \
  next = n;
#endif

#define VALID(A, B) do { \
  t[n].cost = c; \
  ADDPARENTS(A, B) \
  ADDNEXT \
  if (n < nmin) nmin = n; \
  r--; \
  } while (0) \

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
#ifdef PARENTS
  long a, b;
#endif
  long next;
};

typedef struct cell CELL;

int main(int argc, char **argv)
{
  long h, i, m, r;
  int c;
  CELL *t;
  long *first;

  if (argc != 2 && argc != 3)
  {
    fprintf(stderr, "Usage: qtree <m> [<dest_file>]\n");
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

    long next;
    long nmin = LONG_MAX;
    long a, b;
    int ca, cb;

#ifndef SORT
    next = -1;
#endif

    for (ca = 0, cb = c - 1 - ca; cb >= ca; ca++, cb--)
      for (a = first[ca]; a >= 0; a = t[a].next)
        for (b = first[cb]; b >= 0; b = t[b].next)
        {
          long n;

          n = a+b;
          if (n <= m && t[n].cost < 0)
          {
            EMIT(a, b, n, c, '+');
            VALID(a, b);
          }

          n = abs(a-b);
          if (n <= m && t[n].cost < 0)
          {
            EMIT(a, b, n, c, '-');
            VALID(a, -b);
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
            VALID(-a, b);
          }
        }

#ifdef SORT
    for (b = 3; b <= m; b++)
      if (t[b].cost == c && (b & 1 || t[b>>1].cost != c))
#else
    for (b = next; b >= 0; b = t[b].next)
#endif
    {
      unsigned long n;
      for (n = b, a = 2; (n <<= 1) <= m; a <<= 1)
        if (t[n].cost < 0)
        {
          EMIT(a, b, n, c, '*');
          VALID(-a, b);
        }
    }

#ifdef SORT
    next = nmin;
#endif
    first[c] = next;
#ifdef SORT
    for (b = next; b <= m; b++)
      if (t[b].cost == c)
      {
        t[next].next = b;
        next = b;
      }
    t[next].next = -1;
#endif
    printf("Nmin(%d) = %ld\n", c, nmin);
    fflush(stdout);
  }

  if (argc == 3)
  {
    FILE *f;

    f = fopen(argv[2], "wb");
    if (f == NULL)
    {
      fprintf(stderr, "qtree: cannot create file!\n");
      exit(6);
    }
    for (i = 0; i <= m; i++)
    {
      if (t[i].cost > 255)
      {
        fprintf(stderr, "qtree: cost too high!\n");
        exit(7);
      }
      if (putc(t[i].cost, f) < 0)
      {
        fprintf(stderr, "qtree: cannot write to file!\n");
        exit(8);
      }
    }
    if (fclose(f))
    {
      fprintf(stderr, "qtree: cannot close file!\n");
      exit(9);
    }
  }

  return 0;
}
