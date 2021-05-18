README.txt for atm2las_fs14.py

Command will be surrounded with \\\\\\\
0. 
Ensure the laser locker HLA is running at TMO.  Or else, the Target time PV won't change the phase motor!!!!!
Open a terminal
==========================================================

1. Get to the right server
\\\\\\\\\\\\\\\\\\\\
ssh -Y psdev
ssh -Y las-console
\\\\\\\\\\\\\\\\\\\\
==========================================================

2. get in to bash
\\\\\\\\\\\\\
bash
\\\\\\\\\\\\\
==========================================================

3. Check if the script is already running
\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
ps ax | grep atm2las_fs14.py
\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
for me, it shows 

 1834 pts/1    Sl     0:23 python atm2las_fs14.py
16988 pts/1    S+     0:00 grep atm2las_fs14.py

if you see 'python atm2las_fs14.py' in the return, then the script is already running
you DO NOT need to run the script anymore
==========================================================

4. Source the right environment
\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
source /reg/g/pcds/engineering_tools/xpp/scripts/pcds_conda
source /reg/g/pcds/engineering_tools/latest-released/rc/bashrc
source /reg/g/pcds/setup/epicsenv-cur.sh
\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
==========================================================

5. Launch the TT EDM panel
\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
/cds/home/s/sfsyunus/lhn/edm-fs14-tt.cmd
\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
you should see under "TIMETOOL DRIFT CONTROL" Correction to be "ON". 
the under the hood correction should be in the "Current Correction [ns]"

6. Go to the right directory
\\\\\\\\\\\\\\\\\\\\\\\\\\\
cd /cds/home/c/charliex
\\\\\\\\\\\\\\\\\\\\\\\\\\\
==========================================================

7. start the script in nohup mode
\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
nohup python atm2las_fs14.py &> atm2las_fs14.out &
\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
==========================================================


8. to kill the atm2las_fs14.py script
You can actually leave the script running, because if TTamp or TT fwhm is too low,
then it will not make it pass the qualify checking gate.
\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
ps ax | grep atm2las_fs14.py
\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
for me, it shows 

 1834 pts/1    Sl     0:23 python atm2las_fs14.py
16988 pts/1    S+     0:00 grep atm2las_fs14.py

it is the PID 1834 you want to kill
\\\\\\\\\\\\\\\\\\\\\\
kill -9 1834
\\\\\\\\\\\\\\\\\\\\\\

NOTE!!!!!!
If you didn't start the script, you might need to contact the controls person to kill the process
==========================================================
