This is the instruction for starting the feed forward script 
Using SXR PCAV0 to the TMO laser Target time PV
pcav2laser_proto_TMO.py

Command will be surrounded with \\\\\\\
0. 
Ensure the laser locker HLA is running at TMO.  Or else, the Target time PV won't change the phase motor!!!!!
Open a terminal
==========================================================

1. Get to the right server
\\\\\\\\\\\\\\\\\\\\
ssh psdev
ssh las-console
\\\\\\\\\\\\\\\\\\\\
==========================================================

2. get in to bash
\\\\\\\\\\\\\
bash
\\\\\\\\\\\\\
==========================================================

3. Check if the script is already running
\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
ps ax | grep pcav2laser_proto_TMO.py
\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
for me, it shows 

 1834 pts/1    Sl     0:23 python pcav2laser_proto_TMO.py
16988 pts/1    S+     0:00 grep pcav2laser_proto_TMO.py

if you see 'python pcav2laser_proto_TMO.py' in the return, then the script is already running
you DO NOT need to run the script anymore
==========================================================

4. Source the right environment
\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
source /reg/g/pcds/engineering_tools/xpp/scripts/pcds_conda
\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
==========================================================

5. Go to the right directory
\\\\\\\\\\\\\\\\\\\\\\\\\\\
cd /cds/home/c/charliex
\\\\\\\\\\\\\\\\\\\\\\\\\\\
==========================================================

6. start python
\\\\\\\\\\\\\\\\\\\\
python
\\\\\\\\\\\\\\\\\\\\
==========================================================

7. get the current TMO Target time value
\\\\\\\\\\\\\\\\\\\\\\\\\
import epics as epics
TMO_LAS_TT_PV = 'LAS:FS14:VIT:FS_TGT_TIME'  # EGU in ns
TMO_TT_init_Val = epics.caget(TMO_LAS_TT_PV)
print(TMO_TT_init_Val)
\\\\\\\\\\\\\\\\\\\\\\\\\\

write down the value, and keep it safe somewhere, incase you need to recover the target time
==========================================================

8. start the script in nohup mode
\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
nohup python pcav2laser_proto_TMO.py &
\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
==========================================================

9. to kill the pcav2laser_proto_TMO.py script
\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
ps ax | grep pcav2laser_proto_TMO.py
\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
for me, it shows 

 1834 pts/1    Sl     0:23 python pcav2laser_proto_TMO.py
16988 pts/1    S+     0:00 grep pcav2laser_proto_TMO.py

it is the PID 1834 you want to kill
\\\\\\\\\\\\\\\\\\\\\\
kill -9 1834
\\\\\\\\\\\\\\\\\\\\\\

NOTE!!!!!!
If you didn't start the script, you might need to contact the controls person to kill the process
==========================================================


10. If you need to recover the target time
\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
python
\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
then

\\\\\\\\\\\\\\\\\\\\\\\\\\\\
import epics as epics
TMO_LAS_TT_PV = 'LAS:FS14:VIT:FS_TGT_TIME'  # EGU in ns
epics.put(TMO_LAS_TT_PV, _____________)

\\\\\\\\\\\\\\\\\\\\\\\\\\\\
please replace ___________ with the initial value you wrote down for the target time