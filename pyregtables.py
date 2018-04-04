# Copyright 2018, JIAFENG CHEN

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


from statsmodels.iolib.summary2 import summary_col
import re

def regression_table(regs, notes=None):
    """
    Create a pandas.DataFrame object summarizing a series of regressions
    Inputs
    -----
    regs: a list of statsmodels.regression.linear_model.RegressionResults
        objects, one for each column of the regression table

    notes: optional, a dict of additional rows to the table. Each key (string) is
        the name of a row, and each associated value (list of string) is the content

    Returns:
    -----
    t : a pandas.DataFrame of a regression table
    """
    d = {'$N$' : lambda x : '{0:d}'.format(int(x.nobs)),
         '$R^2$' : lambda x : '{:.2f}'.format(x.rsquared)}
    t = summary_col(regs, stars=True, info_dict=d).tables[0].copy()
    if notes:
        for k, v in notes.items():
            t.loc[k] = v
    return t


def as_latex_regtable(table, table_opt='tb',
                      column_names=None, caption=None,
                      label=None, covariate_names=None, notes='',
                      filename=None):
    """
    Convert a suitably formatted pandas.DataFrame to LaTeX. Requires booktabs,
    threeparttable packages in LaTeX.

    Inputs:
    -----
    table: a pandas.DataFrame
    table_opt: string, optional arguments passed to \begin{table} in LaTeX
    column_names: optional string list, change the name of the columns
    caption: string, optional argument passed to \caption in LaTeX
    label: string, optional argument passed to \label in LaTeX, if caption is
        specified and label is not, then label is caption joined by underscores
    covariate_names: a (string, string) dict where keys are covariate names in table
        and values are their proper string representations
    notes: additional notes to appear under the table
    filename: output .tex file directory; does not output file if unspecified. Will
        _overwrite_ existing file

    Returns:
    -----
    output: string
    """

    table = table.copy()
    col_format = 'l{}'.format('c' * (len(table.columns)))
    def formatter(x):
        x = re.sub('\*+', lambda s: '\\textsuperscript{{{}}}'.format(s[0]), x)
        if '$' not in x:
            x = re.sub(r'[-+]?[0-9]*\.?[0-9]+', lambda s: '${}$'.format(s[0]), x)
        return re.sub('_', ' ', x)
    if column_names:
        table.columns = column_names
    else:
        table.columns = map(formatter, (table.columns))

    if covariate_names:
        table.index = [covariate_names[s] if s in covariate_names
                       else s for s in table.index]
    else:
        table.index = map(formatter, (table.index))
    string = table.to_latex(column_format=col_format, escape=False,
                          formatters=[formatter] * len(table.columns))
    row = ''.join(['& ({})'.format(i) for i in range(1, len(table.columns) + 1)]) \
          + '\\\\\\' + '\n\\midrule'

    string = re.sub(r'\\midrule', row, string)

    if not caption:
        caption = 'caption here'
    if not label:
        label = '_'.join(map(lambda s: re.sub(r'\W+','',s),
                             caption.lower().split()))

    output = r'''
\begin{table}[%s]
\caption{%s}
\label{tab:%s}
\centering
\vspace{1em}
\begin{threeparttable}
%s
\begin{tablenotes}
\footnotesize
\item \textsuperscript{*}$p<.1$,
\textsuperscript{**}$p<.05$,
\textsuperscript{***}$p<.01$. %s
\end{tablenotes}
\end{threeparttable}

\end{table}
''' % (table_opt, caption, label, string, notes)
    if filename:
        with open(filename, 'w') as f:
            f.write(output)

    return output
