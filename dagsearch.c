/*
 * $Id: dagsearch.c 1.4 2001/04/30 08:53:40 lefevre Exp lefevre $
 *
 * Usage: dagsearch <mrec> <mmax> <file>
 *   mrec: maximum recorded value
 *   mmax: maximum considered value in the search
 *   file: file where the values are saved
 *   standard input: list of DAGs (e.g. given by gendags)
 *
 */

#include <stdio.h>
#include <stdlib.h>
#include <errno.h>

#define QMAX 32

#ifdef LONGLONG
typedef unsigned long long int VALUE;
#define VALUEFMT "llu"
#define STRTOVALUE(S) strtoull(S, (char **) NULL, 0)
#else
typedef unsigned long int VALUE;
#define VALUEFMT "lu"
#define STRTOVALUE(S) strtoul(S, (char **) NULL, 0)
#endif

#define DIST(x,y) ((x) >= (y) ? (x) - (y) : (y) - (x))

void dagsearch(int q, int *dag, long mmax)
{
  int i;
  int *o, *r, *s;
  VALUE *x;
  int op[QMAX];  /* 0: add; 1: sub */
  int rs[QMAX];  /* 0: shift on the 1st value,
                    1: shift on the 2nd value */
  int sh[QMAX];  /* shift count */
  VALUE v[QMAX+1];  /* values */
  VALUE vp[2*QMAX];

  printf("DAG [ ");
  for (i = 0; i < q; i++)
    printf("(%d,%d) ", dag[2*i], dag[2*i+1]);
  printf("]\n");

  o = op - 1;
  r = rs - 1;
  s = sh - 1;
  x = vp - 2;
  dag -= 2;
  v[0] = 1;
  for (i = 0; ;)
  {
    if (i == q)
    {
    next:
      s[i]++;
      x[2*i+r[i]] <<= 1;
      v[i] = o[i] ? DIST(x[2*i], x[2*i+1]) : x[2*i] + x[2*i+1];
    }
    else
    {
      i++;
      x[2*i] = v[dag[2*i]];
      x[2*i+1] = v[dag[2*i+1]];
      o[i] = 0;
      r[i] = 0;
      s[i] = 0;
      v[i] = x[2*i] + x[2*i+1];
    }
    while (v[i] > mmax)
    {
      x[2*i] = v[dag[2*i]];
      x[2*i+1] = v[dag[2*i+1]];
      if (r[i] == 0 && s[i])
      {
        x[2*i+1] <<= 1;
        r[i] = 1;
        s[i] = 1;
        v[i] = o[i] ? DIST(x[2*i], x[2*i+1]) : x[2*i] + x[2*i+1];
      }
      else if (o[i] == 0)
      {
        o[i] = 1;
        r[i] = 0;
        s[i] = 0;
        v[i] = DIST(x[2*i], x[2*i+1]);
      }
      else if (--i)
        goto next;
      else
        return;
    }
    if (v[i] == 0)
      goto next;
    {
      int j;
      for (j = 0; j < i; j++)
      {
        VALUE x;
        x = v[j];
        while (x < v[i])
          x <<= 1;
        if (x == v[i])
          goto next;
      }
    }
#ifndef NDEBUG
    printf("%3d: %3" VALUEFMT "  ( %3" VALUEFMT " %3" VALUEFMT " )\n",
           i, v[i], x[2*i], x[2*i+1]);
#endif
  }
}

int main(int argc, char **argv)
{
  VALUE mrec, mmax;
  unsigned long line = 0;

  if (argc != 4)
  {
    fprintf(stderr, "Usage: dagsearch <mrec> <mmax> <file>\n");
    exit(1);
  }

  mrec = STRTOVALUE(argv[1]);
  if (errno == ERANGE)
  {
    fprintf(stderr, "dagsearch: mrec is too large (out of range)\n");
    exit(3);
  }
  if (mrec < 1)
  {
    fprintf(stderr, "dagsearch: mrec must be at least 1\n");
    exit(2);
  }

  mmax = STRTOVALUE(argv[2]);
  if (errno == ERANGE)
  {
    fprintf(stderr, "dagsearch: mmax is too large (out of range)\n");
    exit(5);
  }
  if (mmax < mrec)
  {
    fprintf(stderr, "dagsearch: mmax must be greater or equal to mrec\n");
    exit(4);
  }

  while (1)
  {
    int q;
    int dag[2*QMAX];
    char buffer[8];

    line++;
    for (q = 0; scanf("%1[\n]", buffer) == 0; q++)
    {
      if (q > QMAX)
      {
        fprintf(stderr, "dagsearch: too many nodes line %lu\n", line);
        exit(6);
      }
      if (scanf("(%7[(),0-9])", buffer) != 1 ||
          sscanf(buffer, "%d,%d", dag+2*q, dag+2*q+1) != 2)
      {
        fprintf(stderr, "dagsearch: input error line %lu (bad format?)\n",
                line);
        exit(7);
      }
      scanf("%*[\t ]");
    }

    if (!q)
    {
      if (feof(stdin))
        break;
      fprintf(stderr, "dagsearch: input error line %lu (bad format?)\n",
              line);
      exit(8);
    }

    dagsearch(q, dag, mmax);
  }

  return 0;
}
