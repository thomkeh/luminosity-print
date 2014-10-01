#!/usr/bin/python
"""hpmor-convert.py converts chapters to different formats using
jinja2 templates.

Chapters are converted from markdown to pdf (using latex).

hpmor-convert takes the name of the format to build as the first
command line argument.
ex:
    python hpmor-convert.py markdown
"""
import os.path
import os
import re
import glob
import argparse
import jinja2
from subprocess import call

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
ROOT_DIR = os.path.relpath(os.path.split(SCRIPT_DIR)[0])
DUMP_DIR = os.path.join(ROOT_DIR, 'html-dump')
MARKDOWN_DIR = os.path.join(ROOT_DIR, 'markdown')
LATEX_DIR = os.path.join(ROOT_DIR, 'latex')
PDF_DIR = os.path.join(ROOT_DIR, 'pdf')
TEMPLATE_DIR = os.path.join(ROOT_DIR, 'templates')
BUILD_DIR = os.path.join(ROOT_DIR, '.build')
LATEX_SUBS = (
    (re.compile(r'\\'), r'\\textbackslash'),
    (re.compile(r'([{}_#%&$])'), r'\\\1'),
    (re.compile(r'~'), r'\~{}'),
    (re.compile(r'\^'), r'\^{}'),
    (re.compile(r'"'), r"''"),
    (re.compile(r'\.\.\.+'), r'\\ldots'),
)

def escape_tex(value):
    """Jinja2 latex escaping.
    """
    newval = value
    for pattern, replacement in LATEX_SUBS:
        newval = pattern.sub(replacement, newval)
    return newval

def pdf(out_name, style_class, font_size=12, paper_size='a5paper',
        double_sided=True, start_chapter=1, end_chapter=None):
    """Builds a pdf version using latex.

    LaTeX templates are rendered with jinja2 and saved to 'build/latex',
    which should already contain any other required latex files (besides
    the chapters, which are in 'latex').

    pdf output files are saved to the 'pdf' directory.

    ARGS:
        style_class (str): name of the latex class to typeset the book with
            ex: 'hpotter'
        out_name (str): name of output pdf file
        font_size (int): the font font size
        paper_size (string): latex paper size to use
        double_sided (bool): whether or not the book should be double sided
        start_chapter (int): the chapter to start with
        end_chapter (int): the chapter to end with. None means use highest
            chapter.
    """
    if double_sided is True:
        paper_sides = 'twoside'
    else:
        paper_sides = 'oneside'
    template_dir = os.path.join(TEMPLATE_DIR, 'latex')
    texenv = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir))
    texenv.block_start_string = '((*'
    texenv.block_end_string = '*))'
    texenv.variable_start_string = '((('
    texenv.variable_end_string = ')))'
    texenv.comment_start_string = '((='
    texenv.comment_end_string = '=))'
    texenv.filters['escape_tex'] = escape_tex

    template = texenv.get_template('hpmor.tex')
    rendered_template = os.path.join(BUILD_DIR,
                                     os.extsep.join([out_name, 'tex']))
    chapters = glob.glob(os.path.join(LATEX_DIR, '*{}tex'.format(os.extsep)))
    chapters = [os.path.split(ch)[1] for ch in chapters]
    chapters = sorted(chapters)
    if end_chapter is None:
        end_chapter = len(chapters)
    chapters = chapters[start_chapter-1:end_chapter]
    print 'rendering latex template'
    with open(rendered_template, 'w') as f:
        f.write(template.render(style_class=style_class,
                font_size=str(font_size), paper_size=paper_size,
                paper_sides=paper_sides, chapters=chapters))
    # compile the to pdf with xelatex
    pdf_filename = os.path.join(BUILD_DIR, os.extsep.join([out_name, 'pdf']))
    env = os.environ.copy();
    env['TEXINPUTS'] = template_dir+':'+os.path.join(template_dir, style_class)+':'
    command = ['xelatex',
        '--include-directory={}'.format(template_dir),
        '--output-directory={}'.format(BUILD_DIR),
        '--include-directory={}'.format(os.path.join(template_dir, style_class)),
    rendered_template]
    # xelatex is run twice to ensure correct table of contents
    for _ in range(2):
        print ' '.join(command)
        call(command, env=env)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert hpmor to different formats')
    parser.add_argument('--format', help='format to convert to')
    parser.add_argument('--style-class', help='latex style to use (pdf only)')
    parser.add_argument('-o', '--out-name', help='base name of output file')
    parser.add_argument('--font-size', help='font size', type=int, default=12)
    parser.add_argument('--double-sided', action='store_true',
                        help='make pdf double sided')
    parser.add_argument('--paper-size', help='latex paper type (pdf only)')
    parser.add_argument('--start-chapter', help='chapter to start at',
                        type=int, default=1)
    parser.add_argument('--end-chapter', help='chapter to end at', type=int,
                        default=None)
    args = parser.parse_args()
    if args.format == 'pdf':
        pdf(args.out_name, args.style_class, font_size=args.font_size,
            paper_size=args.paper_size, double_sided=args.double_sided,
            start_chapter=args.start_chapter, end_chapter=args.end_chapter)
