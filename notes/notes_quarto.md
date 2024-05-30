
## How Quarto Works

According to their [website](https://quarto.org/docs/get-started/hello/vscode.html) quarto goes through markdown format before reaching pandoc and then pdf. Ergo, as a minimum, anything possible in markdown is possible in the final document.

### Cell Options

Similar to R Markdown, cell options are specified globally and on a cell-by-cell basis. In Jupyter Notebooks they are given as YAML with a `#|` prefix. Best practice is to seperate figures and tables into their own cells and define their options explicitly. Common options include:

`#|fig-cap:` top level caption for a figure, prefixed with "Figure X" where X is an index ordered by appearance of figures.
`#|fig-subcap:` secondary level caption for the figure.
`#|tbl-cap:` top level caption for a table, prefixed with "Table Y" where Y is an index ordered by appearance of tables.
`#|tbl-subcap:` secondary level caption for the table.
`#|fig-label: <label>` A cross-reference target to be used inline by `@<label>` where `<label>` is user defined.
`#|tbl-label: <label>` A cross-reference target to be used inline by `@<label>` where `<label>` is user defined.

### Rendering the pdf

`quarto render <name_of_notebook>.ipynb --to pdf`

### Cross references

Cross referencing can be achieved by the following syntax:

inline:

`@<fig-label>`

in the figure cell:

`#|label: <fig-label>`

## Format Settings

An A4 page measures 210 mm x 297 mm (8.27 in x 11.7 in) [wikipedia](https://en.wikipedia.org/wiki/ISO_216#A_series).

## Examples

The following are examples of how to use Quarto for scientific reporting:

https://hbiostat.org/rflow/rformat.html
