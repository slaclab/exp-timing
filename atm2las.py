#####################################################################
# Filename: atm2las.py
# Author: Chengcheng Xu (charliex@slac.stanford.edu)
# Date: 06/15/2021
#####################################################################
import epics as epics
import sys
import numpy as np
import time as time
import datetime
import yaml

class PVS():
    def __init__(self,hn):
        filename = ("ATM_" + str(hutch) + "_FB.yml")
        with open(filename, 'r') as yaml_file:
            yaml_content = yaml.load(yaml_file, Loader=yaml.SafeLoader)
        print("Key: Value")
        for key, value in yaml_content.items():
            print(str(key)+": "+str(value))

        DC_sw_PV = yaml_content.get("DC_sw_PV")
        DC_val_PV = yaml_content.get("DC_val_PV")

def drift_comp_fb(hutch='NULL'):
    P = PVS(hutch)
    print(P.DC_sw_PV)
    DC_val = epics.caget(P.DC_val_PV)
    print(str(DC_val))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        drift_comp_fb()  # null input will prompt
    else:
        drift_comp_fb(sys.argv[1])