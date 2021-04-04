import epics as epics
import numpy as np
import time as time
import datetime

HXR_PCAV_PV0 = 'SIOC:UNDH:PT01:0:TIME0'     # EGU in ps
HXR_PCAV_PV1 = 'SIOC:UNDH:PT01:0:TIME1'
SXR_PCAV_PV0 = 'SIOC:UNDS:PT01:0:TIME0'
SXR_PCAV_PV1 = 'SIOC:UNDS:PT01:0:TIME1'
XPP_LAS_TT_PV = 'LAS:FS11:VIT:FS_TGT_TIME'  # EGU in ns

pcav_avg_n  = 20    # n sample moving average
time_err_th = 10    # pcav err threshold in fs
time_err_ary = np.zeros((pcav_avg_n)) 
time_err_prev = 0
motr_step_cntr = 0  # counter for how many time the phase "motor" has moved in unit of time_err_th
motr_step_diff_mag = 0 
motr_step_diff_dir = 0 
cntr = 0

PCAV0_setpoint = epics.caget(SXR_PCAV_PV0)
PCAV1_setpoint = epics.caget(SXR_PCAV_PV1)

print('Controller running')
while True:
    print('//////////////////////////////////////////////////////////////////')
    print('Counter val: ' + str(cntr))
    PCAV0_Val_tmp = epics.caget(SXR_PCAV_PV0)
    time_err = np.around((PCAV0_setpoint - PCAV0_Val_tmp), decimals=6)
    time_err_delta = time_err - time_err_prev
    if cntr == 0:
        time_err_ary = np.array(time_err)
    elif (cntr >= pcav_avg_n):
        if np.abs(time_err_delta) < (0.100):
            time_err_ary = np.delete(time_err_ary, 0)
            time_err_ary = np.append(time_err_ary, time_err)
    else:
        time_err_ary = np.append(time_err_ary, time_err)
    time_err_mean = np.mean(time_err_ary)
    time_err_mean_fs = np.around(np.multiply(time_err_mean, 1000), 3)
    pm_step = np.trunc(np.true_divide(time_err_mean_fs, time_err_th))
    if pm_step != motr_step_cntr:
        print('moving TT')
        motr_step_diff = pm_step - motr_step_cntr
        motr_step_diff_mag = np.abs(motr_step_diff)
        motr_step_diff_dir = np.sign(motr_step_diff)
        print('current_tt_val = epics.caget(XPP_LAS_TT_PV)')
        current_tt_val = epics.caget(XPP_LAS_TT_PV)
        pm_val = np.multiply(pm_step, time_err_th)
        new_tt_val = current_tt_val + np.true_divide(pm_val, 1e6)
        print('epics.caput(XPP_LAS_TT_PV, new_tt_val)')
        motr_step_cntr = pm_step
        print('move time by: ' + str(pm_val))
        print('pm delta: ' + str(motr_step_diff))
    print('Time err delta: ' + str(np.around(time_err_delta, 3)) + 'ps')
    print('motor steps: ' + str(pm_step))
    print('current pm cntr: ' + str(motr_step_cntr))
    print(str(pcav_avg_n) + ' sample moving average error: ' + str(time_err_mean_fs) + 'fs')
    print('Time err array: ')
    print(time_err_ary)
    time_err_prev = time_err
    cntr = cntr + 1
    time.sleep(1)