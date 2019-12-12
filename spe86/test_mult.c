/*
 *
 * Test program for mult_spe() function.
 */

#include "spe_mult.h"

#ifdef NCALLS
static unsigned long int ngn = 0, ntry = 0, nmalloc = 0;
#endif

#define ARRAY_SIZE(arr)     (sizeof(arr) / sizeof((arr)[0]))

static void check_costs(VALUE n, COST got, COST expected)
{
  if (got != expected) {
    fprintf(stderr,
	    "For number %" VALUEFMT
	    ", expecting cost %" COSTFMT ", got %" COSTFMT
	    " instead.", n, got, expected);
    exit(EXIT_FAILURE);
  }
}

int main(int argc, char **argv)
{
  init_hash();
  int values[] = {51, 10};
  int expected_cost[] = {4, 3};

  for (int i = 0; i < ARRAY_SIZE(values); i++) {
    NODE *node;
    int n = values[i];
    unsigned int cost = spe_mult(n, node);
    check_costs(n, cost, expected_cost[i]);
  }
  return EXIT_OK;
}
