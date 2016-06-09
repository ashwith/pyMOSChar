import charMOS
import numpy as np
mosLengths = np.concatenate((np.arange(0.18, 0.3, 0.02), np.arange(0.3, 2, 0.2), np.arange(2, 10, 0.5), np.array([10])))
#           (mosLengths, modelFile,     modelN,  modelP,  vgsMax, vgsStep, vdsMax, vdsStep, vsbMax, vsbStep, width, temp, numfing, corner):
charMOS.init(mosLengths, 'tsmc180.mod', "cmosn", "cmosp", 0.9,    25e-3,   0.9,    25e-3,   0.9,    25e-3,   10,    300,  10,      'tt')
charMOS.genDB("spectre")
