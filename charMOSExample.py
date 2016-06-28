#!/usr/bin/env python

import charMOS
import numpy as np
mosLengths = np.concatenate((np.arange(0.18, 0.3, 0.02), np.arange(0.3, 2, 0.2), np.arange(2, 10, 0.5), np.array([10])))
charMOS.init(mosLengths=mosLengths, modelFile='tsmc180.mod')
charMOS.genDB()
