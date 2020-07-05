from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import pyaudio
import wave
import time
from math import sin, cos, e, fabs, log
import numpy as np
import subprocess
import threading
from copy import deepcopy
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("filename", type=str)

args = parser.parse_args()

filename = str( args.filename )

chunk = 1024 
wf = wave.open( filename, 'rb' )
print 'woof'
p = pyaudio.PyAudio()


class playerMonitorThread:
    def __init__(self):
        self.monitoringThread        = threading.Thread(None, self.run)
        self.event                   = threading.Event()
        self.monitoringThread.daemon = True
        self.monitorLock             = threading.Lock()
        self.monitor_data            = []
        self.monitoringThread.start()
        

    def run(self):
        print 'Player Monitor Thread Started'
        self.monitor()
        print '**no**'


    def monitor(self):
        stream = p.open( format   = p.get_format_from_width(wf.getsampwidth()),
                         channels = wf.getnchannels(),
                         rate     = wf.getframerate(),
                         output   = True )
        data = wf.readframes( chunk )

        while True:
            #self.monitorLock.acquire() # enable this to see how wrong it goes
            stream.write( data )
            data   = wf.readframes( chunk )
            result = np.fromstring( data, dtype = np.int16 )
            
            chunk_length = len( result ) / 2
            assert chunk_length == int( chunk_length )
            result = np.reshape( result, ( chunk_length, 2 ) )
            
            #fft = np.fft.fft( result  ) 
            
            # frame = np.frombuffer(data, dtype = np.float32)          # interleaved channels
            # frame = np.stack((frame[::2], frame[1::2]), axis=0)      # channels on separate axes

            self.monitorLock.acquire() # also disable this if you want to see it go wrong
            try:
                self.monitor_data.append( result[:, 0] )               # append left channel data only
                #self.monitor_data.append( fft[:,0] )               # append left channel data only
            finally:
                self.monitorLock.release()
                self.event.set()
        

    def getData(self):
        self.event.wait()
        self.monitorLock.acquire()
        try:
            local_data = deepcopy( self.monitor_data )
            self.monitor_data = []
           
        finally:
            self.monitorLock.release()
            self.event.clear()
           
        return local_data
          

def initFun():
    glClearColor( 0.0, 0.0, 0.0, 0.0 )
    glColor3f(    0.0, 0.0, 0.0      )
    glPointSize(  1.0 ) 
    glMatrixMode( GL_PROJECTION )
    glLoadIdentity()
    # glOrtho( -15.0, 15.0,
    #          -15.0, 15.0,
    #          -15.0, 15.0 )
    
    glOrtho( -5.0, 5.0,
             -5.0, 5.0,
             -5.0, 5.0 )


def displayFun():
    
    glClear(GL_COLOR_BUFFER_BIT)
    while True:
        glClear(GL_COLOR_BUFFER_BIT)
        data = player.getData()
        glBegin(GL_POINTS)

        for value in data:
            #print value
            for i, f in enumerate( value ):
                #glColor3f( 1, 1, 1 )
                
                u = float( i/100.0 )
                v = f.real/10000.0
                #glVertex2f( u, v )  
                x = cos(v)*sin(u)
                y = cos(v)*cos(u)
                z = cos(u)
                glColor3f( x, y, z )
                glVertex3f( x, y, z )  
                
        glEnd()
        glFlush()   
        #glTranslatef(0,-0.1,0)
        glRotatef(-0.9, 90, 180,270)
        #time.sleep(0.01)
        

if __name__ == '__main__':
    player = playerMonitorThread()
    glutInit()   
    #glutInitWindowSize(1200,1920)
    glutInitWindowSize( 1920, 1200 )
    glutCreateWindow("Scatter")
    glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB)
    glutDisplayFunc(displayFun)
    initFun()
    glutMainLoop()
