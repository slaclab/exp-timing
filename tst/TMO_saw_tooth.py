import epics as epics
import numpy as np
import time as time

TMO_LAS_TT_PV = 'LAS:FS14:VIT:FS_TGT_TIME'  # EGU in ns
TMO_LAS_TT_D_PV = 'LAS:FS14:VIT:FS_TGT_TIME_DIAL '  # EGU in ns
TMO_LAS_TT_D_PV = 'LAS:FS14:MMS:PH'
TMO_LAS_TTOffset_PV = 'LAS:FS14:VIT:FS_TGT_TIME_OFFSET' 
# XCS_LAS_TT_PV = 'LAS:FS4:VIT:FS_TGT_TIME'  # EGU in ns

fs_scale    = 1000 
pause_time  = 2    # Let's give some time for the system to react
Cntl_output = 0
cntr = 0

# let's get the current value of the laser phase shifter
TMO_TT_init_Val = epics.caget(TMO_LAS_TT_D_PV)
Cntl_output = TMO_TT_init_Val   # once the script runs, that value is the setpoint
TMO_prev = TMO_TT_init_Val

# Sawtooth test

print('starting saw tooth')
for i in range(0,3):
    for j in range(0,10):
        print(cntr)
        TMO_TT = epics.caget(TMO_LAS_TT_D_PV)
        Cntl_output = TMO_TT + (np.true_divide(10, fs_scale))
        epics.caput(TMO_LAS_TT_D_PV, Cntl_output)
        print(j)
        cntr = cntr + 1
        time.sleep(2)
    epics.caput(TMO_LAS_TT_D_PV, TMO_TT_init_Val)    
    time.sleep(4)

# epics.caput(TMO_LAS_TTOffset_PV, TMO_TT_init_Val)