################################## README BEFORE USAGE ##################################

# This script adds the subfolders as bullet point links to the READMEs
# of analysis/ and processing/ if they don't already exist

#     Usage: python3 add_subfolders_to_readmes.py

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

# Append resources dir to path
p = os.path.dirname(os.getcwd())+'/resources/'
sys.path.append(p)

from utils import *

# Map directories to permanent subdirs to ignore
PERMANENT_DIRS = {
    'processing': ['rules', 'template_snakemake', '.ipynb_checkpoints'],
    'analysis': ['.ipynb_checkpoints']
}

# Map directories to README headers where bullets should go
README_HEADERS = {
    'processing': '## Subfolder descriptions',
    'analysis': '## Subfolder descriptions'  # adjust if different
}

all_missing_dirs = []

for d, perm_dirs in PERMANENT_DIRS.items():
    readme = f'{d}/README.md'

    # Find missing subdirs
    to_update = []
    for sub_d in Path(d).glob('*/'):
        stem_sub_d = sub_d.stem
        if stem_sub_d in perm_dirs or not sub_d.is_dir():
            continue
        fmt_sub_d = f'[{stem_sub_d}]'
        if any(fmt_sub_d in line for line in open(readme)):
            continue
        to_update.append(sub_d)

    # Add missing subdirs to README
    if to_update:
        m = load_resources()  # get repo URL, etc.
        header = README_HEADERS[d]

        with open(readme, 'r') as infile:
            lines = infile.readlines()

        output_lines = []
        inside_section = False
        inserted = False

        for i, line in enumerate(lines):
            output_lines.append(line)

            if header in line:
                inside_section = True
                continue

            if inside_section and line.startswith("## "):
                last_bullet_idx = max(
                    (i for i, line in enumerate(output_lines) if "* [" in line.strip()),
                    default=i-1
                )
                for j, sub_d in enumerate(to_update):
                    stem_sub_d = sub_d.stem
                    output_lines.insert(
                        last_bullet_idx + j + 1,
                        f"* [{stem_sub_d}]({stem_sub_d}/): # TODO!!\n"
                    )
                inside_section = False
                inserted = True

        if not inserted:
            for sub_d in to_update:
                stem_sub_d = sub_d.stem
                output_lines.append(f"* [{stem_sub_d}]({stem_sub_d}/): # TODO!!\n")

        with open(readme, 'w') as outfile:
            outfile.writelines(output_lines)

        print(f"Added README entries to {readme} for:")
        for sub_d in to_update:
            print(f"- {sub_d.stem}")
        all_missing_dirs.extend(to_update)
