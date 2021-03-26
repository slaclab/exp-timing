import sys
import subprocess
import time
import os

freq_setpoint = 162000000
DAC_PV = 'IOC:B084:RF04:AO:CH0'
RF_CNT_PV = 'CNTR:B84:FREQ_RBCK'
V_min = -5
V_max = 5
V_setp = 0.2
i = V_min
FNULL = open(os.devnull, 'w')

while i <= V_max:
	caput_cmd = 'caput '+DAC_PV+' '+(str(i))
	subprocess.call(caput_cmd, shell=True, stdout=FNULL)
	time.sleep(0.5)
	caget_cmd = 'caget -f 3 '+RF_CNT_PV
	freq = subprocess.check_output(caget_cmd, shell=True)
	time.sleep(0.5)
	freq_int = (freq.split())
	print(freq_int[1])
	i = i + V_setp
