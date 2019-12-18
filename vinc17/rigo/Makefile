# A GNU C Makefile
.PHONY: all clean rigo example

COPTS ?= -ggdb
BINS = rigo

all: rigo

#: Raphaël Rigo's implementation (using GMP) of V. Lefèvre's latest algorithm.
rigo: rigo.c
	gcc $(COPTS) $< -lgmp -o $@

#: Sample run of rigo code on 51
example: rigo
	./rigo 1 51

FILES=$(BINS) *.o

#: Wipe clean compiled and derived files, leaving just the source
clean:
	for file in $(FILES); do  [ -e $$file ] && rm $$file || true; done
