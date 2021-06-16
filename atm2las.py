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
        pvlist = dict()
        filename = ("ATM_" + str(hn) + "_FB.yml")
        with open(filename, 'r') as yaml_file:
            self.yaml_content = yaml.load(yaml_file, Loader=yaml.SafeLoader)
        print("Key: Value")
        for key, value in self.yaml_content.items():
            print(str(key)+": "+str(value))

        self.pvlist["DC_sw_PV"]  = self.yaml_content.get("DC_sw_PV")
        self.pvlist["DC_val_PV"] = self.yaml_content.get("DC_val_PV")
        self.pvlist["ATM_FB_EN_PV"] = self.yaml_content.get("ATM_FB_EN_PV")
        self.pvlist["ATM_FB_GAIN_PV"] = self.yaml_content.get("ATM_FB_GAIN_PV")
        self.pvlist["ATM_WF_PV"] = self.yaml_content.get("ATM_WF_PV")
        self.pvlist["ATM_TTC_PV"] = self.yaml_content.get("ATM_TTC_PV")
        self.pvlist["IPM_PV"] = self.yaml_content.get("IPM_PV")
        self.pvlist["HUTCH_XRAY_ST_PV"] = self.yaml_content.get["HUTCH_XRAY_ST_PV"]
        self.pvlist["ATM_time_PV"] = self.yaml_content.get["ATM_time_PV"]
        self.pvlist["ATM_amp_PV"] = self.yaml_content.get["ATM_amp_PV"]
        self.pvlist["ATM_fwhm_PV"] = self.yaml_content.get["ATM_fwhm_PV"]
        self.pvlist["PCAV_FB_EN_PV"] = self.yaml_content.get[""]
        self.pvlist["PCAV_FB_GAIN_PV"] = self.yaml_content.get[""]
        self.pvlist["PCAV_FB_OFFSET_PV"] = self.yaml_content.get[""]
        self.pvlist["LXT_thre_PV"] = self.yaml_content.get["LXT_thre_PV"]
        self.pvlist["LAS_TT_PV"] = self.yaml_content.get["LAS_TT_PV"]
        self.pvlist["HXR_CAST_PS_PV_W"] = self.yaml_content.get["HXR_CAST_PS_PV_W"]
        self.pvlist["SXR_CAST_PS_PV_W"] = self.yaml_content.get["SXR_CAST_PS_PV_W"]
        self.atm_avg_n = self.yaml_content.get["atm_avg_n"]
        self.time_err_th = self.yaml_content.get["time_err_th"]
        self.pause_time = self.yaml_content.get["pause_time"]

def drift_comp_fb(hutch='NULL'):
    P = PVS(hutch)
    print(P.yaml_content.get("IPM_PV"))
    print(P.DC_sw_PV)
    DC_val = epics.caget(P.DC_val_PV)
    print(str(DC_val))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        drift_comp_fb()  # null input will prompt
    else:
        drift_comp_fb(sys.argv[1])