import os
from setuptools import setup, find_packages

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "ipythontools",
    version = "0.1.0",
    author = "Hans Moritz Gunther",
    author_email = "moritz.guenther@gmx.de",
    description = ("Jupyer/IPython notebook to latex converter and spell checker"),
    keywords = "ipython latex notebok jupyter",
    url = "https://github.com/hamogu/ipythontools",
    packages = find_packages(),
    requires = ['pyenchant'],
    long_description=read('README.md'),
    license = 'MIT',
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Topic :: Text Processing :: Markup :: LaTeX"
        "Topic :: Utilities"  ],
    entry_points={
        'console_scripts': [
            'jupyter2article = ipythontools.jupiter2article:jupyter2article',
            'jupyterspellcheck = ipythontools.spellchecker:jupyterspellchecker',
            ]
        }
)
