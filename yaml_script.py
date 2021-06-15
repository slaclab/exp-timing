import epics as epics
import sys
import numpy as np
import time as time
import datetime
import yaml

def drift_comp_fb(hutch='NULL'):
    filename = ("ATM_" + str(hutch) + "_FB.yml")
    with open(filename, 'r') as yaml_file:
        yaml_content = yaml.load(yaml_file, Loader=yaml.SafeLoader)

    print("Key: Value")
    for key, value in yaml_content.items():
        print(str(key)+": "+str(value))

    print(yaml_content)
    print(yaml_content.get("DC_sw_PV"))
    DC_sw_PV = yaml_content.get("DC_sw_PV")
    DC_val_PV = yaml_content.get("DC_val_PV")
    print(DC_sw_PV)
    DC_val = epics.caget(DC_val_PV)
    print(str(DC_val))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        drift_comp_fb()  # null input will prompt
    else:
        drift_comp_fb(sys.argv[1])