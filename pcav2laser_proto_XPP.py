#####################################################################
# Filename: pcav2laser_proto_XPP.py
# Author: Chengcheng Xu (charliex@slac.stanford.edu)
# Date: 03/13/2021
#####################################################################
# When the script starts, the pcav value at that moment will be reference
# any change in the pcav value then, will be reflected on the FS11 Target time
# the script will write to the target time at 0.5Hz
# femto.py/whatever the high level application for the laser needs to be running
# NOTE: This is a band-aid, code is probably breaking many rules
# To ensure right python env sourced
# bash
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

XPP_LAS_TT_PV = 'LAS:FS11:VIT:FS_TGT_TIME'  # EGU in ns
# XPP_LAS_TTOffset_PV = 'LAS:FS11:VIT:FS_TGT_TIME_OFFSET'
# XCS_LAS_TT_PV = 'LAS:FS4:VIT:FS_TGT_TIME'  # EGU in ns

PCAV_err_bar = 1
PCAV2TT_Gain = 1000  # PCAV reads in pico second, TT is in nano
pause_time = 2    # Let's give some time for the system to react
Cntl_gain  = 1     # feed forward gain
Cntl_output = 0
pcav_avg_n  = 5    # 5 sample moving average
time_err_ary = np.zeros((pcav_avg_n,2))
time_err_prev = 0
cntr = 0

# let's get the current value of the laser phase shifter
XPP_TT_init_Val = epics.caget(XPP_LAS_TT_PV)
Cntl_output = XPP_TT_init_Val   # once the script runs, that value is the setpoint
XPP_prev = XPP_TT_init_Val

# Read CAST/PCAV values
CAST_setpoint = epics.caget(HXR_CAST_PS_PV_R)
PCAV0_setpoint = epics.caget(HXR_PCAV_PV0)
PCAV1_setpoint = epics.caget(HXR_PCAV_PV1)

print('Controller running')
while True:
    print('Counter val: ' + str(cntr))
    PCAV0_Val_tmp = epics.caget(HXR_PCAV_PV0)
    time_err = np.round((PCAV0_setpoint - PCAV0_Val_tmp), decimals=6)
    if cntr == 0:
        time_err_ary = np.array(time_err)
    elif (cntr >= pcav_avg_n):
        time_err_ary = np.delete(time_err_ary, 0)
        time_err_ary = np.append(time_err_ary, time_err)
    else:
        time_err_ary = np.append(time_err_ary, time_err)

    time_err_mean = np.mean(time_err_ary)
    time_err_delta = time_err_mean - time_err_prev
    cntl_err = np.true_divide(time_err_delta, PCAV2TT_Gain)
    cntl_output = XPP_TT + cntl_err
    epics.caput(XPP_LAS_TT_PV, cntl_output)
    XPP_Rb = epics.caget(XPP_LAS_TT_PV)
    XPP_diff = XPP_Rb - XPP_TT_init_Val
    XPP_diff = np.multiply(XPP_diff, 1000)
    XPP_fb_diff = np.multiply((XPP_Rb - XPP_TT), 1000)
    print('TMO TT: ' + str(XPP_TT) + 'ns')
    print('PCAV reading:' + str(PCAV0_Val_tmp) + ' ps')
    print('Time err array: ')
    print(time_err_ary)
    print('Time err:' + str(time_err) + ' ps')
    print('TMO new TT: ' + str(XPP_Rb) + ' ns')
    print('TMO diff init: ' + str(XPP_diff) + ' ps')
    print('TMO feedback diff: ' + str(XPP_fb_diff) + ' ps')
    print('PCAV err delta: ' + str(time_err_delta) + ' ps')
    XPP_prev = XPP_Rb
    time_err_prev = time_err_mean
    cntr = cntr + 1
    now = datetime.datetime.now()
    print(now.strftime('%Y-%m-%d-%H-%M-%S'))
    print('=============================================')
    time.sleep(pause_time)

# epics.caput(XPP_LAS_TT_PV, XPP_TT_init_Val)

# Sawtooth test
# cntr = 0
# print('starting saw tooth')
# for i in range(1,6):
#     print(cntr)
#     epics.caput(TMO_LAS_TTOffset_PV, Cntl_output)
#     for j in range(1,100):
#         Cntl_output = TMO_TTOffset_init_Val + (np.true_divide(j, ps_scale))
#         epics.caput(TMO_LAS_TTOffset_PV, Cntl_output)
#         print(i*j)
#         cntr = cntr + 1
#         time.sleep(0.5)

# epics.caput(TMO_LAS_TTOffset_PV, TMO_TTOffset_init_Val)

                                           