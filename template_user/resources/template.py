# HEADER ------------------------------------------------------------------------
from pyprojroot.here import here
import sys
sys.path.append(str(here()))
from resources.utils import * # if the ModuleNotFound in mn5 it is probably because of the module you used. Use module load anaconda
config = load_config() # to refer to files in config use config$
paths = load_paths() # to refer to data, figs, metadata, ref, scratch use resulting paths$
#--------------------------------------------------------------------------------
