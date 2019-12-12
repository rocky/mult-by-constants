/*
 *
 * Test program for mult_spe() function.
 */

#include "spe_mult.h"
#include <assert.h>

#ifdef NCALLS
static unsigned long int ngn = 0, ntry = 0, nmalloc = 0;
#endif

#define ARRAY_SIZE(arr)     (sizeof(arr) / sizeof((arr)[0]))

int main(int argc, char **argv)
{
  init_hash();
  int values[] = {51, 10};
  int expected_cost[] = {4, 3};

  for (int i = 0; i < ARRAY_SIZE(values); i++) {
    NODE *node;
    int n = values[i];
    unsigned int cost = spe_mult(n, node);
    assert(cost == expected_cost[i]);
  }
  return EXIT_OK;
}
