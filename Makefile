# Compatibility for us old-timers.

# Note: This makefile include remake-style target comments.
# These comments before the targets start with #:
# remake --tasks to shows the targets and the comments

GIT2CL ?= git2cl
PYTHON ?= python3
PYTHON3 ?= python3
RM      ?= rm

PHONY=all check clean pytest type-check distclean rmChangeLog clean_pyc

#: Default target - same as "check"
all: check

#: Run all tests - type check and pytest
check: type-check check-python check-spe86

#: Same thing as "make check"
test: check

#: Run Python (pytest) tests
check-python pytest:
	cd python && py.test pytest

#: Run Software -- Practice and Experience C code tests
check-spe86:
	cd spe86 && make check

#: Static type checking
type-check:
	cd python && mypy mult_by_const

#: Run all tests with verbose debug-output
check-debugged:
	cd python && DEBUG=1 py.test -s pytest

#: Clean up temporary files and .pyc files
clean: clean_pyc
	cd python
	$(PYTHON) ./setup.py $@
	find . -name __pycache__ -exec rm -fr {} || true \;
	(cd test && $(MAKE) clean)
	(cd test_unit && $(MAKE) clean)

#: Remove .pyc files
clean_pyc:
	( cd xdis && $(RM) -f *.pyc */*.pyc )

# It is too much work to figure out how to add a new command to distutils
# to do the following. I'm sure distutils will someday get there.
DISTCLEAN_FILES = build dist *.pyc

#: Remove ALL derived files
distclean: clean
	-rm -fvr $(DISTCLEAN_FILES) || true
	-find . -name \*.pyc -exec rm -v {} \;
	-find . -name \*.egg-info -exec rm -vr {} \;

rmChangeLog:
	rm ChangeLog || true

#: Create a ChangeLog from git via git log and git2cl
ChangeLog: rmChangeLog
	git log --pretty --numstat --summary | $(GIT2CL) >$@

.PHONY: $(PHONY)
