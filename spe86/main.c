/*
 *
 * Multiplication by a Constant -- Rocky Bernstein's 1986 Software Practice and Expereince paper
 *
 * Usage: mult-spe86 <verbosity={0 | 1 | 2} [ <constant> ... ]
 *
 * Compile with -DNCALLS to get the number of get_node() and try() calls.
 * This is the main program
 */

#include "spe_mult.h"
#include <string.h>
#include <limits.h>

#ifdef NCALLS
static unsigned long int ngn = 0, ntry = 0, nmalloc = 0;
#endif

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
  fprintf(stderr, "Usage: %s <verbosity-level> [ <constant> ... ]\n"
	  "  verbosity-level 0,1,2\n"
	  "  num: a positive integer\n", PROGRAM);
  exit(exit_code);
}


int main(int argc, char **argv)
{
  char *endptr, *verbosity_str;
  NODE *node;

  if ( (argc < 2) ||
       (strcoll(argv[1], "-h") == 0 ||
	strcoll(argv[1], "--help") == 0 ||
	strcoll(argv[1], "-?") == 0) )
    usage(EXIT_USAGE);

  verbosity_str = argv[1];
  verbosity = strtol(verbosity_str, &endptr, 10);

  /* Check for various possible errors */
  if ((errno == ERANGE && (verbosity == LONG_MAX || verbosity == LONG_MIN))
      || (errno != 0 && verbosity == 0)) {
    perror("strtol");
    exit(EXIT_BADMODE);
  }

  if (endptr == verbosity_str) {
    fprintf(stderr, "No digits for verbosity were found in '%s'.\n", verbosity_str);
    usage(EXIT_BADMODE);
  }

  init_hash();

  if (argc > 2)
    {
      unsigned int i;
      for (i = 2; i < argc; i++)
        (void) spe_mult(string_to_value(argv[i]), node);
    }
  else
    {
      char buffer[64];
      printf("Note: the verbosity level set to %d.\n", verbosity);
      while (1) {
	  printf("Enter a positive number (or Ctrl-d to exit): ");
	  if (scanf("%63s", buffer) == 1)
	    spe_mult(string_to_value(buffer), node);
	  else
	    break;
      };
    }

  return EXIT_OK;
}
