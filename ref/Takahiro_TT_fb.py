fbvalue = 0 # for drift record
while(1):
    tenshots_tt = np.zeros([1,])
    dlen = 0
    while(dlen < 61):
        ttcomm = Popen("caget XPP:TIMETOOL:TTALL",shell = True, stdout=PIPE)
        ttdata = (ttcomm.communicate()[0]).decode()
        current_tt = float((ttdata.split(" "))[3])
        ttamp = float((ttdata.split(" "))[4])
        ipm2val = float((ttdata.split(" "))[5])
        ttfwhm = float((ttdata.split(" "))[7])
        if(dlen%10 == 0):
            print("tt_value",current_tt,"ttamp",ttamp,"ipm2",ipm2val)
        if (ttamp > ttamp_th)and(ipm2val > ipm2_th)and(ttfwhm < 130)and(ttfwhm >  70)and(current_tt != tenshots_tt[-1,]):
            # for filtering (the last one is for when DAQ is stopping)
            tenshots_tt = np.insert(tenshots_tt,dlen,current_tt)
            dlen = np.shape(tenshots_tt)[0]
        time.sleep(0.1)
    tenshots_tt = np.delete(tenshots_tt,0)
    ave_tt = np.mean(tenshots_tt)
    print("Moving average of timetool value:", ave_tt)
    if np.abs(ave_tt) > tt_window:
        ave_tt_second=-(ave_tt*1e-12)
        m.lxt.mvr(ave_tt_second)
        print("feedback %f ps"%ave_tt)
        fbvalue = ave_tt + fbvalue
        drift_log(str(fbvalue))
