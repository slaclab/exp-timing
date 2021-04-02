import epics as epics
import numpy as np
import time as time
import datetime

HXR_PCAV_PV0 = 'SIOC:UNDH:PT01:0:TIME0'
HXR_PCAV_PV1 = 'SIOC:UNDH:PT01:0:TIME1'

pcav_avg_n  = 20    # 5 sample moving average
time_err_th = 10    # pcav err threshold in fs
time_err_ary = np.zeros((pcav_avg_n))
time_err_prev = 0
cntr = 0

PCAV0_setpoint = epics.caget(HXR_PCAV_PV0)
PCAV1_setpoint = epics.caget(HXR_PCAV_PV1)

print('Controller running')
while True:
    print('Counter val: ' + str(cntr))
    PCAV0_Val_tmp = epics.caget(HXR_PCAV_PV0)
    time_err = np.around((PCAV0_setpoint - PCAV0_Val_tmp), decimals=6)
    time_err_delta = time_err - time_err_prev
    if cntr == 0:
        time_err_ary = np.array(time_err)
    elif (cntr >= pcav_avg_n):
        if time_err < (0.100):
            time_err_ary = np.delete(time_err_ary, 0)
            time_err_ary = np.append(time_err_ary, time_err)
    else:
        time_err_ary = np.append(time_err_ary, time_err)
    time_err_mean = np.mean(time_err_ary)
    time_err_mean_fs = np.around(np.multiply(time_err_mean, 1000), 3)
    pm_step = np.trunc(np.true_divide(time_err_mean_fs, time_err_th))
    print('motor steps: ' + str(pm_step))
    print(str(pcav_avg_n) + ' sample moving average error: ' + str(time_err_mean_fs) + 'fs')
    print('Time err array: ')
    print(time_err_ary)
    time_err_prev = time_err
    cntr = cntr + 1
    time.sleep(1)