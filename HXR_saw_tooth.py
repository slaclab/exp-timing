import epics as epics
import numpy as np
import time as time


HXR_CAST_PS_PV_W = 'LAS:UND:MMS:02'
HXR_CAST_PS_PV_R = 'LAS:UND:MMS:02.RBV'

fs_scale    = 1000 
pause_time  = 2    # Let's give some time for the system to react
Cntl_output = 0
cntr = 0

# let's get the current value of the laser phase shifter
HXR_CAST_init_Val = epics.caget(HXR_CAST_PS_PV_R)
Cntl_output = HXR_CAST_init_Val   # once the script runs, that value is the setpoint
HXR_prev = HXR_CAST_init_Val

# Sawtooth test

print('starting saw tooth')
for i in range(0,1):
    for j in range(0,10):
        print(cntr)
        HXR_TT = epics.caget(HXR_CAST_PS_PV_R)
        print('HXR CAST read')
        print(HXR_TT)
        Cntl_output = HXR_TT + (np.true_divide(500, fs_scale))
        epics.caput(HXR_CAST_PS_PV_W, Cntl_output)
        print(Cntl_output)
        cntr = cntr + 1
        time.sleep(5)
    time.sleep(60)
    for j in range(0,10):
        print(cntr)
        HXR_TT = epics.caget(HXR_CAST_PS_PV_R)
        print('HXR CAST read')
        print(HXR_TT)
        Cntl_output = HXR_TT - (np.true_divide(50, fs_scale))
        epics.caput(HXR_CAST_PS_PV_W, Cntl_output)
        print(Cntl_output)
        cntr = cntr + 1
        time.sleep(5)
    epics.caput(HXR_CAST_PS_PV_W, HXR_CAST_init_Val)    
    time.sleep(60)

HXR_TT = epics.caget(HXR_CAST_PS_PV_R)
print('HXR CAST read')
print(HXR_TT)
Cntl_output = HXR_TT + (np.true_divide(2000, fs_scale))
epics.caput(HXR_CAST_PS_PV_W, Cntl_output)
print(Cntl_output)