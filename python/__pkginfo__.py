"""mult_by_const packaging information"""

# To the extent possible we make this file look more like a
# configuration file rather than code like setup.py. I find putting
# configuration stuff in the middle of a function call in setup.py,
# which for example requires commas in between parameters, is a little
# less elegant than having it here with reduced code, albeit there
# still is some room for improvement.

# Things that change more often go here.
copyright = """
Copyright (C) 2019 Rocky Bernstein <rb@dustyfeet.com>.
"""

classifiers = ["Programming Language :: Python :: 3.8"]

# The rest in alphabetic order
author = "Rocky Bernstein"
author_email = "rb@dustyfeet.com"
entry_points = {"console_scripts": ["mult-by-const=mult_by_const.main:main"]}
ftp_url = None

#  click: for command-line options
#  ruamel: For YAML output
#  matplot, numpy, and pandas for plotting. This could be in a separate package!
install_requires = ["click", "ruamel.yaml"]

license = "GPL-3"
modname = "mult_by_const"
py_modules = None
# setup_requires     = ['pytest-runner']
# scripts = ["bin/pydisasm.py"]
short_desc = "Python cross-version byte-code disassembler and marshal routines"
tests_require = ["pytest==3.2.0", "mypy"]
web = "https://github.com/rocky/python-mult_by_const/"

# tracebacks in zip files are funky and not debuggable
zip_safe = True

import os.path


def get_srcdir():
    filename = os.path.normcase(os.path.dirname(os.path.abspath(__file__)))
    return os.path.realpath(filename)


srcdir = get_srcdir()


def read(*rnames):
    return open(os.path.join(srcdir, *rnames)).read()


# Get info from files; set: long_description and VERSION
long_description = read("README.md") + "\n"
exec(read("mult_by_const/version.py"))
