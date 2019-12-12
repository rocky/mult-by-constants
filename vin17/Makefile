# A GNU C Makefile
.PHONY: clean all rigo

COPTS ?= -ggdb
BINS = dagsearch dsjoin gendags maxc readcode readcost sumcosts

#: Make all targets
all: $(BINS) rigo

dagsearch: dagsearch.c
	gcc $(COPTS) $< -o $@

dsjoin: dsjoin.c
	gcc $(COPTS) $< -o $@

gendags: gendags.c
	gcc $(COPTS) $< -o $@

maxc: maxc.c
	gcc $(COPTS) $< -o $@

qtree: qtree.c
	gcc $(COPTS) $< -o $@

readcode: readcode.c
	gcc $(COPTS) $< -o $@

rigo:
	$(MAKE) -C rigo all

readcost: readcost.c
	gcc $(COPTS) $< -o $@

sumcosts: sumcosts.c
	gcc $(COPTS) $< -o $@

FILES=$(BINS) *.o

#: Wipe clean compiled and derived files, leaving just the source
clean:
	for file in $(FILES); do  [ -e $$file ] && rm $$file || true; done
