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
LAS_TT_PV = 'LAS:FS4:VIT:FS_TGT_TIME'      # EGU in ns
HXR_CAST_PS_PV_W = 'LAS:UND:MMS:02'        # EGU in ps
HXR_CAST_PS_PV_R = 'LAS:UND:MMS:02.RBV'
SXR_CAST_PS_PV_W = 'LAS:UND:MMS:01'        # EGU in ps
SXR_CAST_PS_PV_R = 'LAS:UND:MMS:01.RBV'

# put limit threshold PV here from EDM

avg_n = 60
# ATM Feedback variables
atm_avg_n = avg_n
atm_val_ary = np.zeros(avg_n)
ttamp_th = 0.05
ipm2_th = 3000
ttfwhm_hi = 130
ttfwhm_lo = 70
ATM_wf_val = epics.caget(ATM_PV)
ATM_pos = ATM_wf_val[0]
ATM_val = ATM_wf_val[1]
ATM_amp = ATM_wf_val[2]
ATM_nxt_amp = ATM_wf_val[3]
ATM_ref_amp = ATM_wf_val[4]
ATM_fwhm = ATM_wf_val[5]
atm_pm_step = 0


