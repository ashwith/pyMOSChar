import struct
import re
import numpy as np
import collections
import os


def readRaw(fileName):
    
    rawFile = open(fileName, 'rb')
    dataBytes = rawFile.read()
    dataStr = str(dataBytes)
    
    simStarts = [m.start() for m in re.finditer('Title', dataStr)]
    plotDat = collections.OrderedDict()

    for startPtr in simStarts:
        flagStart = dataBytes.find(b'Flags: ', startPtr) + len('Flags: ')
        flags = dataBytes[flagStart:flagStart+4].decode()
        
        if flags == 'real':
        
            # Extract the number of variables
            startPos = dataBytes.find(b'No. Variables: ', startPtr) + len('No. Variables: ')
            endPos = dataBytes.find(b'No. Points:', startPtr)
            numVars = int(dataBytes[startPos:endPos].decode())

            #Extract the number of points
            startPos = endPos + len('No. Points: ')
            endPos = dataBytes.find(b'Variables:', startPos)
            numPoints = int(dataBytes[startPos:endPos].decode())
        
            #Extract variable names
            startPos = endPos + len('Variables:')
            endPos = dataBytes.find(b'Binary:', startPtr)
            varList = dataBytes[startPos:endPos].decode().split()
            
            # Create arrays to store the points
            for j in range(numVars):
                plotDat[(varList[j*3 + 1], varList[j*3 + 2])] = np.zeros((numPoints, 1))
            
            # Populate the arrays
            bytePtr = endPos + len('Binary:\n')
            for j in range(numPoints):
                for k in plotDat.keys():
                    plotDat[k][j] = struct.unpack('d', dataBytes[bytePtr:bytePtr+8])[0]
                    bytePtr += 8
    return plotDat
