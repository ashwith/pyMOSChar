import lookupMOS as lk
import numpy as np
import matplotlib.pyplot as plt


lk.init()
VGS = np.arange(0, 1.8, 0.1)
mid = lk.lookup('nfet', 'id', vds=0.9, vsb=0, l=0.5, vgs=VGS)

plt.plot(VGS, mid)
plt.show()
