# A GNU C Makefile
.PHONY: all clean mult-spe86

all: mult-spe86


# Add COPTS -DPRUNE to prune the tree.
# Add COPTS -DNCALLS to get the number of get_node() and try() calls.

COPTS=-DPRUNE -ggdb

#: V. Lefèvre's implementation of My Software: Practice & Experience Paper
mult-spe86: main.c
	gcc $(COPTS) $< -o $@


#: Sample run of Multiplication code on 51
example: mult-spe86
	./$< 1 102

clean:
	[ -e mult-spe86 ] && rm mult-spe86 || true
