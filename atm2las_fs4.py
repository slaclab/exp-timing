#####################################################################
# Filename: atm2las_fs4.py
# Author: Chengcheng Xu (charliex@slac.stanford.edu)
# Date: 04/28/2021
#####################################################################

import epics as epics
import numpy as np
import time as time
import datetime

pause_time = 0.1
DC_sw_PV  = 'LAS:FS4:VIT:TT_DRIFT_ENABLE'  # Put 0 for disable, put 1 for enable
DC_val_PV = 'LAS:FS4:VIT:matlab:04'        # Drift correct value in ns
ATM_PV = 'XCS:TIMETOOL:TTALL'              # ATM waveform PV
TTC_PV = 'XCS:LAS:MMN:01'                  # ATM mech delay stage
IPM_PV = 'XCS:SB1:BMMON:SUM'               # intensity profile monitor PV
IPM_HI_PV = 'LAS:FS4:VIT:matlab:28.HIGH'
IPM_LO_PV = 'LAS:FS4:VIT:matlab:28.LOW'
TT_amp_PV = 'LAS:FS4:VIT:matlab:23'
TT_amp_HI_PV  = 'LAS:FS4:VIT:matlab:23.HIGH'
TT_amp_LO_PV  = 'LAS:FS4:VIT:matlab:23.LOW'
LAS_TT_PV = 'LAS:FS4:VIT:FS_TGT_TIME'      # EGU in ns
HXR_CAST_PS_PV_W = 'LAS:UND:MMS:02'        # EGU in ps
HXR_CAST_PS_PV_R = 'LAS:UND:MMS:02.RBV'
SXR_CAST_PS_PV_W = 'LAS:UND:MMS:01'        # EGU in ps
SXR_CAST_PS_PV_R = 'LAS:UND:MMS:01.RBV'
ATM_OFFSET_PV = 'LAS:UNDH:FLOAT:04'            # Notepad PV for ATM setpoint PV in ps

# ATM Feedback variables
atm_avg_n = 70
atm_val_ary = np.array([0])
ttfwhm_hi = 200
ttfwhm_lo = 100
ATM_wf_val = epics.caget(ATM_PV)
ATM_pos = ATM_wf_val[0]
ATM_val = ATM_wf_val[1]
ATM_amp = ATM_wf_val[2]
ATM_nxt_amp = ATM_wf_val[3]
ATM_ref_amp = ATM_wf_val[4]
ATM_fwhm = ATM_wf_val[5]
atm_err = 0
atm_ary_mean = 0
atm_ary_mean_fs = 0
atm_pm_step = 0
atm_prev = ATM_val
atm_t_cntr = 1
atm_stat = 0
tt_good_cntr = 0
tt_bad_cntr = 0
cast_ff_en = 0
cast_ff_cntr = 0

# PCAV/CAST feed forward variables 
DC_val = 0
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

