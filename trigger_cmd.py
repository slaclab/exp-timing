from subprocess import call
from os import system
import sys
import argparse

def trigger_cmd(rw = 'r', chan = 'all', delay = 0, width = 0, rate = '71kHz'): 
    if chan == "all":
        chan = 4
            
    rate_dict = {'1MHz':0, '71kHz':1, '71KHz':1, '10kHz':2, '1KHz':3, '1kHz':3,
            '100Hz':4, '10Hz':5, '1Hz':6}    
    rw_dict = {'r':0, 'w':1}

    if rate in rate_dict:            
        rate_num = rate_dict[rate]
    else:
        rate_num = 1
        
    delay_tic = ns2tic('delay',delay)
#    print delay_tic
    width_tic = ns2tic('width',width)
    cmd = "ssh laci@cpu-b084-sp01 -t /afs/slac/u/cd/charliex/trigger_cmd " + str(rw_dict[rw]) + " "+ str(chan) +" "+ str(delay_tic) +" "+ str(width_tic) +" "+ str(rate_num) +  ""
    cmd1 = 'ssh laci@cpu-b084-sp01'
    print cmd
    # system(cmd)
    temp = call(cmd, shell=True)
    print temp
    # call("ssh charliex@lcls-dev3 -t '/afs/slac/u/cd/charliex/trigger_cmd'", shell=True)

def ns2tic(name,ns = 0):
    clk = 185.7e6
    clk_period = 1/clk
    
    if (round((int(ns)/clk_period),4) % 1) != 0:
        print str(ns) + " sec is " + str(ns / clk_period) + " evr tics"
        print "Can not have fractical tics, rounding " + name + " setting down to " + str(int(ns / clk_period)) + " evr tics"
        tic = int(ns / clk_period)
    else:
        tic = (ns / clk_period)        
    return tic


#trigger_cmd('r', 'all', 35e-9, 10*(1/185.7e6), '1MHz')
#trigger_cmd('r','3', 7.775*(1/185.7e6), 0.5*(1/185.7e6), '1MHz')
#trigger_cmd('r','2', 12.735*(1/185.7e6), 2.5*(1/185.7e6), '71kHz')
#trigger_cmd('r','1', 1.753*(1/185.7e6), 6.345*(1/185.7e6), '1KHz')
#trigger_cmd('r','0', 0.125*(1/185.7e6), 6.666*(1/185.7e6), '2MHz')
#trigger_cmd()

parser = argparse.ArgumentParser(description='Controlling TPR trigger.')
parser.add_argument('rw', type=str, help='Read/Write option for tpr')
parser.add_argument('chan', type=str, help='specifying channel')
parser.add_argument('delay',type=int, help='delay in ns')
parser.add_argument('width',type=int, help='pulse width in ns')
parser.add_argument('rate',type=str, help='1MHz, 71KHz, 10KHz, 1KHz, 100Hz, 10Hz, 1Hz')

args = parser.parse_args()

trigger_cmd(args.rw, args.chan, args.delay/(1e9), args.width/(1e9), args.rate)

