#include "util.h"

extern int errexit(const char* msg, int exit_code) {
  fprintf(stderr, "%s: %s\n", PROGRAM, msg);
  exit(exit_code);
}

static char bin_string[sizeof(VALUE)<<3];

/* Adapted from
   https://stackoverflow.com/questions/111928/is-there-a-printf-converter-to-print-in-binary-format
*/
extern
char *format_binary_value(VALUE n)
{
  int j = 0;
  char *start = bin_string;
  for(int i = sizeof(n)<<3; i; i--, j++) {
    bin_string[j] = '0' + ((n>>(i-1)) & 1);
  }
  bin_string[j+1] = '\0';
  while (*start++ == '0') ;
  return --start;
}

extern void
print_cost(VALUE n, COST cost) {
  char *str = format_binary_value(n);
  printf("%" VALUEFMT " = %s, cost: %" COSTFMT "\n", n, str, cost);
}
