# A GNU C Makefile
.PHONY: all clean mult-spe86 test-mult check

all: mult-spe86 check

# Add COPTS -DNCALLS to get the number of alpha_beta_search_node() and try() calls.

COPTS ?= -ggdb

#: V. Lefèvre's implementation of My Software: Practice & Experience Paper
mult-spe86:  util.o spe_mult.o main.o
	gcc $(COPTS) util.o spe_mult.o main.o -o $@

.c.o:
	gcc $(COPTS) $< -c -o $@

util.c: util.h
main.c: spe_mult.h
spe_mult.c: spe_mult.h
test_mult.c: spe_mult.h

#: Build the main command-line utility
test-mult: util.o spe_mult.o test_mult.o
	gcc $(COPTS) util.o spe_mult.o test_mult.o -o $@

#: Run tests
check: test-mult
	./test-mult

#: Same thing as "make check"
test: check

#: Sample run of Multiplication code on 51
example: mult-spe86
	./$< 1 102

BINS=mult-spe86 test-mult
FILES=$(BINS) *.o

#: Wipe clean compiled and derived files, leaving just the source
clean:
	for file in $(FILES); do  [ -e $$file ] && rm $$file || true; done
