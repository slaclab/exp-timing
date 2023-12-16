#####################################################################
# Filename: pcav2cast.py
# Author: Chengcheng Xu (charliex@slac.stanford.edu)
# Date: 03/07/2021
#####################################################################
# This script will take the phase cavity value and put throw 
# an exponential feedback controller, then output its value to the 
# phase shifter in the cable stabilizer system
# NOTE: This is a band-aid, code is probably breaking many rules

import epics as epics
import numpy as np
import time as time
# from matplotlib import pyplot as plt

HXR_PCAV_PV0 = 'SIOC:UNDH:PT01:0:TIME0'
HXR_PCAV_PV1 = 'SIOC:UNDH:PT01:0:TIME1'
HXR_CAST_PS_PV_W = 'LAS:UND:MMS:02'
HXR_CAST_PS_PV_R = 'LAS:UND:MMS:02.RBV'
HXR_CAST2PCAV_Gain = 1.1283 # the slow from plotting cast phase shifter to value read from PCAV

pause_time = 2          # Let's give some time for the system to react
Cntl_gain = 0.1   # Feed back loop gain
#We are doing an exponential fb loop, where the output = output[-1] + (-gain * error)
Cntl_output = 0
Cntl_setpt  = epics.caget(HXR_PCAV_PV0)  # Latch in the value before starting the feedback, this will be value we correct to
pcav_avg_n  = 5    # Taking 5 data samples to average and throw out outliers

# let's get the current value of the phase shifter
HXR_CAST_PS_init_Val = epics.caget(HXR_CAST_PS_PV_R)
HXR_CAST_PS_target = HXR_CAST_PS_init_Val
Cntl_output = HXR_CAST_PS_target   # once the script runs, that value is the setpoint

time_err_ary = np.zeros((pcav_avg_n,))

cntr = 0
fb_itr = 30
asd = HXR_CAST_PS_target

print('Controller running')

while True:
    for h in range(0,pcav_avg_n):
        HXR_PCAV_Val_tmp = epics.caget(HXR_PCAV_PV0)
        time_err = np.around((Cntl_setpt - HXR_PCAV_Val_tmp), decimals=6)
        time_err_ary[h] = time_err
        time.sleep(0.1)
    time_err_ary_sort = np.sort(time_err_ary)
    time_err_ary_sort1 = time_err_ary_sort[1:-1]
    time_err_avg = np.mean(time_err_ary_sort1)    
    print('average error')
    print(time_err_avg)
    cntl_temp = np.true_divide(time_err_avg, HXR_CAST2PCAV_Gain)
    cntl_delta = np.multiply(Cntl_gain, cntl_temp)
    Cntl_output = Cntl_output + cntl_delta
    print('feedback value')
    print(Cntl_output)
    print('feedback delta')
    print(cntl_delta)
    epics.caput(HXR_CAST_PS_PV_W, Cntl_output)
    cntr = cntr + 1
    print('=============================================')        
    time.sleep(pause_time)    

# epics.caput(HXR_CAST_PS_PV_W, HXR_CAST_PS_init_Val)

