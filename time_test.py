import time

pause_time = 0.1
cntr = 0

while True:
    if (cntr%(pause_time*3000) == 0):
        # it is true every second because 10, 20, 30 are all interger divide of 10
        print('//////////////////////////////////////////////////////////////////')
        print('Counter val: ' + str(cntr))       
    cntr += 1
    time.sleep(pause_time) 