#####################################################################
# Filename: LXT_sawtooth.py
# Author: Chengcheng Xu (charliex@slac.stanford.edu)
# Date: 04/17/2022
#####################################################################

import epics as epics
import numpy as np
import time as time
import datetime

pause_time = 1
TGT_PV = "LAS:FS14:VIT:FS_TGT_TIME"
CTR_PV = "LAS:FS14:VIT:FS_CTR_TIME"
scan_range = 40    # Scan range in ns, always goes +/- range/2 
scan_step = 0.5   # Scan reslution in ns
scan_loop = 5
current_TGT = epics.caget(TGT_PV)
start_TGT = current_TGT - (scan_range/2)
time.sleep(0.5)

i = 0
for j in range(0, scan_loop, 1):
    while (i < scan_range):
        desire_TGT = start_TGT + (i * scan_step)
        print("setting TGT to: ", str(desire_TGT))
        epics.caput(TGT_PV, desire_TGT)
        time.sleep(0.1)
        current_CTR = epics.caget(CTR_PV)
        print("CTR time is: ", str(current_CTR))
        i = i + scan_step
        print(i)
        time.sleep(pause_time)  
        
              
epics.caput(TGT_PV, current_TGT)