print('Controller running')
while True:
    # Getting ATM & IPM reading determine if the ATM reading is good
    atm_wf_tmp = epics.caget(ATM_PV)
    atm_pos = atm_wf_tmp[0]
    atm_val = atm_wf_tmp[1]  # in ps
    atm_amp = atm_wf_tmp[2]
    atm_nxt_amp = atm_wf_tmp[3]
    atm_ref_amp = atm_wf_tmp[4]
    atm_fwhm = atm_wf_tmp[5]
    IPM_val  = epics.caget(IPM_PV)
    atm_offset  = epics.caget(ATM_OFFSET_PV)  # get setpoint in ps

    # Get limit threshold from EDM
    IPM_HI_val = epics.caget(IPM_HI_PV)
    IPM_LO_val = epics.caget(IPM_LO_PV)
    TT_amp_HI_val = epics.caget(TT_amp_HI_PV)
    TT_amp_LO_val = epics.caget(TT_amp_LO_PV)

    # Condition for good atm reading
    # 05/05 maybe fwhm threshold should be PVs too
    # if (atm_amp > TT_amp_LO_val)and(IPM_val > IPM_LO_val)and(atm_fwhm < ttfwhm_hi)and(atm_fwhm > ttfwhm_lo):
    if (atm_amp > TT_amp_LO_val)and(atm_fwhm < ttfwhm_hi)and(atm_fwhm > ttfwhm_lo):
        tt_good_cntr += 1
        tt_good = True
    else:
        tt_bad_cntr += 1
        tt_good = False
    
    # Determine if use ATM or PCAV as drift compensation
    if (tt_good_cntr > 100) and (atm_t_cntr%(3000*pause_time) == 0) :
        # print('good atm')
        atm_stat = 1
        tt_good_cntr = 0
        tt_bad_cntr = 0
        atm_t_cntr = 1
    elif (tt_bad_cntr > 100) and (atm_t_cntr%(3000*pause_time) == 0) :
        # print('bad atm')
        atm_stat = 0
        tt_good_cntr = 0
        tt_bad_cntr = 0
        atm_t_cntr = 1
    elif (atm_t_cntr%(3000*pause_time) == 0) :
        # print('resetting')
        atm_t_cntr = 1
        tt_good_cntr = 0
        tt_bad_cntr = 0

    if (tt_good_cntr != 0) or (tt_bad_cntr != 0):
        atm_t_cntr += 1    

    # Filling the running avg array
    if tt_good:            
        if cntr == 0 and tt_good:
            atm_val_ary = atm_val
        elif (atm_val_ary.size >= atm_avg_n) and tt_good:
            atm_val_ary = np.delete(atm_val_ary, 0)
            atm_val_ary = np.append(atm_val_ary,atm_val)
        else:
            if tt_good:
                atm_val_ary = np.append(atm_val_ary,atm_val)
        # average and convert to fs, ns
        atm_ary_mean  = np.mean(atm_val_ary)
        atm_ary_mean_fs = np.around(np.multiply(atm_ary_mean, 1000), 3)
        atm_ary_mean_ns = np.true_divide(atm_ary_mean, 1000)
        atm_err = atm_ary_mean + atm_offset
        atm_err_ns = np.true_divide(atm_err, 1000)

    if (cntr%(pause_time*200) == 0):
        # epics.caput(TT_amp_PV, atm_amp)  # Update EDM panel
        print('#################################')
        print('ATM array error: ' + str(atm_err) + 'ps')
        print('ATM array mean: ' + str(atm_ary_mean_fs) + 'fs')        
        print('ATM time: ' + str(atm_val))
        print('ATM amp: ' + str(atm_amp))
        print('ATM fwhm: ' + str(atm_fwhm))
        print('IPM val: ' + str(IPM_val))
        print('tt_good_cntr: ' + str(tt_good_cntr))
        print('tt_bad_cntr: ' + str(tt_bad_cntr))

    if (cntr%(pause_time*200) == 0):
        print('+++++++++++++++++++++++++++++++++++++')
        if atm_val_ary.size == atm_avg_n:
            print('array full')
            print(atm_val_ary)
            if np.absolute(atm_ary_mean_fs)>time_err_th:
                print('Move to compensate')
                print('ATM err ns average: ' + str(atm_err_ns))
                DC_val = epics.caget(DC_val_PV)
                DC_val = DC_val - atm_err_ns
                epics.caput(DC_val_PV, DC_val)
                print("move DC PV to: " + str(DC_val) + "ns")
                print('Clearning ATM array')
                atm_val_ary = np.array([0])
    
    if (cntr%(pause_time*1500) == 0):
        print('//////////////////////////////////////////////////////////////////')
        print('Counter val: ' + str(cntr))
        ts = time.strftime('%Y-%m-%d-%H:%M:%S', time.localtime())
        print(ts)
        if atm_stat:
            print('###############################')
            print('Good ATM reading')
            print('tt_good_cntr val: ' + str(tt_good_cntr))
            print('tt_bad_cntr val: ' + str(tt_bad_cntr))
            # print('atm_t_cntr: ' + str(atm_t_cntr))
            print('###############################')   
        else:
            print('##############################')
            print('Bad ATM readings')

            print('tt_good_cntr val: ' + str(tt_good_cntr))
            print('tt_bad_cntr val: ' + str(tt_bad_cntr))
            # print('atm_t_cntr: ' + str(atm_t_cntr))             
    
    cntr += 1
    time.sleep(pause_time)
    