#####################################################################
# Filename: pcav2laser_proto.py
# Author: Chengcheng Xu (charliex@slac.stanford.edu)
# Date: 03/07/2021
#####################################################################
# This script will take the phase cavity value and put throw 
# an exponential feedback controller, then output its value to the 
# phase shifter in the cable stabilizer system
# NOTE: This is a band-aid, code is probably breaking many rules
# To ensure right python env sourced
# source /reg/g/pcds/engineering_tools/xpp/scripts/pcds_conda
import epics as epics
import numpy as np
import time as time
import datetime

# from matplotlib import pyplot as plt
PCAV2TT_Gain = -1000  # PCAV reads in pico second, TT is in nano

HXR_PCAV_PV0 = 'SIOC:UNDH:PT01:0:TIME0'
HXR_PCAV_PV1 = 'SIOC:UNDH:PT01:0:TIME1'


SXR_PCAV_PV0 = 'SIOC:UNDS:PT01:0:TIME0'
SXR_PCAV_PV1 = 'SIOC:UNDS:PT01:0:TIME1'
TMO_LAS_TT_PV = 'LAS:FS14:VIT:FS_TGT_TIME'  # EGU in ns
XCS_LAS_TT_PV = 'LAS:FS4:VIT:FS_TGT_TIME'  # EGU in ns


pause_time = 5    # Let's give some time for the system to react
Cntl_gain = 0.1   # Feed back loop gain
#We are doing an exponential fb loop, where the output = output[-1] + (-gain * error)
Cntl_setpt  = epics.caget(HXR_PCAV_PV0)  # Latch in the value before starting the feedback, this will be value we correct to
Cntl_output = 0
pcav_avg_n  = 5    # Taking 5 data samples to average and throw out outliers

# let's get the current value of the phase shifter
TMO_TT_init_Val = epics.caget(XCS_LAS_TT_PV)
Cntl_output = TMO_TT_init_Val   # once the script runs, that value is the setpoint

time_err_ary = np.zeros((pcav_avg_n,)) 

cntr = 0
time_err_avg_prev = 0

print('Controller running')

while True:
    print(cntr)
    for h in range(0,pcav_avg_n):
        HXR_PCAV_Val_tmp = epics.caget(HXR_PCAV_PV0)
        time_err = np.around((Cntl_setpt - HXR_PCAV_Val_tmp), decimals=6)
        time_err_ary[h] = time_err
        time.sleep(0.1)
    time_err_ary_sort = np.sort(time_err_ary)
    time_err_ary_sort1 = time_err_ary_sort[1:-1]
    time_err_avg = np.mean(time_err_ary_sort1)  
    
    if cntr == 0:
        time_err_diff = 0.01
    else:
        time_err_diff = time_err_avg_prev - time_err_avg  
    print('average error')
    print(time_err_avg)
    cntl_temp = np.true_divide(time_err_avg, PCAV2TT_Gain)
    cntl_delta = np.multiply(Cntl_gain, cntl_temp)
    print('previous error')
    print(time_err_avg_prev)
    print('Error diff')
    print(time_err_diff)
    if (time_err_diff == 0) or (time_err_diff >= 100):
        cntl_delta = 0
    Cntl_output = Cntl_output + cntl_delta
    print('feedback value')
    print(Cntl_output)
    print('feedback delta')
    print(cntl_delta)
    epics.caput(XCS_LAS_TT_PV, Cntl_output)
    time_err_avg_prev = time_err_avg
    cntr = cntr + 1
    now = datetime.datetime.now()
    print(now.strftime('%Y-%m-%d-%H-%M-%S'))
    print('=============================================')        
    time.sleep(pause_time)    

# epics.caput(HXR_CAST_PS_PV_W, TMO_TT_init_Val)