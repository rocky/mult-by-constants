# Compatibility for us old-timers.

# Note: This makefile include remake-style target comments.
# These comments before the targets start with #:
# remake --tasks to shows the targets and the comments

GIT2CL ?= git2cl
PYTHON ?= python3
PYTHON3 ?= python3
RM      ?= rm
LINT    = flake8

PHONY=all check clean pytest type-check distclean lint flake8 test rmChangeLog clean_pyc

#: Default target - same as "check"
all: check

#: Run all tests - type check and pytest
check: type-check check-python check-spe86

#: Same thing as "make check"
test: check

#: Run Python (pytest) tests
check-python pytest:
	py.test pytest

#: Run Software -- Practice and Experience C code tests
check-spe86:
	cd spe86 && make check

#: Static type checking
type-check:
	mypy mult_by_const

#: Run all tests with verbose debug-output
check-debugged:
	DEBUG=1 py.test -s pytest

#: Clean up temporary files and .pyc files
clean: clean_pyc
	$(PYTHON) ./setup.py $@
	find . -name __pycache__ -exec rm -fr {} || true \;
	(cd test && $(MAKE) clean)
	(cd test_unit && $(MAKE) clean)

#: Create source (tarball) and wheel distribution
dist: clean
	$(PYTHON) ./setup.py sdist bdist_wheel

#: Remove .pyc files
clean_pyc:
	( cd xdis && $(RM) -f *.pyc */*.pyc )

#: Create source tarball
sdist:
	$(PYTHON) ./setup.py sdist


#: Style check. Set env var LINT to pyflakes, flake, or flake8
lint: flake8

#: Lint program
flake8:
	$(LINT) xdis

#: Create binary egg distribution
bdist_egg:
	$(PYTHON) ./setup.py bdist_egg


#: Create binary wheel distribution
bdist_wheel:
	$(PYTHON) ./setup.py bdist_wheel

# It is too much work to figure out how to add a new command to distutils
# to do the following. I'm sure distutils will someday get there.
DISTCLEAN_FILES = build dist *.pyc

#: Remove ALL derived files
distclean: clean
	-rm -fvr $(DISTCLEAN_FILES) || true
	-find . -name \*.pyc -exec rm -v {} \;
	-find . -name \*.egg-info -exec rm -vr {} \;

#: Install package locally
verbose-install:
	$(PYTHON) ./setup.py install

#: Install package locally without the verbiage
install:
	$(PYTHON) ./setup.py install >/dev/null

rmChangeLog:
	rm ChangeLog || true

#: Create a ChangeLog from git via git log and git2cl
ChangeLog: rmChangeLog
	git log --pretty --numstat --summary | $(GIT2CL) >$@

.PHONY: $(PHONY)
