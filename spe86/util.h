#ifndef SPE_MULT_UTIL_H
#define SPE_MULT_UTIL_H

#include "spe_mult.h"
extern int errexit(const char* msg, int exit_code);
extern char *format_binary_value(VALUE n);
extern void print_cost(const char *prefix, VALUE n, COST cost);

#endif /* SPE_MULT_UTIL_H */


/*
 * Local variables:
 *  c-file-style: "gnu"
 *  tab-width: 8
 *  indent-tabs-mode: nil
 * End:
 */
