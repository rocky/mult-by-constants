/*
 * $Id$
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

void dagsearch(int q, int *dag)
{
  int i;

  printf("DAG [ ");
  for (i = 0; i < q; i++)
    printf("(%d,%d) ", dag[2*i], dag[2*i+1]);
  printf("]\n");
}

int main(int argc, char **argv)
{
  long mrec, mmax;
  unsigned long line = 0;

  if (argc != 4)
  {
    fprintf(stderr, "Usage: dagsearch <mrec> <mmax> <file>\n");
    exit(1);
  }

  mrec = strtol(argv[1], (char **) NULL, 0);
  if (mrec < 1)
  {
    fprintf(stderr, "dagsearch: mrec must be at least 1\n");
    exit(2);
  }
  if (errno == ERANGE)
  {
    fprintf(stderr, "dagsearch: mrec is too large (out of range)\n");
    exit(3);
  }

  mmax = strtol(argv[2], (char **) NULL, 0);
  if (mmax < mrec)
  {
    fprintf(stderr, "dagsearch: mmax must be greater or equal to mrec\n");
    exit(4);
  }
  if (errno == ERANGE)
  {
    fprintf(stderr, "dagsearch: mmax is too large (out of range)\n");
    exit(5);
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

    dagsearch(q, dag);
  }

  return 0;
}
