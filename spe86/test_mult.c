/*
 *
 * Test program for mult_spe() function.
 */

#include <string.h>
#include "spe_mult.h"
#include "util.h"

#ifdef NCALLS
static unsigned long int ngn = 0, ntry = 0, nmalloc = 0;
#endif

#define ARRAY_SIZE(arr)     (sizeof(arr) / sizeof((arr)[0]))

static void check_costs(VALUE n, const char method[], COST got, COST expected,
			unsigned int shift_got, unsigned int shift_expected)
{
  if (got != expected) {
    fprintf(stderr,
	    "Using method %s for number %" VALUEFMT
	    ", expecting cost %" COSTFMT ", got %" COSTFMT
	    " instead.\n",
	    method, n, expected, got);
    exit(EXIT_FAILURE);
  }
  if (shift_got != shift_expected) {
    fprintf(stderr,
	    "Using method %s for number %" VALUEFMT
	    ", expecting shift %u, got %u instead.\n",
	    method, n, shift_expected, shift_got);
    exit(EXIT_FAILURE);
  }
}

int main(int argc, char **argv)
{
  int values[] = {16, 51, 10};
  int expected_cost[] = {1, 4, 3};
  int expected_shift[] = {4, 0, 1};
  int expected_binary_cost_to16[] = {1,
				     0, 1, 2, 1, 2, 3, 2, 1,
				     2, 3, 4, 3, 4, 3, 2, 1};

  NODE *node = NULL;
  unsigned int initial_shift = 0;

  const char* bin_strings[] =
    {
     "0",
     "1",
     "10",
     "11",
     "100",
     "101",
     "110",
     "111",
     "1000",
     "1001",
     "1010",
     "1011",
     "1100",
     "1101",
     "1110",
     "1111",
     "10000"
    };

  int exit_rc = EXIT_OK;
  // Test format_binary-value
  for (int i=0; i <= 16; i++) {
    char *str = format_binary_value(i);

    // debug:
    // printf("format_binary_value: got %s, expected %s\n",
    //	     str, bin_strings[i]);

    if (strncmp(str, bin_strings[i], strlen(str)) != 0) {
      printf("format_binary_value: got %s, expected %s\n",
	     str, bin_strings[i]);
      exit_rc = EXIT_FAILURE;
    }

  }

  // Test binary cost method
  for (int n = 0; n < ARRAY_SIZE(expected_binary_cost_to16); n++) {
    // printf("Trying  %d\n", n);
    COST cost = binary_mult_cost((VALUE) n);
    // printf("%d cost %g\n", n, cost);
    check_costs(n, "binary method", cost, expected_binary_cost_to16[n],
  		0, 0);
  }

  // Test SPE multiplication method
  for (int i = 0; i < ARRAY_SIZE(values); i++) {
    int n = values[i];
    unsigned int cost = spe_mult(n, node, &initial_shift);
    check_costs(n, "spe method", cost, expected_cost[i],
  		initial_shift, expected_shift[i]);
  }
  return exit_rc;
}
