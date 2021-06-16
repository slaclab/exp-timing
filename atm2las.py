#####################################################################
# Filename: atm2las.py
# Author: Chengcheng Xu (charliex@slac.stanford.edu)
# Date: 06/15/2021
#####################################################################
import epics as epics
import sys
import numpy as np
import time as time
import datetime
import yaml

class PVS():
    def __init__(self,hn):              
        self.pvlist = dict()
        self.pv_val  = dict()

        filename = ("ATM_" + str(hn) + "_FBPV.yml")
        with open(filename, 'r') as yaml_file:
            self.yaml_content = yaml.load(yaml_file, Loader=yaml.SafeLoader)
        
        a = self.yaml_content.keys()
        for pv in a:
            print(pv)
            self.pvlist[pv] = self.yaml_content.get(pv)
            self.pv_val[pv] = epics.caget(self.pvlist[pv])

class Config_var():
    def __init__(self,hn):
        self.config_var = dict()

        filename = ("ATM_" + str(hn) + "_FBVal.yml")
        with open(filename, 'r') as yaml_file:
            self.yaml_content = yaml.load(yaml_file, Loader=yaml.SafeLoader)
        
        a = self.yaml_content.keys()
        for pv in a:
            print(pv)
            self.config_var[pv] = self.yaml_content.get(pv)

def drift_comp_fb(hutch='NULL'):
    P = PVS(hutch)
    Q = Config_var(hutch)

    print("Key: Value")
    for key, value in P.pv_val.items():
        print(str(key)+": "+str(value))
    for key, value in Q.config_var.items():
        print(str(key)+": "+str(value))
    atm_pv_key = ["ATM_time", "ATM_amp", "ATM_fwhm"]

    print(len(P.pv_val["ATM_WF"]))
    ATM_pos = P.pv_val["ATM_WF"][0]
    ATM_val = P.pv_val["ATM_WF"][1]
    ATM_amp = P.pv_val["ATM_WF"][2]
    ATM_nxt_amp = P.pv_val["ATM_WF"][3]
    ATM_ref_amp = P.pv_val["ATM_WF"][4]
    ATM_fwhm = P.pv_val["ATM_WF"][5]

    atm_err = 0
    atm_ary_mean = 0
    atm_ary_mean_fs = 0
    atm_pm_step = 0
    atm_prev = ATM_val
    atm_t_cntr = 1      
    las_tt_pre = P.pv_val["LAS_TT"]
    # atm_offset_pre = epics.caget(ATM_OFFSET_PV)
    i_val  = 0
    t_old = time.time()    
    
    # PCAV/CAST feed forward variables 
    atm_stat = True
    tt_good_cntr = 0
    tt_bad_cntr = 0

    time_err_ary = 0 
    cast_old = P.pv_val["CAST_PS_R"]

    cntr = 0

    # enabled the drift feedback
    epics.caput(P.pvlist["DC_sw"], 1)

    print("Controller running")
    while True:
        for i in range(len(P.pv_val["ATM_WF"])):
            print(P.pv_val["ATM_WF"][i])
            epics.caput(P.pvlist[])



if __name__ == "__main__":
    if len(sys.argv) < 2:
        drift_comp_fb()  # null input will prompt
    else:
        drift_comp_fb(sys.argv[1])