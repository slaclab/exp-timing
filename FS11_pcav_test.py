# pcavatm2las_alpha.py
# script looks at the FEH CAST phase shifter value also the ATM value
# and apply the mirror value to the FS11 drift correction PV 

import epics as epics
import numpy as np
import time as time
import datetime

# source /reg/g/pcds/engineering_tools/xpp/scripts/pcds_conda
pause_time = 0.1
FS11_DC_sw_PV  = 'LAS:FS11:VIT:TT_DRIFT_ENABLE'  # Put 0 for disable, put 1 for enable
FS11_DC_val_PV = 'LAS:FS11:VIT:matlab:04'        # Drift correct value in ns
FS11_ATM_PV  = 'XPP:TIMETOOL:TTALL'        # Waveform PV for reading ATM
HXR_PCAV_PV0 = 'SIOC:UNDH:PT01:0:TIME0'     # EGU in ps
HXR_PCAV_PV1 = 'SIOC:UNDH:PT01:0:TIME1'
HXR_CAST_PS_PV_W = 'LAS:UND:MMS:02'         # EGU in ps
HXR_CAST_PS_PV_R = 'LAS:UND:MMS:02.RBV'
SXR_PCAV_PV0 = 'SIOC:UNDS:PT01:0:TIME0'
SXR_PCAV_PV1 = 'SIOC:UNDS:PT01:0:TIME1'
SXR_CAST_PS_PV_W = 'LAS:UND:MMS:01'         # EGU in ps
SXR_CAST_PS_PV_R = 'LAS:UND:MMS:01.RBV'
XPP_LAS_TT_PV = 'LAS:FS11:VIT:FS_TGT_TIME'  # EGU in ns

# PCAV/CAST feed forward variables 
FS11_DC_val = 0
cast_avg_n  = 20    # n sample moving average
cast_acc    = 0
cast_acc_ns = 0
cast_tot_acc  = 0
time_err_th = 50    # pcav err threshold in fs
time_err_ary = 0 
time_err_prev = epics.caget(HXR_CAST_PS_PV_R)
motr_step_cntr = 0  # counter for how many time the phase "motor" has moved in unit of time_err_th
motr_step_diff_mag = 0 
motr_step_diff_dir = 0 
cntr = 0
mv_cntr = 0

# ATM Feedback variables
atm_avg_n = cast_avg_n
atm_val_ary = np.zeros(cast_avg_n)
ttamp_th = 0.05
ipm2_th = 3000
ttfwhm_hi = 130
ttfwhm_lo = 70
ATM_wf_val = epics.caget(FS11_ATM_PV)
ATM_pos = ATM_wf_val[0]
ATM_val = ATM_wf_val[1]
ATM_amp = ATM_wf_val[2]
ATM_nxt_amp = ATM_wf_val[3]
ATM_ref_amp = ATM_wf_val[4]
ATM_fwhm = ATM_wf_val[5]
atm_pm_step = 0
atm_prev = ATM_val
atm_t_cntr = 0
tt_good_cntr = 0
tt_bad_cntr = 0

print('Controller running')
while True:
    # Getting ATM reading determine if the ATM reading is good
    atm_wf_tmp = epics.caget(FS11_ATM_PV)
    atm_pos = atm_wf_tmp[0]
    atm_val = atm_wf_tmp[1]
    atm_amp = atm_wf_tmp[2]
    atm_nxt_amp = atm_wf_tmp[3]
    atm_ref_amp = atm_wf_tmp[4]
    atm_fwhm = atm_wf_tmp[5]
    # atm_t_err_delta = atm_val - atm_prev
    # atm_err_d_fs = np.around(np.multiply(atm_t_err_delta, 1000), 3)

    if (atm_amp > ttamp_th)and(atm_nxt_amp > ipm2_th)and(atm_fwhm < ttfwhm_hi)and(atm_fwhm > ttfwhm_lo)and(atm_val != atm_val_ary[-1,]):
        tt_good_cntr += 1
        if (tt_good_cntr > 200) and (atm_t_cntr%(3000*pause_time) == 0) :
            cast_ff_en = 1
            tt_bad_cntr = 0
            atm_t_cntr = 0
    else:
        tt_bad_cntr += 1
        if (tt_good_cntr > 200) and (atm_t_cntr%(3000*pause_time) == 0) :
            cast_ff_en = 0
            tt_good_cntr = 0
            atm_t_cntr = 0
    if (tt_good_cntr != 0) or (tt_bad_cntr != 0):
        atm_t_cntr += 1

    # PCAV/CAST delta change of feedforward
    cast_val_tmp = epics.caget(HXR_CAST_PS_PV_R)
    if (cntr%(pause_time*50) == 0):
        time_err_delta = cast_val_tmp - time_err_prev
        time_err_d_fs = np.around(np.multiply(time_err_delta, 1000), 3)
        cast_tot_acc = cast_tot_acc + time_err_d_fs
        time_err_prev = cast_val_tmp
        if cast_ff_en:
            cast_acc = cast_acc + time_err_d_fs
        else:
            cast_acc = 
    if cast_acc>time_err_th or cast_acc<time_err_th:
        print('Move to compensate')
        cast_acc_ns = -np.true_divide(cast_acc, 1e6)
        FS11_DC_val = epics.caget(FS11_DC_val_PV)
        FS11_DC_val = FS11_DC_val + cast_acc_ns
        epics.caput(FS11_DC_val_PV, FS11_DC_val)
        mv_cntr = mv_cntr + 1
        cast_acc = 0

    time_err_d_fs = np.around(np.multiply(time_err_delta, 1000), 3)      

    if (cntr%(pause_time*100) == 0):
        print('//////////////////////////////////////////////////////////////////')
        print('Counter val: ' + str(cntr))        
        print('cast shifter value: '  + str(cast_val_tmp)  + ' ps')
        print('Shifter delta err:  '  + str(time_err_d_fs) + ' fs')
        print('Shifter threshold:  '  + str(time_err_th)   + ' fs')
        print('Total CAST acc: ' + str(cast_tot_acc) + ' fs')
        print('CAST err acc: ' + str(cast_acc_ns) + ' ns')
        print('CAST err acc: ' + str(cast_acc) + ' fs')
        print('FS11 DC: ' + str(FS11_DC_val) + ' ns')
        print('Moved cntr: ' + str(mv_cntr))
        # print('!!!!!!!!!!Last Good ATM reading!!!!!!!!!!')
        # print('ATM val: ' + str(atm_val) + 'ps')
        # print('ATM delta err: ' + str(atm_err_d_fs) + 'fs')

    cntr += 1

    time.sleep(pause_time)