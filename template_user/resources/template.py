# HEADER ------------------------------------------------------------------------
from pyprojroot.here import here
import sys
sys.path.append(str(here()))
from resources.utils import *
config = load_config() # to refer to files in config use config$
paths = load_paths() # to refer to data, figs, metadata, ref, scratch use resulting paths$
#--------------------------------------------------------------------------------