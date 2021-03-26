import sys
import subprocess
import time
import os

freq_setpoint = 162500000 # Target frequency of 162.5MHz
VCO_gain = -60.7 # -60.7Hz / Volt for the 162.5MHz Wenzel
DAC_PV = 'IOC:B084:RF04:AO:CH0'
RF_CNT_PV = 'CNTR:B84:FREQ_RBCK'
V_min = -5
V_max = 5



FNULL = open(os.devnull, 'w')

caput_cmd = 'caput '+DAC_PV+' '+(str(i))
subprocess.call(caput_cmd, shell=True, stdout=FNULL)
time.sleep(0.5)
caget_cmd = 'caget -f 3 '+RF_CNT_PV
freq = subprocess.check_output(caget_cmd, shell=True)
time.sleep(0.5)
freq_int = (freq.split())
print(freq_int[1])
