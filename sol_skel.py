"""
Solution to the one-way tunnel
"""
import time
import random
from multiprocessing import Lock, Condition, Process
from multiprocessing import Value, Array

SOUTH = "north"
NORTH = "south"

NCARS = 100

class Monitor():
    def __init__(self):
        self.mutex = Lock()
        self.direction = Value('i',2)
        self.changeable = Value('i',1)
        
        self.nexthurry = Value('i',0)
        
        self.crossing = Value('i',0)
        self.waiting = Array('i', [0]*2)
        
        self.cross_allowed = Condition(self.mutex)
        
        self.crossed = Value('i',0)
        
        self.const_too_much_queue = 8

    def crossing_allowed(self):
        return(self.dir == self.direction.value)
    
    def change(self,direction):
        if(self.changeable.value == 1):
            self.changeable.value = 0
            self.direction.value = direction
    
    def ch_exit(self):
        if(self.nexthurry.value != 0):
            self.direction.value = 2
            self.nexthurry.value = 0
        if(self.crossing.value == 0):
            if(self.waiting[0] > 0 or self.waiting[1] > 0):
                self.direction.value = self.waiting[:].index(max(self.waiting[:]))
            else:
                self.changeable.value = 1

    def wants_enter(self, direction):
        self.mutex.acquire()
        
        if(direction == SOUTH):
            self.dir = 0
        elif(direction == NORTH):
            self.dir = 1
        
        self.waiting[self.dir] += 1
        if (self.waiting[self.dir] >= self.const_too_much_queue):
            self.nexthurry.value = 1
        self.change(self.dir)
        self.cross_allowed.wait_for(self.crossing_allowed)
        self.waiting[self.dir] -= 1
        self.crossing.value += 1
        
        self.mutex.release()

    def leaves_tunnel(self, direction):
        self.mutex.acquire()
        self.crossing.value -= 1
#        print(self.direction.value,self.nexthurry.value,self.dir)
        self.ch_exit()
        self.cross_allowed.notify_all()
        self.crossed.value += 1
#        print(self.crossed.value,self.waiting[:],self.direction.value,self.dir,self.crossing.value,self.nexthurry.value)
        self.mutex.release()

def delay(n=3):
    time.sleep(random.random()*n)

def car(cid, direction, monitor):
    print(f"car {cid} direction {direction} created")
    delay(6)
    print(f"car {cid} heading {direction} wants to enter")
    monitor.wants_enter(direction)
    print(f"car {cid} heading {direction} enters the tunnel")
    delay(3)
    print(f"car {cid} heading {direction} leaving the tunnel")
    monitor.leaves_tunnel(direction)
    print(f"car {cid} heading {direction} out of the tunnel")
    print(monitor.crossed.value)
    


def main():
    monitor = Monitor()
    cid = 0
    for _ in range(NCARS):
        direction = NORTH if random.randint(0,1)==1  else SOUTH
        cid += 1
        p = Process(target=car, args=(cid, direction, monitor))
        p.start()
        time.sleep(random.expovariate(1/0.5)) # a new car enters each 0.5s

if __name__ == '__main__':
    main()
