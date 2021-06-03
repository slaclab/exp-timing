import time as time

pause_time = 0.1
cntr = 0
t_old = time.time()

while True:
    t = time.time()
    dt = t - t_old
    if (cntr%(1/pause_time) == 0):
        # it is true every second because 10, 20, 30 are all interger divide of 10
        print('//////////////////////////////////////////////////////////////////')
        print('Counter val: ' + str(cntr))     
    print(dt)  
    cntr += 1
    t_old = t
    time.sleep(pause_time) 