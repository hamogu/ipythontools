ipythontools
============
This module installs two command line scripts:

- ``jupyter2article`` extracts some content (raw cells, markdown cells, code output) from a
  Jupyter/IPython notebook and pastes it into a new file. It also converst markdown headings
  to proper LaTeX chapter, section, subsetion etc. and inserts appropriate labels.
  This converter is not intended to replace the nbconvert from the IPython
  project. Instead, it serves one very specific purpose:
  Turn a notebook into a LaTeX file that I can submit to the journal.

- ``jupyterspellcheck`` spell checks markdown and raw cells in a notebook.

Note that scipts and procedures have been renamed to "jupyter", but the name of the package
and its directory structure still reflect that fact that Jupyter notebooks started out as part of the IPython project.


The converter
-------------
When I first encountered the IPython notebook, I thought this was a solution
looking for a problem. However, I have since been converted!
The tipping point for me was this: I want to version control my papers and
I always had multiple directories for analysis code, plotting code, LaTeX files,
plot scripts and figures and tables. That's just so unwieldy.
Also, I found it cumbersome to email figures to individual collaborators all
the time.
The Notebook can hold all this information in one place and I can just provide
my co-authors with a link to the github repository once and they have access
to the latest version all the time. Even if they do not use python, they can
still see the all the current figures using nbviewer.ipython.org

Now all papers I work on a are written in an IPython notebook. So, the final
step to do is to convert the notebook to the LaTeX file I can submit to a
journal. That's what this simple converter code does.

This converter is not intended to replace the nbconvert from the IPython
project. Instead, it serves one very specific purpose:
Turn a notebook into a LaTeX file that I can submit to the journal.

**How to use it**

*As a script*

Installing this module places a script in your path, so you can do:

  > jupyter2article myanalysis.ipynb myanalysis.tex

In this case it's run with my set of design choices (see below).

*As a Python module*

Import into python and make a ``NotebookConverter`` object:

    from ipynb2article import NotebookConverter
    converter = NotebookConverter

Then, customize how each type of cell is converted by changing the converter:

    converter.cellconverters['code'] = NotebookConverter.IgnoreConverter()

Finally, call:

    converter.convert(infile, outfile, ...)

This method allows you to use only part of a notebook file (ignore to first n
cells or ignore everything until a cell has a specific string value, e.g.
"The paper starts here"). Also, it allows you to provide a text file that will be
pasted before or after the converted notebook (you can put the '\usepackage' and
similar stuff in those files so they don't clutter your notebook).
However, I do not use this option any longer, because that means I would have
multiple input files. If I put all those LaTeX headers into the notebook as
well, I only have a single file.

Design
======

The code is written around these design ideas:

- Be able to ignore certain parts of the notebook (e.g. introductory comments
  in the first few cells).
- Convert headings to section / subsection etc.
  I generally level 2 such as "## Heading" for section, "### Heading" for subsections etc.
- Copy text in "markdown" and "raw text" cells. To simplify, I just write
  real LaTeX code in those cells. All equations will be rendered correctly
  in the notebook file for me and my co-authors to see.
  When I want to highlight something I type LaTeX "\emph{}" or "\textbf{}",
  not the markdown equivalents. That looks not as nice in the notebook, but
  makes live so much easier.
  Also, markdown does not recognize "\cite", "\ref" and "\label". Again, it
  looks not as nice in markdown, but
  (1) I only need to know LaTeX and (2) it works flawlessly when converted.
- No figure conversion. Instead, in the notebook itself I issue:

    fig.savefig('/path/to/my/article/XXX.eps')

  because ApJ requires me to submit figures as separate files anyway.
- Just type figure captions into markdown cells.
- No conversion of code cells. Who wants code in an ApJ paper?
- Occasionally, I want to have the output of a computation (e.g. a table
  written with astropy in LaTeX format) in the article. Keep it simple.
  Output of all code cells that have a certain comment string (I use
  "# output->LaTeX") is copied verbatim to the LaTeX file.
- Work with the python standard library only. No external dependencies.


To implement this I wrote a converter for each cell type.
``LiteralSourceConverter`` just takes the literal string value (it also adds
a line break at the end of the  cell) and puts it into the LaTeX file
(use for markdown and raw text cells),
``MarkedCodeOutputConverter`` checks if a code cell has a specific string in
it and if so, it copies the output of this cell, and ``LatexHeadingConverter``
looks for the level of the heading and turns that into LaTeX (it also adds
as label like "\label{sect:title}").


The spellchecker
----------------
Spell check the markdown text in IPython notebooks

As much as I love the IPython notebook, there is one big drawback (at least in
my installation). When I type into a cell in the browser (I use firefox) there
is no automatic spell checking of the input. Sure, the notebook has syntax
highlighting for code cells in python, but I want to do my entire paper
writing in the notebook and for me that means that a spell checker for cells
with markdown, headings or raw text is absolutely essential.
On the other hand, I cannot just run e.g. ``ispell`` on the ipynb file, since
most of its contents is actually code and not plain English.
So, I wanted to write a spell checker, that parses the ipynb file and spell checks
only the markdown, heading and raw text input cells.

Oh, one more thing: Because I type a lot of raw LaTeX in my notebooks (see my
other post on ``ipynb2article.py``) as opposed to real markdown that resembles
English much better I define a custom filter function that
makes sure that strings which look like LaTeX commands will not be spell checked
(since very few LaTeX command are valid English words so that would give a lot of
apparent typos).
More complicated filters that avoid spell checking within equations or
commands like ``\label{XXX}`` or ``\cite{}`` are possible (they would be called
a ``chunker`` in ``pyenchant``). Check the `github repository <https://github.com/hamogu/ipythontools>`_
for this code if you want to see if I have an improved version.


*How to use this script*:

Close down the notebook you want to spell check in IPython, then simply type on
the command line:

    > jupyterspellcheck filein.ipynb fileout.ipynb

Open the new file in IPython, run all cells again and keep working.

`filein` and `fileout` can be the same filename (in this case the old file will get
overwritten with the spelling corrected version), but I recommend to keep a copy
just in case something gets screwed up.
