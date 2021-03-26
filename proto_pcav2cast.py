import epics as epics
import numpy as np
import time as time
import datetime
from matplotlib import pyplot as plt

# now = datetime.datetime.now()
# filename = 'pcav_cast_scan_' + now.strftime('%Y-%m-%d-%H-%M-%S') + '.csv'
# print(filename)
# f = open(filename, 'w')

HXR_PCAV_PV0 = 'SIOC:UNDH:PT01:0:TIME0'
HXR_PCAV_PV1 = 'SIOC:UNDH:PT01:0:TIME1'
HXR_CAST_PS_PV_W = 'LAS:UND:MMS:02'
HXR_CAST_PS_PV_R = 'LAS:UND:MMS:02.RBV'
HXR_CAST2PCAV_Gain = 1.1283 # the slow from plotting cast phase shifter to value read from PCAV

pause_time = 2          # Let's give some time for the system to react
phase_steps = 5        # How many steps we are taking 
phase_gap = 5         # number of ps we are increasing each time
HXR_CAST_PS_target = 0  # Targeted value for the phase shifter
Cntl_gain = 0.1   # Feed back loop gain
#We are doing an exponential fb loop, where the output = output[-1] + (-gain * error)
Cntl_output = 0
Cntl_setpt  = epics.caget(HXR_PCAV_PV0)
pcav_avg_n  = 5

CAST_PS_Val_ary  = np.zeros((phase_steps,))
HXR_PCAV_Val_ary = np.zeros((phase_steps,))
HXR_PCAV_err_ary = np.zeros((phase_steps,))
HXR_PCAV_ctnl_result_ary = np.zeros((phase_steps,))
HXR_PCAV_ctnl_output_ary = np.zeros((phase_steps,))
time_err_ary = np.zeros((pcav_avg_n,))

# let's get the current value of the phase shifter
HXR_CAST_PS_init_Val = epics.caget(HXR_CAST_PS_PV_R)
HXR_CAST_PS_target = HXR_CAST_PS_init_Val
Cntl_output = HXR_CAST_PS_target

cntr = 0
fb_itr = 50
badidea_HXR_PCAV_Val_ary = np.zeros((phase_steps*fb_itr,))
badidea_HXR_PCAV_err_ary = np.zeros((phase_steps*fb_itr,))
badidea_HXR_PCAV_ctnl_output_ary = np.zeros((phase_steps*fb_itr,))
badidea_HXR_CAST_Val_ary = np.zeros((phase_steps*fb_itr,))
badidea_cntr_ary = np.zeros((phase_steps*fb_itr,))

asd = HXR_CAST_PS_target

for y in range(0,phase_steps):
    # print('epics.caget(HXR_CAST_PS_PV_R)')
    print(y)
    HXR_CAST_PS_target = asd+(phase_gap)
    Cntl_output = HXR_CAST_PS_target
    print('Phase shifter target')
    print(HXR_CAST_PS_target)
    CAST_PS_Val_ary[y] = HXR_CAST_PS_target
    # f.write(str(HXR_CAST_PS_target) + ',')
    # print('epics.caput(HXR_CAST_PS_PV_R, ' + str(HXR_CAST_PS_target) + ')')
    epics.caput(HXR_CAST_PS_PV_W, HXR_CAST_PS_target)
    time.sleep(pause_time*3)
    print('Controller running')
    for g in range(0,fb_itr):
        badidea_HXR_CAST_Val_ary[cntr] = HXR_CAST_PS_target
        for h in range(0,pcav_avg_n):
            HXR_PCAV_Val_tmp = epics.caget(HXR_PCAV_PV0)
            time_err = np.around((Cntl_setpt - HXR_PCAV_Val_tmp), decimals=6)
            time_err_ary[h] = time_err
            time.sleep(0.1)
        time_err_ary_sort = np.sort(time_err_ary)
        time_err_ary_sort1 = time_err_ary_sort[1:-1]
        time_err_avg = np.mean(time_err_ary_sort1)
        HXR_PCAV_Val_ary[y] = HXR_PCAV_Val_tmp
        badidea_HXR_PCAV_Val_ary[cntr] = HXR_PCAV_Val_tmp
        print(HXR_PCAV_Val_tmp)
        # f.write(str(HXR_PCAV_Val_ary[y]) + ',')    
        HXR_PCAV_err_ary[y] = time_err_avg
        badidea_HXR_PCAV_err_ary[cntr] = time_err_avg
        print('average error')
        print(time_err_avg)
        # f.write(str(HXR_PCAV_err_ary[y]) + ',')
        # time.sleep(pause_time)
        cntl_temp = np.true_divide(HXR_PCAV_err_ary[y], HXR_CAST2PCAV_Gain)
        cntl_delta = np.multiply(Cntl_gain, cntl_temp)
        Cntl_output = Cntl_output + cntl_delta
        HXR_PCAV_ctnl_output_ary[y] = Cntl_output
        badidea_HXR_PCAV_ctnl_output_ary[cntr] = Cntl_output        
        print('feedback value')
        print(Cntl_output)
        print('feedback delta')
        print(cntl_delta)
        epics.caput(HXR_CAST_PS_PV_W, Cntl_output)
        badidea_cntr_ary[cntr] = cntr
        cntr = cntr + 1
        print('=============================================')        
        time.sleep(2)


print('++++++++++++++++++')
test = np.linspace(0, cntr-1, cntr)
epics.caput(HXR_CAST_PS_PV_W, HXR_CAST_PS_init_Val)

    # # f.write(str(Cntl_output) + ',')
    # time.sleep(pause_time*2)
    # HXR_PCAV_ctnl_result_ary[y] = epics.caget(HXR_PCAV_PV0)
    # f.write(str(HXR_PCAV_ctnl_result_ary[y]) + '\n')
# f.close()

plt.plot(CAST_PS_Val_ary,HXR_PCAV_Val_ary)
plt.plot(CAST_PS_Val_ary,HXR_PCAV_err_ary)
plt.plot(test, badidea_HXR_PCAV_err_ary, '+')
plt.show()
