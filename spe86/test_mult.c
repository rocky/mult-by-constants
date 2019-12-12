/*
 *
 * Test program for mult_spe() function.
 */

#include "spe_mult.h"

#ifdef NCALLS
static unsigned long int ngn = 0, ntry = 0, nmalloc = 0;
#endif

#define ARRAY_SIZE(arr)     (sizeof(arr) / sizeof((arr)[0]))

static void check_costs(VALUE n, COST got, COST expected,
			unsigned int shift_got, unsigned int shift_expected)
{
  if (got != expected || expected != expected) {
    fprintf(stderr,
	    "For number %" VALUEFMT
	    ", expecting cost %" COSTFMT ", got %" COSTFMT
	    ", expecting shift %u, got %u instead.\n",
	    n, expected, got, shift_expected, shift_got);
    exit(EXIT_FAILURE);
  }
}

int main(int argc, char **argv)
{
  int values[] = {51, 10};
  int expected_cost[] = {4, 3};
  int expected_shift[] = {0, 1};
  NODE *node = NULL;
  unsigned int initial_shift = 0;

  for (int i = 0; i < ARRAY_SIZE(values); i++) {
    int n = values[i];
    unsigned int cost = spe_mult(n, node, &initial_shift);
    check_costs(n, cost, expected_cost[i], initial_shift, expected_shift[i]);
  }
  return EXIT_OK;
}
