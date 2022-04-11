import epics as epics
import numpy as np
import time as time


PV_laser_trig = 'XCS:LAS:EVR:01:TRIG0:TDES'
PV_gate_trig  = 'XCS:LAS:EVR:01:TRIG3:TDES'
PV_laser_width = 'XCS:LAS:EVR:01:TRIG0:TWID'
PV_gate_width  = 'XCS:LAS:EVR:01:TRIG3:TWID'
EC40_T0 = 9277.31   # in ns
EC87_T0 = 731.09    # in ns
gate_early = 3000   # in ns
i = 0

while(i == 0):
    time.sleep(0.2)
    laser_time = epics.caget(PV_laser_trig)
    laser_width = epics.caget(PV_laser_width)
    gate_width = laser_width + gate_early + 500 # have to be at least 0.5us wider than laser trg
    gate_time  = laser_time - gate_early
    print(gate_time)
    epics.caput(PV_gate_width, gate_width)
    epics.caput(PV_gate_trig, gate_time)