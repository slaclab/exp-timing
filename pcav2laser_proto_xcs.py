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

HXR_PCAV_PV0 = 'SIOC:UNDH:PT01:0:TIME0'
HXR_PCAV_PV1 = 'SIOC:UNDH:PT01:0:TIME1'


SXR_PCAV_PV0 = 'SIOC:UNDS:PT01:0:TIME0'
SXR_PCAV_PV1 = 'SIOC:UNDS:PT01:0:TIME1'

HXR_CAST_PS_PV_W = 'LAS:UND:MMS:02'
HXR_CAST_PS_PV_R = 'LAS:UND:MMS:02.RBV'

XCS_LAS_TT_PV = 'LAS:FS4:VIT:FS_TGT_TIME'  # EGU in ns
XCS_LAS_TTOffset_PV = 'LAS:FS4:VIT:FS_TGT_TIME_OFFSET' 
# XCS_LAS_TT_PV = 'LAS:FS4:VIT:FS_TGT_TIME'  # EGU in ns

PCAV2TT_Gain = -1000  # PCAV reads in pico second, TT is in nano
pause_time = 1    # Let's give some time for the system to react
Cntl_gain  = 1     # feed forward gain

Cntl_setpt  = epics.caget(HXR_PCAV_PV0)  # Latch in the value before starting the feedback, this will be value we correct to
Cntl_output = 0
pcav_avg_n  = 5    # Taking 5 data samples to average and throw out outliers

# let's get the current value of the laser phase shifter
XCS_TT_init_Val = epics.caget(XCS_LAS_TT_PV)
Cntl_output = XCS_TT_init_Val   # once the script runs, that value is the setpoint
XCS_prev = XCS_TT_init_Val

# Read CAST value as reference
CAST_setpoint = epics.caget(HXR_CAST_PS_PV_R)
PCAV0_setpoint = epics.caget(HXR_PCAV_PV0)
PCAV1_setpoint = epics.caget(HXR_PCAV_PV1)

time_err_ary = np.zeros((pcav_avg_n,2)) 

cntr = 0

print('Controller running')

while True:
    print('Counter val: ' + str(cntr))
    PCAV0_Val_tmp = epics.caget(HXR_PCAV_PV0)
    time_err = np.around((PCAV0_setpoint - PCAV0_Val_tmp), decimals=6)
    if cntr == 0:
        time_err_ary = np.array(time_err)
    elif (cntr >= pcav_avg_n):
        time_err_ary = np.delete(time_err_ary, 0)
        time_err_ary = np.append(time_err_ary, time_err)
    else:
        time_err_ary = np.append(time_err_ary, time_err)
    time_err_mean = np.mean(time_err_ary)   
    XCS_TT = epics.caget(XCS_LAS_TT_PV)
    cntl_err = np.true_divide(time_err_mean, PCAV2TT_Gain)
    cntl_output = XCS_TT_init_Val + cntl_err
    epics.caput(XCS_LAS_TT_PV, cntl_output)
    XCS_Rb = epics.caget(XCS_LAS_TT_PV)
    XCS_diff = XCS_Rb - XCS_TT_init_Val
    XCS_diff = np.multiply(XCS_diff, 1000)
    XCS_fb_diff = np.multiply((XCS_Rb - XCS_TT), 1000)
    print('TMO TT: ' + str(XCS_TT) + 'ns') 
    print('HXR PCAV reading:' + str(PCAV0_Val_tmp) + ' ps')
    print('Time err array: ')
    print(time_err_ary)
    print('Time err:' + str(time_err) + ' ps')    
    print('TMO new TT: ' + str(XCS_Rb) + ' ns')    
    print('TMO diff init: ' + str(XCS_diff) + ' ps')    
    print('TMO feedback diff: ' + str(XCS_fb_diff) + ' ps')
    XCS_prev = XCS_Rb
    cntr = cntr + 1
    now = datetime.datetime.now()
    print(now.strftime('%Y-%m-%d-%H-%M-%S'))
    print('=============================================')        
    time.sleep(2)      

# epics.caput(XCS_LAS_TT_PV, XCS_TT_init_Val)

# Sawtooth test
# cntr = 0
# print('starting saw tooth')
# for i in range(1,6):
#     print(cntr)
#     epics.caput(XCS_LAS_TTOffset_PV, Cntl_output)
#     for j in range(1,100):
#         Cntl_output = XCS_TTOffset_init_Val + (np.true_divide(j, ps_scale))
#         epics.caput(XCS_LAS_TTOffset_PV, Cntl_output)
#         print(i*j)
#         cntr = cntr + 1
#         time.sleep(0.5)

# epics.caput(XCS_LAS_TTOffset_PV, XCS_TTOffset_init_Val)
