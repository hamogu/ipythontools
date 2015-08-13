import os
from distutils.core import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "ipythontools",
    version = "0.0.1",
    author = "Hans Moritz Gunther",
    author_email = "",
    description = ("ipynb to latex converter"),
    keywords = "ipython latex notebok",
    url = "https://github.com/douglase/ipythontools",
    packages=['ipythontools'],
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities"  ],
)
