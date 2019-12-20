



########  Imports ########

import nbformat as nbf
from argparse import ArgumentParser, FileType
from re import match
from io import StringIO


'''
nb = nbf.v4.new_notebook(metadata={'language': 'python'})


text = """\
# My first automatic Jupyter Notebook
This is an auto-generated notebook."""

code = """\
%pylab inline
hist(normal(size=2000), bins=50);"""

nb['cells'] = [nbf.v4.new_markdown_cell(text),
               nbf.v4.new_code_cell(code) ]



nbf.write(nb, 'test.ipynb')
'''



if __name__ == '__main__':
    parser = ArgumentParser(description='This program converts python scripts into v4 jupyter notebooks')
    parser.add_argument('file', type=FileType(mode='r'), help='Python file to be converted')
    parser.add_argument('--output', '-o', type=FileType(mode='w'), default=None, help='Filepath for the jupyter notebook that will be generated. By default will be out.ipynb')

    parsed_args = parser.parse_args()
    input_file = parsed_args.file
    output_file = parsed_args.output
    if output_file is None:
        output_file = open('out.ipynb', 'w')


    cells = []
    buffer = StringIO()
    source_lines = []

    # Read input file line by line
    for line in input_file:
        if line.startswith('#') or not line.rstrip('\n'):
            cells.append(nbf.v4.new_code_cell(''.join(source_lines).strip('\n')))

        result = match('^[#]+([\w ]+)[#]+', line)
        if result:
            text = '## ' + result.group(1).strip(' ')
            cells.append(nbf.v4.new_markdown_cell(text))
            continue

        result = match('^#([\w ]+)', line)
        if result:
            text = result.group(1).strip(' ')
            cells.append(nbf.v4.new_markdown_cell(text))
            continue
        source_lines.append(line)


    if source_lines:
        cells.append(nbf.v4.new_code_cell(source_lines))

    for cell in cells:
        print(cell)
