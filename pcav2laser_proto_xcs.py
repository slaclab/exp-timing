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

HXR_CAST_PS_PV_W = 'LAS:UND:MMS:02'
HXR_CAST_PS_PV_R = 'LAS:UND:MMS:02.RBV'

TMO_LAS_TT_PV = 'LAS:FS14:VIT:FS_TGT_TIME'  # EGU in ns
TMO_LAS_TTOffset_PV = 'LAS:FS14:VIT:FS_TGT_TIME_OFFSET' 
# XCS_LAS_TT_PV = 'LAS:FS4:VIT:FS_TGT_TIME'  # EGU in ns


pause_time = 1    # Let's give some time for the system to react
Cntl_gain  = 1     # feed forward gain

Cntl_setpt  = epics.caget(HXR_PCAV_PV0)  # Latch in the value before starting the feedback, this will be value we correct to
Cntl_output = 0
pcav_avg_n  = 5    # Taking 5 data samples to average and throw out outliers

# let's get the current value of the phase shifter
TMO_TT_init_Val = epics.caget(TMO_LAS_TT_PV)
Cntl_output = TMO_TT_init_Val   # once the script runs, that value is the setpoint
TMO_prev = TMO_TT_init_Val

# TMO_TTOffset_init_Val = epics.caget(TMO_LAS_TTOffset_PV)
# Cntl_output = TMO_TTOffset_init_Val   # once the script runs, that value is the setpoint
# TMO_prev = TMO_TTOffset_init_Val
# ps_scale = 1000

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


# Read CAST value as reference
CAST_setpoint = epics.caget(HXR_CAST_PS_PV_R)
PCAV0_setpoint = epics.caget(HXR_PCAV_PV0)
PCAV1_setpoint = epics.caget(HXR_PCAV_PV1)

time_err_ary = np.zeros((pcav_avg_n,2)) 
time_err_ary_sort = np.zeros((pcav_avg_n,2)) 
time_err_ary_red = np.zeros((2,)) 

cntr = 0
time_err_avg_prev = 0

print('Controller running')

while True:
    PCAV0_Val_tmp = epics.caget(HXR_PCAV_PV0)
    time_err = np.around((PCAV0_setpoint - PCAV0_Val_tmp), decimals=6)
    print(time_err)
    if cntr == 0:
        time_err_ary = np.array(time_err)
    elif (cntr >= pcav_avg_n):
        time_err_ary = np.delete(time_err_ary, 0)
        time_err_ary = np.append(time_err_ary, time_err)
    else:
        time_err_ary = np.append(time_err_ary, time_err)
    time_err_mean = np.mean(time_err_ary)
    print(time_err_ary)
    print(cntr)
    print('TMO_TT: ' + str(TMO_Rb))    
    print('HXR PCAV reading:' + str(PCAV0_Val_tmp))
    print('Time err:' + str(time_err) + 'ps')
    cntl_err = np.true_divide(time_err_mean, PCAV2TT_Gain)
    cntl_output = TMO_TT_init_Val + cntl_err
    epics.caput(TMO_LAS_TT_PV, cntl_output)
    TMO_Rb = epics.caget(TMO_LAS_TT_PV)
    print('TMO_Rb: ' + str(TMO_Rb))
    TMO_diff = TMO_Rb - TMO_TT_init_Val
    TMO_diff = np.multiply(TMO_diff, 1000)
    print('TMO diff init: ' + str(TMO_diff) + 'ps')
    TMO_fb_diff = np.multiply((TMO_Rb - TMO_prev), 1000)
    print('TMO feedback diff: ' + str(TMO_fb_diff) + 'ps')
    TMO_prev = TMO_Rb
    cntr = cntr + 1
    now = datetime.datetime.now()
    print(now.strftime('%Y-%m-%d-%H-%M-%S'))
    print('=============================================')        
    time.sleep(2)      

