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

# Append resources dir to path
p = os.path.dirname(os.getcwd())+'/resources/'
sys.path.append(p)

from utils import *

# Call function from utils.py
save_mn5_config()
