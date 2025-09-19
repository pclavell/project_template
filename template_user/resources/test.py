from pathlib import Path
import re
import os
import sys
import pandas as pd

script_path = Path.cwd()
user_dir = re.sub(r"/(metadata|processing|analysis)/.*$", "", str(script_path))
sys.path.append(user_dir)

from resources.utils import *

print(Path(__file__).resolve().parent)
os.chdir(Path(__file__).resolve().parent)