import serial
import numpy
import math
from device import Device
from cubelib import rgbemulator as emulator
from cubelib import rgbwireframe as wireframe
from rgbanimations import *
import time
import threading

# A class for the RGBcube
# TODO : 
# Add RGB value dimension to the layer - DONE.
# Convert the ByteStream function to send proper data- DONE. 
# Sending 8 bytes(entire cube)of red first followed by green and then blue.

class Cube(Device):
    def __init__(self, port, dimension=4, emulator=False):
        Device.__init__(self, "Cube", port)
        self.array = numpy.array([[[\
                [0]*3]*dimension]*dimension]*dimension, dtype='bool')
        self.dimension = dimension
        self.emulator = emulator
        self.name = "RGBCube"

    def set_led(self, x, y, z, level=[1,1,1]):
        self.array[x][y][z] = level

    def get_led(self, x, y, z):
        return self.array[x][y][z]

    def takeSignal(self, signal):
        pass

    def toByteStream(self):
        # 16 bits per layer, 0 bits waste. 
	# Note : Bytes to be read in reverse order.
 
        bytesPerLayer = int(math.ceil((self.dimension**2) / 8.0))
        print bytesPerLayer
        discardBits = bytesPerLayer * 8 - self.dimension**2
        print discardBits
	bts = []
        for i in range(0,3):
	    bts.append(bytearray(bytesPerLayer*self.dimension))

        pos = 0
        mod = 0

        for layer in self.array:
            mod = discardBits
            for row in layer:
                for bit in row:
                    for i in range(0,3):
                        if bit[i]: bts[i][pos] |= 1 << mod
                        else: bts[i][pos] &= ~(1 << mod)

                    mod += 1

                    if mod == 8:
                        mod = 0
                        pos += 1
        return bts

    def redraw(self, wf=None, pv=None):
        if self.emulator:
            wf.setVisible(emulator.findIndexArray(self.array))
            pv.run()

if __name__ == "__main__":
    cube = Cube("/dev/ttyACM0",4,True)
    pv = emulator.ProjectionViewer(640,480)
    wf = wireframe.Wireframe()
    pv.createCube(wf)
    count = 0
    start = (0, 0, 0)
    point = (0,0)
    #bs = cube.toByteStream();
    #fillCube(cube,0)
    #cube.redraw()
    def sendingThread():
        while True:
            cube.port.write("S")
            bs = cube.toByteStream()
            for i in range(0, 3):
                time.sleep(0.01)
                for j in range(0,8):
                    cube.port.write(chr(bs[i][j]))
                    print "wrote", bs[i][j]
            assert(cube.port.read() == '.')

    #t = threading.Thread(target=sendingThread)
    #t.start()
    
    while True:
        #wireframeCube(cube,(1,1,1),(9,9,9))
        #fillCube(cube, 1)
        #planeBounce(cube,(count/20)%2+1,count%20)
        #planeBounce(cube,1,count)
        #start = wireframeExpandContract(cube,start)
        #rain(cube,count,5,10)
	#randomness(cube,count)
        #time.sleep(.1)
        #point = voxel(cube,count,point)
	#sine_wave(cube,count)
	#pyramids(cube,count)
	#side_waves(cube,count)
	#fireworks(cube,4)
        #technites(cube, count)
        #setPlane(cube,1,(counter/100)%10,1)
        #setPlane(cube,2,0,1)
	#stringPrint(cube,'TECHNITES',count)
        #moveFaces(cube)
        #cube.set_led(0,0,0)
        #cube.set_led(0,0,1)
        #fillCube(cube,[0,1,0])
        colourCube(cube)
	cube.redraw(wf,pv)
        count += 1
        time.sleep(.1)
