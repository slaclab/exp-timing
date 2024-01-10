import epics as epics
import numpy as np
import time as time
import datetime

# now = datetime.datetime.now()
# filename = 'pcav_cast_scan_' + now.strftime('%Y-%m-%d-%H-%M-%S') + '.txt'
# print(filename)
# f = open(filename, 'w')

# Define the PV variables
HXR_PCAV_PV0 = 'SIOC:UNDH:PT01:0:TIME0'
HXR_PCAV_PV1 = 'SIOC:UNDH:PT01:0:TIME1'
HXR_CAST_PS_PV_W = 'LAS:UND:MMS:02'
HXR_CAST_PS_PV_R = 'LAS:UND:MMS:02.RBV'
SXR_PCAV_PV0 = 'SIOC:UNDS:PT01:0:TIME0'
SXR_PCAV_PV1 = 'SIOC:UNDS:PT01:0:TIME1'
SXR_CAST_PS_PV_W = 'LAS:UND:MMS:01'
SXR_CAST_PS_PV_R = 'LAS:UND:MMS:01.RBV'

# Assign the beamline specific PV to the general purpose call variables 
CAST_PS_PV_W = HXR_CAST_PS_PV_W
CAST_PS_PV_R = HXR_CAST_PS_PV_R
PCAV_PV0 = SXR_PCAV_PV0
PCAV_PV1 = SXR_PCAV_PV1

pause_time = 10   # Let's give some time for the system to react
phase_steps = 1000  # How many steps we are taking 
phase_gap = 0.001      # number of ps we are increasing each time
CAST_PS_target = 0  # Targeted value for the phase shifter
y = 0

PCAV_Val_ary = np.zeros((phase_steps,))

# let's get the current value of the phase shifter
CAST_PS_init_Val = epics.caget(HXR_CAST_PS_PV_R)
CAST_PS_target = CAST_PS_init_Val

while true:
    print('PS value')
    print(CAST_PS_target)
    print('Step')
    print(y)
    CAST_PS_target = CAST_PS_init_Val + (phase_gap * y)
    if y < phase_steps:
        y = y + 1
    else:
        y = 0
    print('epics.caput(' + CAST_PS_PV_W + ', ' + str(CAST_PS_target) + ')')
    epics.caput(CAST_PS_PV_W, CAST_PS_target)
    time.sleep(pause_time)

# for y in range(0,phase_steps):
#     # print('epics.caget(CAST_PS_PV_R)')
#     print(y)
#     CAST_PS_target = CAST_PS_target+(phase_gap)
#     print(CAST_PS_target)
#     f.write(str(CAST_PS_target) + ',')
#     print('epics.caput(' + CAST_PS_PV_W + ', ' + str(CAST_PS_target) + ')')
#     # epics.caput(CAST_PS_PV_W, CAST_PS_target)
#     time.sleep(pause_time)
#     print('PCAV value')
#     PCAV_Val_ary[y] = epics.caget(PCAV_PV0)
#     print(PCAV_Val_ary[y])
#     f.write(str(PCAV_Val_ary[y]) + '\n')
#     print('==========================================')

epics.caput(CAST_PS_PV_W, CAST_PS_init_Val)
# f.close()
# print(y)
# print(now.strftime('%Y-%m-%d-%H-%M-%S'))