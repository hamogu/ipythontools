#! /data/guenther/anaconda/bin/python
'''Very simple converter from an IPython notebook to e.g. an ApJ or A&A article

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

How to use it
=============
As a script
-----------
You can use this file form the command line::

  > python ipynb2article.py myanalysis.ipynb myanalysis.tex

In this case it's run with my set of design choices (see below).

As a Python module
------------------
Import into python and make a ``NotebookConverter`` object::

    from ipynb2article import NotebookConverter
    converter = NotebookConverter

Then, customize how each type of cell is converted by changing the converter::

    converter.cellconverters['code'] = NotebookConverter.IgnoreConverter()

Finally, call::
    
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
  I generally use "Heading 2" for section, "Heading 3" for subsections etc.
  In the notebook, just press "Ctrl+m 2" to format a cell as "Heading 2"
  or select with the mouse from the drop-down menu.
- Copy text in "markdown" and "raw text" cells. To simplify, I just write
  real LaTeX code in those cells. All equations will be rendered correctly
  in the notebook file for me and my co-authors to see.
  When I want to highlight something I type LaTeX "\emph{}" or "\textbf{}",
  not the markdown equivalents. That looks not as nice in the notebook, but
  makes live so much easier.
  Also, markdown does not recognize "\cite", "\ref" and "\label". Again, it 
  looks not as nice in markdown, but 
  (1) I only need to know LaTeX and (2) it works flawlessly when converted.
- No figure conversion. Instead, in the notebook itself I issue::
    
    fig.savefig('/path/to/my/article/XXX.eps')

  because ApJ requires me to submit eps figures as separate files anyway.
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
'''
import json
import re

import sys
import getopt

def ismarkercell(cell, start):
    if 'source' in cell.keys():
        return cell['source'] == [start]
    elif 'input' in cell.keys():
        return cell['input'] == [start]
    else:
        raise ValueError('Type of cell not recognized.')

class IgnoreConverter(object):
    '''Use this converter for cell types that should be ignored'''
    def __call__(self, cell):
        return []

class LiteralSourceConverter(object):
    '''This converter return the literal ``source`` entry of a cell.'''
    def __call__(self, cell):
        text = cell['source']
        
        if len(text) > 0:
            text[-1] +='\n'
        else:
            return '\n'
        return text

class MarkedCodeOutputConverter(object):
    '''Add output of code cells that have a specific string in the code cell'''
    def __init__(self, marker):
        '''Add output of code cells that have a specific string in the code cell

        Parameters
        ----------
        marker : string
            Convert the output of a code cell if and only if one line in the
            code matches ``marker``.
            I often use ``marker='# output->LaTeX'`` to mark cells whose
            output I want.
        '''
        self.marker = marker
    def __call__(self, cell):
        text = []
        if (self.marker in cell['input']) or (self.marker+'\n' in cell['input']):
            for out in cell['outputs']:
                if 'text' in out:
                    text.extend(out['text'])
                    
        if len(text) > 0:
            text[-1] +='\n'
        return text

class LatexHeadingConverter(object):
    '''Convert headings in notebook to appropriate level in LaTeX'''
    def __init__(self, latexlevels=['chapter','section','subsection', 'subsubsection', 'paragraph', 'subparagraph']):
        '''Convert headings in notebook to appropriate level in LaTeX

        Parameters
        ----------
        latexlevels : list of 6 strings
            Latex equivalents for 'Heading 1', 'Heading 2' etc.
        '''
        self.latexlevels = latexlevels
    def __call__(self, cell):
        # Just to be careful for multi-line headings
        title = ''.join(cell['source']) 
        line1 = '\\{0}{{{1}}}\n'.format(self.latexlevels[cell['level']-1],
                                      title)
        cleantitle = re.sub(r'\W+', '', title)
        line2 = '\\label{{sect:{0}}}\n'.format(cleantitle.lower())
        return ['\n','\n', line1, line2, '\n']

class NotebookConverter(object):
    cellconverters = {
                      'code' : MarkedCodeOutputConverter('# output->LaTeX'),
                      'heading': LatexHeadingConverter(),
                      'markdown': LiteralSourceConverter(),
                      'raw': LiteralSourceConverter()
                      }

    def find_cell(self, cells, marker, skip = 0):
        '''return number of cell that's specified either by number of by content'''
        if isinstance(marker, basestring):
            for i, c in enumerate(cells):
                if ismarkercell(cells[i], marker):
                    return i + skip
            raise ValueError('cell {0} not found in notebook.')
        else:
            try:
                return int(marker)
            except:
                raise ValueError('Cells need to be specified with integer number or content string')


    def convert(self, infile, outfile, start=0, stop=100000000, file_before=None, file_after=None):
        '''Convert IPython notebook to LaTeX file

        Parameters
        ----------
        infile : string
            filename of IPython notebook
        outfile : string
            filename of Latex file to be written
        start : int or string
            If this is a number, skip that many cells starting from the top;
            if it is a string, skip cells until a cell has *exactly* the 
            content that ``start`` has.
        stop : int or string
            If this is a number, ignore anything after that cells
            (``stop=5`` means the fifth cell from the top, not the cell with number
            ``[5]`` in the ipython notebook)
            if it is a string, skip cells after the cell that has *exactly* the 
            content that ``stop`` has.
        file_before : string
        file_after: string
            String with filename. These files are copied above and below
            the content from the ipynb file. Use this e.g. for templates
            that contain the LaTeX header info that does not appear in the 
            notebook.
        '''
        with open(infile, 'r') as f:
            print 'Parsing ', infile
            ipynb = json.load(f)

        cells = ipynb['worksheets'][0]['cells']
        start = self.find_cell(cells, start, skip=1)
        stop = self.find_cell(cells, stop)
        if stop > len(cells):
            stop = len(cells)
        if start > stop:
            raise Exception('Start cell found after end cell')
        cells = cells[start:stop]
        
        with open(outfile, 'w') as out:
            print 'Writing ', outfile
            if file_before is not None:
                with open(file_before, 'r') as f:
                    for line in f:
                        try:
                            out.write(line)
                        except UnicodeEncodeError:
                            raise ValueError(line)
         
            for cell in cells:
                lines = self.cellconverters[cell['cell_type']](cell)
                for line_num,line in enumerate(lines):
                    try:
                        out.write(line)
                    except UnicodeEncodeError:
                        raise ValueError(line)
                    
            if file_after is not None:
                with open(file_after, 'r') as f:
                    for line in f:
                        try:
                            out.write(line)
                        except UnicodeEncodeError:
                            raise ValueError(line)
         
        
if __name__ == '__main__':
    converter = NotebookConverter()
    try:                                
        opts, args = getopt.getopt(sys.argv[1:], "h", ["help"])
    except getopt.GetoptError:           
        print converter.convert.__doc__                          
        sys.exit(2)

    for opt, arg in opts:           
        if opt in ("-h", "--help"): 
            print converter.convert.__doc__                     
            sys.exit()                  
    
    print args
    converter.convert(*args)

