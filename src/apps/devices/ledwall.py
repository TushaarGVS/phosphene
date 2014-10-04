import device
from phosphene.signal import *
import scipy, numpy
from phosphene.graphs import barGraph
import math

class LEDWall(device.Device):
    def __init__(self, port):
        device.Device.__init__(self, "LEDWall", port)

    def setupSignal(self, signal):
        def LEDWall(s):
            lights = [s.avg6[i] * 150 / max(0.5, s.longavg6[i]) \
                            for i in range(0, 6)]

            lights.reverse()
            return lights

        signal.ledwall = lift(LEDWall)

    def graphOutput(self, signal):
        return barGraph(self.truncate(signal.ledwall) / 255.0)

    def redraw(self, signal):
        payload = self.toByteStream(self.truncate(signal.ledwall))
        print "writing"
        self.port.write("S") #Start
        ack = self.port.read(size=1) #Ack
        print ack
        self.port.write(payload) #Data - First byte - woofers.
        print "done"

    def toByteStream(self,array):
        data = []
        bts = bytearray(6)
        LEVELS = 6
        #Writing 0 to the woofers for now.
        bts[0] = chr(0)
        def group(val):
            div = 42.67 #255/6
            if val == 0:
                return [0 for i in range(0,LEVELS)]
            n = int(math.ceil(val/div)) #Number of levels to be lit. (0-6)
            return [1 for i in range(0,n)] + [0 for i in range(0,6-n)]
        #Convert into a nested array. 6 values with 6 values inside.
        for value in array:
            data.append(group(value))
        #Now convert into Bytes.
        #First 4 bits waste.
        pos = 1
        mod = 4
        print "ARRAY", array
        print "DATA", data
        for channel in data:
            for strip in channel:
                if strip: bts[pos] |= (1 << (7-mod))
                else: bts[pos] &= (~(1<<(7-mod)))
                mod += 1
                if mod == 8:
                    mod = 0
                    pos+=1
        for i in bts:
            print i
        return bts
