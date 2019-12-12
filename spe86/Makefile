# A GNU C Makefile
.PHONY: all clean mult-spe86 test-mult check

all: mult-spe86 check

# Add COPTS -DNCALLS to get the number of get_node() and try() calls.

COPTS ?= -ggdb

#: V. Lefèvre's implementation of My Software: Practice & Experience Paper
mult-spe86: main.o spe_mult.o
	gcc $(COPTS) spe_mult.o main.o -o $@

.c.o:
	gcc $(COPTS) $< -c -o $@

main.c: spe_mult.h
spe_mult.c: spe_mult.h
test_mult.c: spe_mult.h

#: Build the main command-line utility
test-mult: test_mult.o spe_mult.o
	gcc $(COPTS) spe_mult.o test_mult.o -o $@

#: Run tests
check: test-mult
	./test-mult

#: Sample run of Multiplication code on 51
example: mult-spe86
	./$< 1 102

BINS=mult-spe86 test-mult
FILES=$(BINS) *.o

#: Wipe clean compiled and derived files, leaving just the source
clean:
	for file in $(FILES); do  [ -e $$file ] && rm $$file || true; done
