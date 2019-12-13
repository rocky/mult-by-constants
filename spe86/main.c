/*
 *
 * Multiplication by a Constant -- Rocky Bernstein's 1986 Software Practice and Expereince paper
 *
 * Usage: mult-spe86 <verbosity={0..3}> [ <constant> ... ]
 *
 * Compile with -DNCALLS to get the number of get_node() and try() calls.
 * This is the main program
 */

#include "spe_mult.h"
#include <string.h>
#include <stdbool.h>

#ifdef NCALLS
static unsigned long int ngn = 0, ntry = 0, nmalloc = 0;
#endif

static int errexit(const char* msg, int exit_code) {
  fprintf(stderr, "%s: %s\n", PROGRAM, msg);
  exit(exit_code);
}

static
VALUE string_to_value(char *s)
{
  VALUE n;
  n = STRTOVALUE(s);
  if (errno || n == 0)
    {
      static char buf[30] = "";
      snprintf(buf, sizeof(buf), "bad constant '%s'", s);
      errexit(buf, EXIT_BADCONST);
      exit(EXIT_BADCONST);
    }
  return n;
}

static
void usage(int exit_code)
{
  fprintf(stderr,
	  "Usage: \n"
	  "  %s <verbosity-level> [ <constant> ... ]\n"
	  "  %s -b | --binary [ <constant> ... ] \n"
	  "  %s -V | --version \n"
	  "  %s -h | | -? --help \n"
	  "\n"
	  "<verbosity-level> is an integer from 0..3;\n"
	  "<constant> is a positive integer\n",
	  PROGRAM, PROGRAM, PROGRAM, PROGRAM);
  exit(exit_code);
}


int main(int argc, char **argv)
{
  char *endptr;
  const char *first_arg = argv[1];
  bool binary_cost_only = false;

  /* The following are returned as a result of searching for a multiplication sequence. */
  NODE *node = NULL;
  unsigned int initial_shift = 0;

  if ( (argc < 2) ||
       (strcoll(first_arg, "-h") == 0 ||
	strcoll(first_arg, "--help") == 0 ||
	strcoll(first_arg, "-?") == 0) )
    usage(EXIT_USAGE);

  if ( (strcoll(first_arg, "-V") == 0) ||
       (strcoll(first_arg, "--version") == 0) ) {
    printf("%s, version %s\n", PROGRAM, VERSION);
    exit(EXIT_SUCCESS);
  }

  if ( (strcoll(first_arg, "-b") == 0) ||
       (strcoll(first_arg, "--binary") == 0 ) )
    binary_cost_only = true;
  else {
    verbosity = strtol(first_arg, &endptr, 10);

    /* Check for various possible errors */
    if ((errno == ERANGE && (verbosity == LONG_MAX || verbosity == LONG_MIN))
	|| (errno != 0 && verbosity == 0)) {
      perror("strtol");
      exit(EXIT_BADMODE);
    }

    if (endptr == first_arg) {
      fprintf(stderr, "No digits for verbosity were found in '%s'.\n", first_arg);
      usage(EXIT_BADMODE);
    }
  }

  if (argc > 2)
    {
      unsigned int i;

      for (i = 2; i < argc; i++)
	if (binary_cost_only) {
	  VALUE n = string_to_value(argv[i]);
	  COST cost = binary_mult_cost(n);
	  print_cost(n, cost);
	} else {
	  (void) spe_mult(string_to_value(argv[i]), node, &initial_shift);
	}
    }
  else
    {
      char buffer[64];
      if (binary_cost_only) {
	printf("Using binary-method to show costs only.\n");
      } else {
	printf("Using SP&E instruction searching method.\n");
	printf("Using Note: the verbosity level set to %d.\n", verbosity);
      }
      printf("Note: the verbosity level set to %d.\n", verbosity);
      while (1) {
	  printf("Enter a positive number (or Ctrl-d to exit): ");
	  if (scanf("%63s", buffer) == 1)
	    if (binary_cost_only) {
	      VALUE n = string_to_value(buffer);
	      COST cost = binary_mult_cost(n);
	      print_cost(n, cost);
	    } else {
	      spe_mult(string_to_value(buffer), node, &initial_shift);
	    }
	  else
	    break;
      };
    }

  return EXIT_SUCCESS;
}