# epics.caput(TMO_LAS_TT_PV, TMO_TT_init_Val)


    for h in range(0,pcav_avg_n):
        PCAV0_Val_tmp = epics.caget(HXR_PCAV_PV0)
        PCAV1_Val_tmp = epics.caget(HXR_PCAV_PV1)
        time_err0 = np.around((PCAV0_setpoint - PCAV0_Val_tmp), decimals=8)
        time_err1 = np.around((PCAV1_setpoint - PCAV1_Val_tmp), decimals=8)
        time_err_ary[h,0] = time_err0
        time_err_ary[h,1] = time_err1
        time.sleep(0.5)
    time_err_ary_sort[:,0] = np.sort(time_err_ary[:,0])
    time_err_ary_sort[:,1] = np.sort(time_err_ary[:,1])
    time_err_ary_red[0,] = np.mean(time_err_ary_sort[1:-1,0])
    time_err_ary_red[1,] = np.mean(time_err_ary_sort[1:-1,1])
    time_err_avg = np.mean(time_err_ary_red)  
    time_err_avg = time_err_ary_red[0,]  
    LAS_TT_val = epics.caget(TMO_LAS_TT_PV)
    PCAV0_Val_tmp = epics.caget(HXR_PCAV_PV0)
    time_err0 = np.around((PCAV0_setpoint - PCAV0_Val_tmp), decimals=8)    
    if cntr == 0:
        time_err_diff = 0.001
        # LAS_TT_pre_val = LAS_TT_val
        LAS_tt_diff = 0
        LAS_tt_adiff = time_err_avg
    else:
        time_err_diff = time_err_avg_prev - time_err_avg 
        LAS_tt_diff   = np.multiply((LAS_TT_pre_val - LAS_TT_val), 1000)
        LAS_tt_adiff  = np.multiply((TMO_TT_init_Val - LAS_TT_val), 1000)
    print('Average PCAV error: ' + str(time_err_avg) + ' ps')
    print('TT abs diff: ' + str(LAS_tt_adiff) + ' ps')
    cntl_temp = np.true_divide(time_err_avg, PCAV2TT_Gain)
    cntl_temp = np.true_divide(time_err0, PCAV2TT_Gain)
    cntl_delta = np.multiply(Cntl_gain, cntl_temp)
    print('Previous error: ' + str(time_err_avg_prev) + ' ps')
    print('PCAV error diff: ' + str(time_err_diff) + ' ps')
    print('TT error diff: ' + str(LAS_tt_diff) + ' ps')
    # if (time_err_diff == 0) or (time_err_diff >= 100):
    #     cntl_delta = 0
    Cntl_output = Cntl_output + cntl_delta
    print('TT value: ' + str(Cntl_output) + ' ns')
    epics.caput(TMO_LAS_TT_PV, Cntl_output)
    time_err_avg_prev = time_err_avg
    LAS_TT_pre_val = LAS_TT_val
    cntr = cntr + 1
    now = datetime.datetime.now()
    print(now.strftime('%Y-%m-%d-%H-%M-%S'))
    print('=============================================')        
    time.sleep(1)    


    print(cntr)
    TMO_Rb = epics.caget(TMO_LAS_TT_PV)
    print('TMO_TT: ' + str(TMO_Rb))    
    HXR_PCAV_Val_tmp = epics.caget(HXR_PCAV_PV0)
    HXR_CAST_Val = epics.caget(HXR_CAST_PS_PV_R)
    # print('HXR PCAV reading:' + str(HXR_PCAV_Val_tmp))
    print('HXR CAST reading:' + str(HXR_CAST_Val))
    time_err = CAST_setpoint - HXR_CAST_Val
    print('Time err:' + str(time_err) + 'ps')
    cntl_err = np.true_divide(time_err, PCAV2TT_Gain)
    cntl_output = TMO_TT_init_Val + cntl_err
    epics.caput(TMO_LAS_TT_PV, cntl_output)
    TMO_Rb = epics.caget(TMO_LAS_TT_PV)
    print('TMO_Rb: ' + str(TMO_Rb))
    TMO_diff = TMO_Rb - TMO_TT_init_Val
    TMO_diff = np.multiply(TMO_diff, 1000)
    print('TMO diff init: ' + str(TMO_diff) + 'ps')
    TMO_fb_diff = np.multiply((TMO_Rb - TMO_prev), 1000)
    print('TMO feedback diff: ' + str(TMO_fb_diff) + 'ps')
    TMO_prev = TMO_Rb
    cntr = cntr + 1
    now = datetime.datetime.now()
    print(now.strftime('%Y-%m-%d-%H-%M-%S'))
    print('=============================================')        
    time.sleep(1)   


# epics.caput(TMO_LAS_TT_PV, TMO_TT_init_Val)
# epics.caput(TMO_LAS_TT_PV, 5439.684289909387)
# 5439.684289909387