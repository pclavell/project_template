################################## README BEFORE USAGE ##################################

# USE THIS SCRIPT TO CREATE THE config.yml with the full marenostrum5 paths

#     Usage: python3 save_mn5_config.py

                                    #   /\_/\
                                    #  ( o.o )
                                    #   > ^ <
                                    #  /     \
                                    # (       )
                                    #  \__ __/
                                    #   || ||

############ --------------------------------------------------------------- ############

import os
import sys
from pathlib import Path
from marko import Markdown
from marko.md_renderer import MarkdownRenderer
from marko.inline import RawText, Link, CodeSpan
from marko.block import FencedCode, CodeBlock

import re

# Append resources dir to path
p = os.path.dirname(os.getcwd())+'/resources/'
sys.path.append(p)

from utils import *

# add links to all relevant unlinked files and directories in READMEs
# anchored "normal" pattern
_pat_normal = re.compile(
    r'^([\W\s]*?)'              # leading non-word/space
    r'((?:\.\./)*\.?[\w./-]+?)' # the path-ish thing (lazy)
    r'([^\w./-]*)$'             # trailing punctuation
)

# fallback: find candidate path-like substrings
_candidate_re = re.compile(r'(?:\.\./)*\.?[\w./-]+')

_PUNCT_TO_TRIM = set('.,:;)]}\'"')

def _trim_trailing_punct(core: str):
    trailing = []
    while core and core[-1] in _PUNCT_TO_TRIM:
        trailing.append(core[-1])
        core = core[:-1]
    return core, ''.join(reversed(trailing))

def extract_parts(s: str):
    """
    Extract (leading, core_path, trailing) from a token string.
    Returns None if no path-like core is found.
    """
    m = _pat_normal.match(s)
    if m:
        p1, core, p2 = m.groups()
        core, extra = _trim_trailing_punct(core)
        p2 = extra + p2
        return p1, core, p2

    candidates = list(_candidate_re.finditer(s))
    if not candidates:
        return None

    best = max(candidates, key=lambda mm: mm.end() - mm.start())
    core = best.group(0)
    start, end = best.start(), best.end()
    core_trimmed, extra = _trim_trailing_punct(core)
    leading = s[:start]
    trailing = extra + s[end:]
    return leading, core_trimmed, trailing


def format_link(word):
    """Format link in markdown depending on if it's a directory or a file."""
    if Path(word).is_dir():
        return f'[{word}]({word})'
    else:
        return f'[`{word}`]({word})'


# ---- main transformer ----

def link_files(node, files):
    """
    Walk a Markdown AST node and replace unlinked filenames/dirs
    with markdown links to those paths.

    Parameters
    ----------
    node : mdit_py_plugins node
        AST node to transform.
    files : set of str
        Set of known file/directory paths to link.

    Returns
    -------
    node : mdit_py_plugins node
        Node with links inserted where appropriate.
    """

    # skip entire code blocks
    if isinstance(node, (FencedCode, CodeBlock)):
        return node

    # skip inline code spans
    if isinstance(node, CodeSpan):
        return node

    # skip existing links
    if isinstance(node, Link):
        return node

    if isinstance(node, RawText):
        tokens = re.findall(r'\S+|\s+', node.children)
        new_nodes = []
        for tok in tokens:
            if tok.isspace():
                new_nodes.append(RawText(tok))
                continue
            parts = extract_parts(tok)
            if parts:
                p1, core, p2 = parts
                if core in files:
                    replaced = format_link(core)
                    new_nodes.append(RawText(p1 + replaced + p2))
                    continue

            # nothing to replace
            new_nodes.append(RawText(tok))

        return new_nodes

    # recurse into children
    if hasattr(node, "children"):
        new_children = []
        for child in node.children:
            replaced = link_files(child, files)
            if isinstance(replaced, list):
                new_children.extend(replaced)
            else:
                new_children.append(replaced)
        node.children = new_children

    return node

# get all git files that are md
cmd = 'git ls-files'
files = run_cmd(cmd).splitlines()
dirs = [str(Path(f).parent) for f in files]
md_files = [f for f in list(set(files)|set(dirs)) if f != '.' and f.endswith('.md')]

# get all git files
cmd = 'git ls-files'
files = run_cmd(cmd).splitlines()
dirs = [str(Path(f).parent) for f in files]
files = [f for f in list(set(files)|set(dirs)) if f != '.']
dirs = [f'{f}/' for f in files if Path(f).is_dir()] # add the trailing / version of dirs
files += dirs

# loop through all md files to edit
# md_files = ['README_test.md']
# md_files = ['TEST_revised.md']
# md_files = ['analysis/README.md']
for md_file in md_files:
    rel_files = []
    for file in files:

        # compute relative path from md_file's directory
        rel_path = os.path.relpath(file, Path(md_file).parent)
        rel_files.append(rel_path)

    md = Markdown()
    with open(md_file, 'r') as f:
        content = f.read()
        doc = md.parse(content)

    doc = link_files(doc, rel_files)

    md = Markdown(renderer=MarkdownRenderer)
    doc = md.render(doc)

    # write to new md file
    with open(f'{md_file}', 'w') as ofile:
        ofile.write(doc)
