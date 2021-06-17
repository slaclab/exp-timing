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
    atm_pv_key = ["ATM_time", "ATM_time", "ATM_amp", "ATM_amp", "ATM_amp", "ATM_fwhm"]

    print(len(P.pv_val["ATM_WF"]))
    ATM_pos = P.pv_val["ATM_WF"][0]
    ATM_val = P.pv_val["ATM_WF"][1]
    ATM_amp = P.pv_val["ATM_WF"][2]
    ATM_nxt_amp = P.pv_val["ATM_WF"][3]
    ATM_ref_amp = P.pv_val["ATM_WF"][4]
    ATM_fwhm = P.pv_val["ATM_WF"][5]

    pause_time = Q.config_var["pause_time"]
    atm_good_thre = Q.config_var["atm_good_thre"]
    atm_bad_thre = Q.config_var["atm_bad_thre"]
    atm_avg_n = Q.config_var["atm_avg_n"]
    time_err_th = Q.config_var["time_err_th"]
    atm_val_ary = np.array([0])
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

    # enabled the drift feedback
    epics.caput(P.pvlist["DC_sw"], 1)
    cntr = 0

    print("Controller running")
    while True:
        # Read PV values
        a = P.pvlist.keys()
        for pv in a:
            # print(pv)
            P.pv_val[pv] = epics.caget(P.pvlist[pv])
        
        # Get limit threshold from EDM
        tt_amp_hi_val = epics.caget((P.pvlist["ATM_amp"] + ".HIGH"))
        tt_amp_lo_val = epics.caget((P.pvlist["ATM_amp"] + ".LOW"))
        tt_fwhm_hi_val = epics.caget((P.pvlist["ATM_fwhm"] + ".HIGH"))
        tt_fwhm_lo_val = epics.caget((P.pvlist["ATM_fwhm"] + ".LOW"))

        # Push ATM value from WF PV to dedicated PVs
        ATM_pos = P.pv_val["ATM_WF"][0]
        ATM_val = P.pv_val["ATM_WF"][1]
        ATM_amp = P.pv_val["ATM_WF"][2]
        ATM_nxt_amp = P.pv_val["ATM_WF"][3]
        ATM_ref_amp = P.pv_val["ATM_WF"][4]
        ATM_fwhm = P.pv_val["ATM_WF"][5]
        if (cntr%(1/Q.config_var["pause_time"]) == 0):
            for i in range(len(P.pv_val["ATM_WF"])):
                print(P.pv_val["ATM_WF"][i])
                print(P.pvlist[atm_pv_key[i]])
        
        cast_dif = cast_old - P.pv_val["CAST_PS_R"]
        cast_dif_ns = np.true_divide(cast_dif, 1000)

        # Condition for good atm reading
        # if (atm_amp > tt_amhilo_val)and(IPM_val > ipm_lo_val)and(atm_fwhm < ttfwhm_hi)and(atm_fwhm > ttfwhm_lo):
        if ((P.pv_val["HUTCH_XRAY_ST"]==0) and
            (ATM_amp>tt_amp_lo_val) and
            (ATM_fwhm<tt_fwhm_hi_val) and
            (ATM_fwhm>tt_fwhm_lo_val) and
            (ATM_val!=atm_val_ary[-1])):
            tt_good_cntr += 1
            tt_good = True
        else:
            tt_bad_cntr += 1
            tt_good = False
        
        # Determine if use ATM or PCAV as drift compensation
        if (tt_good_cntr > atm_good_thre) and (cntr%(10/pause_time) == 0) :
            atm_stat = True
            tt_good_cntr = 0
            tt_bad_cntr = 0
        elif (tt_bad_cntr > atm_bad_thre) and (cntr%(10/pause_time) == 0) :
            atm_stat = False
            tt_good_cntr = 0
            tt_bad_cntr = 0
        elif (cntr%(20/pause_time) == 0) :
            atm_t_cntr = 1
            tt_good_cntr = 0
            tt_bad_cntr = 0
    
        # Filling the running avg array
        if tt_good:            
            if cntr == 0 and tt_good:
                atm_val_ary[0] = ATM_val
            elif (atm_val_ary.size >= atm_avg_n) and tt_good:
                atm_val_ary = np.delete(atm_val_ary, 0)
                atm_val_ary = np.append(atm_val_ary,ATM_val)
            else:
                if tt_good:
                    atm_val_ary = np.append(atm_val_ary,ATM_val)
            # average and convert to fs, ns, also add in the offset 
            atm_ary_mean  = np.mean(atm_val_ary) - P.pv_val["PCAV_FB_OFFSET"]
            atm_ary_mean_fs = np.around(np.multiply(atm_ary_mean, 1000), 3)
            atm_ary_mean_ns = np.true_divide(atm_ary_mean, 1000)
            atm_err = np.multiply(atm_ary_mean, P.pv_val["ATM_FB_GAIN"])
            atm_err_ns = np.true_divide(atm_err, 1000)

        if (cntr%(2/pause_time) == 0):
            # epics.caput(TT_amp_PV, atm_amp)  # Update EDM panel
            print('#################################')
            print('ATM array error: ' + str(atm_err) + 'ps')
            print('ATM array mean: ' + str(atm_ary_mean_fs) + 'fs')        
            print('ATM time: ' + str(ATM_val))
            print('ATM amp: ' + str(ATM_amp) + '  HIGH:' + str(tt_amp_hi_val) + ' LOW:' + str(tt_amp_lo_val))
            print('ATM fwhm: ' + str(ATM_fwhm) + '  HIGH:' + str(tt_fwhm_hi_val) + ' LOW:' + str(tt_fwhm_lo_val))
            print('IPM val: ' + str(P.pv_val["IPM"]))
            print('tt_good_cntr: ' + str(tt_good_cntr))
            print('tt_bad_cntr: ' + str(tt_bad_cntr))
            print('ATM feedback used status: ' + str(P.pv_val["ATM_FB_EN"]))
            print('ATM offset: ' + str(P.pv_val["PCAV_FB_OFFSET"]) + 'ps')
            print('+++++++++++++++++++++++++++++++++++++')
            print(atm_val_ary)

        if (atm_val_ary.size == atm_avg_n) and (np.absolute(atm_ary_mean_fs)>time_err_th) and (P.pv_val["ATM_FB_EN"] != 0):   
            t_now = time.time()
            dt = t_now - t_old
            print('Move to compensate')
            # DC_val = (p_term * atm_err_ns) + (i_term * (i_val + (np.multiply(atm_err_ns, dt))))
            DC_val = epics.caget(P.pvlist["DC_val"])
            DC_val = DC_val + atm_err_ns
            epics.caput(P.pvlist["DC_val"], DC_val)
            print('ATM err fs average: ' + str(atm_ary_mean_fs) +'fs')        
            print('ATM err ns average: ' + str(atm_err_ns))        
            print("move DC PV to: " + str(DC_val))
            print('Clearning ATM array')
            atm_val_ary = np.array([0])
            t_old = t_now
        # else:
        #     # DC_val = epics.caget(DC_val_PV)
        #     # DC_val = DC_val + cast_dif_ns
        #     # epics.caput(DC_val_PV, DC_val)
            
        #     if (cntr%(2/pause_time) == 0):
        #         print('#################################')
        #         print('Bad atm shots')
        #         print('#################################')
        #         print('ATM array error: ' + str(atm_err) + 'ps')
        #         print('ATM array mean: ' + str(atm_ary_mean_fs) + 'fs')        
        #         print('ATM time: ' + str(ATM_val))
        #         print('ATM amp: ' + str(atm_amp) + '  HIGH:' + str(tt_amp_hi_val) + ' LOW:' + str(tt_amp_lo_val))
        #         print('ATM fwhm: ' + str(atm_fwhm) + '  HIGH:' + str(tt_fwhm_hi_val) + ' LOW:' + str(tt_fwhm_lo_val))
        #         print('IPM val: ' + str(IPM_val) + '  HIGH:' + str(ipm_hi_val) + ' LOW:' + str(ipm_lo_val))
        #         print('tt_good_cntr: ' + str(tt_good_cntr))
        #         print('tt_bad_cntr: ' + str(tt_bad_cntr))
        #         print('ATM feedback used status: ' + str(P.pv_val["ATM_FB_EN"]))    
        #         print('+++++++++++++++++++++++++++++++++++++')
        #         print(atm_val_ary)                    
        #         # print(np.multiply(cast_dif,1000))
        #         # print('tt_good_cntr: ' + str(tt_good_cntr))
        #         # print('tt_bad_cntr: ' + str(tt_bad_cntr))
    
        if (cntr%(60/pause_time) == 0):
            print('//////////////////////////////////////////////////////////////////')
            print('Counter val: ' + str(cntr))
            ts = time.strftime('%Y-%m-%d-%H:%M:%S', time.localtime())
            print(ts)        

        # clean up
        atm_offset_pre = P.pv_val["PCAV_FB_OFFSET"]        
        cast_old = P.pv_val["CAST_PS_R"]
        las_tt_pre = P.pv_val["LAS_TT"]
        # Reset the counter after 10minutes
        if (cntr%((60*10)/pause_time) == 0):
            cntr = 1
        else:
            cntr += 1
        time.sleep(pause_time)



if __name__ == "__main__":
    if len(sys.argv) < 2:
        drift_comp_fb()  # null input will prompt
    else:
        drift_comp_fb(sys.argv[1])