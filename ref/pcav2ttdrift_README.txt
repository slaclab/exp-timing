Command will be surrounded with \\\\\\\
0. Open 2 terminal follow until step 4 in both terminals
turn off pcav2cast_hxr feedback

1. Get to the right server
\\\\\\\\\\\\\\\\\\\\
ssh psdev
ssh las-console
\\\\\\\\\\\\\\\\\\\\

2. Go into bash 
\\\\\\\\\\\\\\
bash
\\\\\\\\\\\\\\

3. Source the right environment variable
\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
export PSPKG_ROOT=/reg/g/pcds/pkg_mgr
export PSPKG_RELEASE=controls-0.1.9
source $PSPKG_ROOT/etc/set_env.sh
\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
this will get you all the settings you need to run the python script

4. Go to the directory to run the script
\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
cd /cds/home/c/charliex/justin
\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
I added some visual readback to show the script is running 
in the terminal, just for this test.

5. Get the initial value of the phase motor
\\\\\\\\\\\\\\\\
python
\\\\\\\\\\\\\\\\
this launchs you into python
then paste in

\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
from psp.Pv import Pv
FS4PH=Pv('LAS:FS4:MMS:PH')
FS4PH.get(ctrl=True, timeout=1.0)
\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
copy this number to a notepad. 
you can highlight and then copy 

6. Run the python script in PCAV only mode
######################
SWITCH TO THE OTHER TERMINAL!!!!!
\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
python pcav2ttdrift.py -P XCS
\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
this will start the script and it is an infinit loop
you can not do anything in the terminal while this is running

to stop the loop, press Ctrl + c 


7. Restore the phase motor value 
once you finish the test, use this to put it put
the value back, in the terminal where you got the initial
value
\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
FS4PH.put(8022.080301935433, timeout=1.0)
\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

8. restart pcav2cast_hxr feedback


NOTE:
HXR Phase cavity feedback to the HXR cable stabilizer is now running by the iocManager
If you want to kill the feedback, we would need to contact Sameen to get instructions
on how to turn the feedback on and off



