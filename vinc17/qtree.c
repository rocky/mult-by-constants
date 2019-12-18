/*
 * $Id: qtree.c 1.16 2001/02/28 14:10:44 lefevre Exp lefevre $
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
 *   -DLOWMEM    low memory (--> PARENTS is undefined)
 *
 * Usage: qtree <cmax> <m> [[-]<dest_file>]
 *   cmax: maximal cost (-1 if no maximal cost)
 *   m: value of m (decimal number)
 *   dest_file: if present, file where the values of f_m are stored
 *   -dest_file: the file is saved at each iteration
 */

#include <stdio.h>
#include <stdlib.h>
#include <limits.h>

#ifdef LOWMEM

#undef PARENTS

#define COST(X) t[X]

#define FRST(X) X = first[c##X], v##X = u[c##X]

#define NEXT(X) do { \
    long k; \
    k = *(v##X++); \
    if (k && COST(X+k) == c##X) \
      X += k; \
    else \
    { \
      k += *(v##X++) << 8; \
      if (k && COST(X+k) == c##X) \
        X += k; \
      else \
      { \
        k += *(v##X++) << 16; \
        if (k && COST(X+k) == c##X) \
          X += k; \
        else \
        { \
          k += *(v##X++) << 24; \
          if (k) \
            X += k; \
          else \
            X = -1; \
        } \
      } \
    } \
  } while (0)

#define SETNEXT(X,V)

static size_t setu0(char *t, char *z, unsigned char *v)
{
  size_t s = 4;
  long d = 0;
  int c;

  c = *t;
  while (++d, ++t <= z)
    if (*t == c)
      for (; d; d >>= 8)
      {
        s++;
        if (v)
          *(v++) = (unsigned char) d;
      }
  if (v)
    v[0] = v[1] = v[2] = v[3] = 0;
  return s;
}

static void setu(char *t, char *z, unsigned char **u)
{
  unsigned long s;
  s = setu0(t, z, NULL);
  printf("Memory requested: %lu bytes\n", s);
  fflush(stdout);
  *u = malloc(s);
  if (*u == NULL)
  {
    fprintf(stderr, "qtree: out of memory!\n");
    exit(7);
  }
  (void) setu0(t, z, *u);
}

#else

#define COST(X) t[X].cost
#define FRST(X) X = first[c##X]
#define NEXT(X) X = t[X].next
#define SETNEXT(X,V) t[X].next = V

#endif

#ifdef PARENTS
#define ADDPARENTS(A, B) \
  t[n].a = (A); \
  t[n].b = (B);
#else
#define ADDPARENTS(A, B)
#endif

#define VALID(A, B) do { \
    COST(n) = c; \
    ADDPARENTS(A, B) \
    if (n < nmin) nmin = n; \
    r--; \
  } while (0)

#ifdef RESULTS

#define EMIT(a, b, n, c, o) emit(a, b, n, c, o)

static void emit(long a, long b, long n, int c, int o)
{
  printf("Cost %d: %8ld %c %8ld -> %8ld\n", c, a, o, b, n);
}

#else

#define EMIT(a, b, n, c, o)

#endif

#ifdef LOWMEM

typedef signed char CELL;
CELL cost;

#else

struct cell
{
  int cost;
#ifdef PARENTS
  long a, b;
#endif
  long next;
};

typedef struct cell CELL;

#endif

#define WRITEFILE do { \
    for (i = 0; i <= m; i++) \
    { \
      if (COST(i) > 126) \
      { \
        fprintf(stderr, "qtree: cost too high!\n"); \
        exit(33); \
      } \
      if (putc(COST(i), f) < 0) \
      { \
        fprintf(stderr, "qtree: cannot write to file!\n"); \
        exit(34); \
      } \
    } \
    if (fclose(f)) \
    { \
      fprintf(stderr, "qtree: cannot close file!\n"); \
      exit(35); \
    } \
  } while (0)

int main(int argc, char **argv)
{
  int flag = -1;   /* -1: results not saved;
                       0: results saved at each iteration;
                       1: results saved at the end */
  char *file = NULL;
  long h, i, m, r;
  int c, cmax;
  CELL *t;
  long *first;

#ifdef LOWMEM
  unsigned char **u;
#endif

  if (argc != 3 && argc != 4)
  {
    usage: fprintf(stderr, "Usage: qtree <cmax> <m> [[-]<dest_file>]\n");
    exit(1);
  }

  cmax = atoi(argv[1]);
  if (cmax < 0)
    printf("No maximal cost\n");
  else
    printf("Maximal cost: %d\n", cmax);

  m = atol(argv[2]);
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

  if (argc == 4)
  {
    file = argv[3];
    flag = file[0] != '-';
    if (!flag && *(++file) == '\0')
      goto usage;
    printf(flag ? "Results saved at the end\n"
                : "Results saved at each iteration\n");
  }
  else
    file = NULL;  /* to avoid the warning with gcc 2.95.2 */

  for (i = 2; i <= m; i++)
    COST(i) = -1;  /* not valid yet */

  COST(0) = 0;
  r = m;  /* number of unitialized cells */
  for (h = 0, i = 1, c = 0; i <= m; h = i, i <<= 1, c++)
  {
    COST(i) = 0;
    SETNEXT(h,i);
    r--;
  }
  SETNEXT(h,-1);  /* last element in list */

  first = malloc(c * sizeof(*first));
  if (first == NULL)
  {
    fprintf(stderr, "qtree: out of memory!\n");
    exit(5);
  }
  first[0] = 0;

#ifdef LOWMEM
  u = malloc(c * sizeof(*u));
  if (u == NULL)
  {
    fprintf(stderr, "qtree: out of memory!\n");
    exit(6);
  }
  setu(t, t + m, u);
#endif

  for (c = 1; r && (cmax < 0 || c <= cmax); c++)
  {
    /* find all the positive integers n such that f_m(n) = c */

    long nmin = LONG_MAX;
    long a, b;
    int ca, cb;

#ifdef LOWMEM
    unsigned char *va, *vb;
#else
    long next;
#endif

    for (ca = 0, cb = c - 1 - ca; cb >= ca; ca++, cb--)
      for (FRST(a); a >= 0;)
      { /* loop a */

        FRST(b);

        while ((unsigned long) b < a)
        { /* loop b1 */
          long n;

          n = a+b;
          if (n <= m && COST(n) < 0)
          {
            EMIT(a, b, n, c, '+');
            VALID(a, b);
          }

          n = a-b;
          if (COST(n) < 0)
          {
            EMIT(a, b, n, c, '-');
            VALID(a, -b);
          }

          NEXT(b);
        } /* loop b1 */

        while (b >= 0)
        { /* loop b2 */
          long n;

          n = a+b;
          if (n > m) break;
          if (COST(n) < 0)
          {
            EMIT(a, b, n, c, '+');
            VALID(a, b);
          }

          n = b-a;
          if (COST(n) < 0)
          {
            EMIT(a, b, n, c, '-');
            VALID(a, -b);
          }

          NEXT(b);
        } /* loop b2 */

        while (b >= 0)
        { /* loop b3 */
          long n;

          n = b-a;
          if (COST(n) < 0)
          {
            EMIT(a, b, n, c, '-');
            VALID(a, -b);
          }

          NEXT(b);
        } /* loop b3 */

        NEXT(a);
      } /* loop a */

    for (ca = 1, cb = c - ca; cb >= ca; ca++, cb--)
      for (FRST(a); a >= 0;)
      {
        for (FRST(b); b >= 0;)
        {
          unsigned long long n;
          n = (unsigned long long) a * (unsigned long long) b;
          if (n > m) break;
          if (COST(n) < 0)
          {
            EMIT(a, b, (long) n, c, '*');
            VALID(-a, b);
          }
          NEXT(b);
        }
        NEXT(a);
      }

    for (b = 3; b <= m; b++)
      if (COST(b) == c && (b & 1 || COST(b>>1) != c))
    {
      unsigned long n;
      for (n = b, a = 2; (n <<= 1) <= m; a <<= 1)
        if (COST(n) < 0)
        {
          EMIT(a, b, n, c, '*');
          VALID(-a, b);
        }
    }

    first[c] = nmin;

#ifdef LOWMEM
    setu(t + nmin, t + m, u + c);
#else
    next = nmin;
    for (b = next; b <= m; b++)
      if (COST(b) == c)
      {
        SETNEXT(next,b);
        next = b;
      }
    SETNEXT(next,-1);
#endif

    printf("Nmin(%d) = %ld\n", c, nmin);
    fflush(stdout);

    if (flag == 0)  /* temporary results */
    {
      FILE *f;

      f = fopen(file, "r+b");
      if (f == NULL)
      {
        f = fopen(file, "wb");
        if (f == NULL)
        {
          fprintf(stderr, "qtree: cannot open file (update or create)!\n");
          exit(32);
        }
      }
      WRITEFILE;
    }
  }

  if (flag == 1)  /* final results */
  {
    FILE *f;

    f = fopen(file, "wb");
    if (f == NULL)
    {
      fprintf(stderr, "qtree: cannot create file!\n");
      exit(32);
    }
    WRITEFILE;
  }

  return 0;
}
