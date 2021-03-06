/*
 * $Id: dagsearch.c 1.13 2002/12/28 03:03:37 lefevre Exp lefevre $
 *
 * Usage: dagsearch <mrec> <mmax> <cost> [ <cinf> <csup> <code> ]
 *   mrec: maximum recorded value
 *   mmax: maximum considered value in the search
 *   cost: file where the costs are saved
 *   cinf: file where the cinf values are saved
 *   csup: file where the csup values are saved
 *   code: file where the codes corresponding to cinf and csup are saved
 *   standard input: list of DAGs (e.g. given by gendags)
 *
 * Define SHIFTS to compute cinf and csup.
 *
 * In practice, searches will be performed with DAGs whose length is
 * not larger than 6. Thus, a code can be encoded in 8 bytes: 2 bytes
 * for the DAG number and one byte for each elementary operation: for
 * each operation, the type of the operation is encoded in the most
 * significant 2 bits and the shift count (assumed to be <= 63) is
 * stored in the other 6 bits. When the shift count is 0, the shifted
 * value is assumed to be the second one; thus the byte corresponding
 * to an operation is never 0. Therefore, the sequences shorter than
 * 8 bytes can be padded with null bytes.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
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

#ifdef NDEBUG
#define OUT(...)
#else
#define OUT(...) printf(__VA_ARGS__)
#endif

#define DIST(x,y) ((x) >= (y) ? (x) - (y) : (y) - (x))

#ifdef SHIFTS
void stcode(unsigned char *code, int *o, int *r, int *s,
            unsigned int line, int q)
{
  int i;

  code[0] = (unsigned char) line;
  code[1] = (unsigned char) (line >> 8);
  code++;
  for (i = 1; i <= q; i++)
    *(++code) = (o[i] << 7) | (r[i] << 6) | s[i];
  while (i++ <= 6)
    *(++code) = 0;
}
#endif

void dagsearch(int q, int *dag, unsigned char *cost,
#ifdef SHIFTS
               unsigned char *cinf,
               unsigned char *csup,
               unsigned char *code,
               unsigned int line,
#endif
               long mrec, long mmax)
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
  fflush(stdout);

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
          r[i] = 1;
          s[i] = 0;
          v[i] = x[2*i] + x[2*i+1];
        }
      while (v[i] > mmax)
        {
          x[2*i] = v[dag[2*i]];
          x[2*i+1] = v[dag[2*i+1]];
          if (r[i] && s[i])
            {
              x[2*i] <<= 1;
              r[i] = 0;
              s[i] = 1;
              v[i] = o[i] ? DIST(x[2*i], x[2*i+1]) : x[2*i] + x[2*i+1];
            }
          else if (o[i] == 0)
            {
              o[i] = 1;
              r[i] = 1;
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
      if (i < q)
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
      OUT("%3d: %3" VALUEFMT "  ( %3" VALUEFMT " %3" VALUEFMT " )",
          i, v[i], x[2*i], x[2*i+1]);
      if (v[i] <= mrec)
        {
          if (cost[v[i]] > i)
            {
              cost[v[i]] = i;
              OUT("   -   Cost(%3" VALUEFMT ") = %d", v[i], i);
#ifdef SHIFTS
              if (v[i] & 1)
                {
                  unsigned int cmax = 0;
                  int j;
                  for (j = 0; j < i; j++)
                    if (sh[j] > cmax)
                      cmax = sh[j];
                  cinf[v[i]] = cmax;
                  csup[v[i]] = cmax;
                  stcode(code + (v[i]<<3) - 8, o, r, s, line, i);
                  stcode(code + (v[i]<<3), o, r, s, line, i);
                }
#endif
            }
#ifdef SHIFTS
          if ((v[i] & 1) && cost[v[i]] == i)
            {
              unsigned int cmax = 0;
              int j;
              for (j = 0; j < i; j++)
                if (sh[j] > cmax)
                  cmax = sh[j];
              if (cinf[v[i]] > cmax)
                {
                  cinf[v[i]] = cmax;
                  stcode(code + (v[i]<<3) - 8, o, r, s, line, i);
                }
              if (csup[v[i]] < cmax)
                {
                  csup[v[i]] = cmax;
                  stcode(code + (v[i]<<3), o, r, s, line, i);
                }
            }
#endif
        }
      OUT("\n");
    }
}

void save(unsigned char *array, VALUE size, char *filename)
{
  FILE *f;

  f = fopen(filename, "wb");
  if (f == NULL)
    {
      fprintf(stderr, "dagsearch: cannot create file %s\n", filename);
      exit(11);
    }
  if (fwrite(array, size, 1, f) != 1)
    {
      fprintf(stderr, "dagsearch: cannot write to file %s\n", filename);
      exit(12);
    }
  if (fclose(f))
    {
      fprintf(stderr, "dagsearch: cannot close file %s\n", filename);
      exit(13);
    }
}

int main(int argc, char **argv)
{
  VALUE mrec, mmax;
  unsigned int line = 0;
  unsigned char *cost;
#ifdef SHIFTS
  unsigned char *cinf, *csup, *code;
#endif

#ifndef SHIFTS
  if (argc != 4)
    {
      fprintf(stderr, "Usage: dagsearch <mrec> <mmax> <file>\n");
      exit(1);
    }
#else
  if (argc != 7)
    {
      fprintf(stderr, "Usage: dagsearch <mrec> <mmax>"
              " <cost> <cinf> <csup> <code>\n");
      exit(1);
    }
#endif

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

  cost = malloc(mrec+1);
  if (cost == NULL)
    {
      fprintf(stderr, "dagsearch: out of memory!\n");
      exit(10);
    }
  memset(cost, -1, mrec+1);
  cost[0] = 0;
  cost[1] = 0;

#ifdef SHIFTS
  cinf = malloc(mrec+1);
  csup = malloc(mrec+1);
  code = malloc((mrec+1) << 3);
  if (cinf == NULL || csup == NULL || code == NULL)
    {
      fprintf(stderr, "dagsearch: out of memory!\n");
      exit(10);
    }
  cinf[0] = csup[0] = 0;
  cinf[1] = csup[1] = 0;
  memset(code, 0, 16);
#endif

  while (1)
    {
      VALUE v;
      int q;
      int dag[2*QMAX];
      char buffer[8];

      line++;
      for (q = 0; scanf("%1[\n]", buffer) == 0; q++)
        {
          if (q > QMAX)
            {
              fprintf(stderr, "dagsearch: too many nodes at line %u\n",
                      line);
              exit(6);
            }
          if (scanf("(%7[,0-9])", buffer) != 1 ||
              sscanf(buffer, "%d,%d", dag+2*q, dag+2*q+1) != 2)
            {
              fprintf(stderr, "dagsearch: input error at line %u\n", line);
              exit(7);
            }
          scanf("%*[\t ]");
        }

      if (!q)
        {
          if (feof(stdin))
            return 0;
          fprintf(stderr, "dagsearch: input error at line %u\n", line);
          exit(8);
        }

      dagsearch(q, dag, cost,
#ifdef SHIFTS
                cinf, csup, code, line,
#endif
                mrec, mmax);

      for (v = 1; v < mrec; v += 2)
        {
          VALUE w;
          int c;

          c = cost[v];
          w = v;
          while ((w <<= 1) <= mrec)
            if (cost[w] > c)
              {
                cost[w] = c;
#ifdef SHIFTS
                cinf[w] = csup[w] = 0;
#endif
              }
        }

      save(cost, mrec+1, argv[3]);
#ifdef SHIFTS
      save(cinf, mrec+1, argv[4]);
      save(csup, mrec+1, argv[5]);
      save(code, (mrec+1) << 3, argv[6]);
#endif
    }
}
