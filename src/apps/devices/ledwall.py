import device
from phosphene.signal import *
import scipy, numpy
from phosphene.graphs import barGraph
import math
from phosphene import signalutil
from phosphene.util import *
""" The LEDWall is a device which composed of a 6*6 square of led strips.
    Attached to it were 2 "woofers" which had 4 rings of leds 
    and a set of 8 bulbs. The LEDWall was used as an equaliser while the
    woofers and the bulbs responded to beats. """

class LEDWall(device.Device):
    def __init__(self, port):
        device.Device.__init__(self, "LEDWall", port)

    def setupSignal(self, signal):
        def LEDWall(s):
            lights = [s.avg6[i] * 150 / max(0.5, s.longavg6[i]) \
                            for i in range(0, 6)]

            lights.reverse()
            return lights
        
        def beats(s):
            return numpymap(lambda (a, b): 1 if a > b * 1.414 else 0, zip(s.avg6, s.longavg6))
        signal.woofers = signalutil.blend(beats, 0.7) #Beats
        signal.ledwall = lift(LEDWall) 

    def graphOutput(self, signal):
        return barGraph(self.truncate(signal.ledwall) / 255.0)

    def redraw(self, signal):
        payload = self.toByteStream(signal.ledwall,signal.woofers)
        self.port.write("S") #Start
        ack = self.port.read(size=1) #Ack
        self.port.write(payload) #Data - First byte - woofers.

    def toByteStream(self,array,wooferArray):
        data = []
        bts = bytearray(6)
        LEVELS = 6
        beatVal  = wooferArray[1]
        #Writing 0 to the woofers for now.
        def woofByteStream(val,mod):
                n = int(math.ceil(val*4))
                if val<0.5:
                    n=0
                print val,n,bts[0]
                for i in range(0,n):
                    bts[0] |= (1<<(mod+i))
                    print bts[0]
        woofByteStream(beatVal,0) #woofer data
        woofByteStream(beatVal,4)
        woofByteStream(beatVal,4) #bulbs data
        def group(val):
            div = 85.34 #512/6
            if val < 5:
                return [0 for i in range(0,LEVELS)]
            n = min(6,int(math.ceil(val/div))) #Number of levels to be lit. (0-6)
            return [1 for i in range(0,n)] + [0 for i in range(0,6-n)]
        #Convert into a nested array. 6 values with 6 values inside.
        for value in array:
            data.append(group(value))
        #Now convert into Bytes.
        #Last 4 bits is for bulbs and is set earlier.
        pos = 1
        mod = 4
        for channel in data:
            for strip in channel:
                if strip: bts[pos] |= (1 << (7-mod))
                else: bts[pos] &= (~(1<<(7-mod)))
                mod += 1
                if mod == 8:
                    mod = 0
                    pos+=1
        return bts
