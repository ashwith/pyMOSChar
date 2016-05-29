import os
import os.path
import sys
import pickle
import pltNgspice
import numpy as np

mosDat = {}
vgsStep =   None
vdsStep =   None
vsbStep =   None

vgsMax  =   None
vdsMax  =   None
vsbMax  =   None

mosLengths = None 

width = None
vsb   = None

modelFile = None

def init(mosLengths, modelFile, vgsMax=1.8, vgsStep=25e-3, vdsMax=1.8, vdsStep=25e-3, vsbMax=1.8, vsbStep=25e-3, width=10, temp=300, numfing=10, corner='T'):

    global vsb

    if (not os.path.isfile(modelFile)):
        print("Model file {0} not found!".format(modelFile))
        print("Please call init() again with a valid model file")
        return None

    globals()['mosLengths'] = mosLengths

    globals()['vgsStep']    =   vgsStep
    globals()['vdsStep']    =   vdsStep
    globals()['vsbStep']    =   vsbStep

    globals()['vgsMax']     =   vgsMax
    globals()['vdsMax']     =   vdsMax
    globals()['vsbMax']     =   vsbMax
    globals()['width']      =   width
    
    globals()['modelFile']  =   modelFile

    vgs = np.linspace(0, vgsMax, vgsMax/vgsStep + 1)
    vds = np.linspace(0, vdsMax, vdsMax/vdsStep + 1)
    vsb = np.linspace(0, vsbMax, vsbMax/vsbStep + 1)

    mosDat['pfet'] = {}
    mosDat['nfet'] = {}
    mosDat['modelFile'] = modelFile

    mosDat['nfet']['corner'] = corner
    mosDat['nfet']['temp'] = temp
    mosDat['nfet']['length'] = mosLengths
    mosDat['nfet']['width'] = width
    mosDat['nfet']['numfing'] = numfing
    mosDat['nfet']['vgs'] = vgs
    mosDat['nfet']['vds'] = vds
    mosDat['nfet']['vsb'] = -vsb
    
    mosDat['pfet']['corner'] = corner
    mosDat['pfet']['temp'] = temp
    mosDat['pfet']['length'] = mosLengths
    mosDat['pfet']['width'] = width
    mosDat['pfet']['numfing'] = numfing
    mosDat['pfet']['vgs'] = -vgs
    mosDat['pfet']['vds'] = -vds
    mosDat['pfet']['vsb'] = vsb

    # 4D arrays to store MOS data-->f(L,               VSB,      VDS,      VGS      )
    mosDat['nfet']['id']  = np.zeros((len(mosLengths), len(vsb), len(vds), len(vgs)))
    mosDat['nfet']['vt']  = np.zeros((len(mosLengths), len(vsb), len(vds), len(vgs)))
    mosDat['nfet']['gm']  = np.zeros((len(mosLengths), len(vsb), len(vds), len(vgs)))
    mosDat['nfet']['gmb'] = np.zeros((len(mosLengths), len(vsb), len(vds), len(vgs)))
    mosDat['nfet']['gds'] = np.zeros((len(mosLengths), len(vsb), len(vds), len(vgs)))
    mosDat['nfet']['cgg'] = np.zeros((len(mosLengths), len(vsb), len(vds), len(vgs)))
    mosDat['nfet']['cgs'] = np.zeros((len(mosLengths), len(vsb), len(vds), len(vgs)))
    mosDat['nfet']['cgd'] = np.zeros((len(mosLengths), len(vsb), len(vds), len(vgs)))
    mosDat['nfet']['cgb'] = np.zeros((len(mosLengths), len(vsb), len(vds), len(vgs)))
    mosDat['nfet']['cdd'] = np.zeros((len(mosLengths), len(vsb), len(vds), len(vgs)))
    mosDat['nfet']['css'] = np.zeros((len(mosLengths), len(vsb), len(vds), len(vgs)))

    mosDat['pfet']['id']  = np.zeros((len(mosLengths), len(vsb), len(vds), len(vgs)))
    mosDat['pfet']['vt']  = np.zeros((len(mosLengths), len(vsb), len(vds), len(vgs)))
    mosDat['pfet']['gm']  = np.zeros((len(mosLengths), len(vsb), len(vds), len(vgs)))
    mosDat['pfet']['gmb'] = np.zeros((len(mosLengths), len(vsb), len(vds), len(vgs)))
    mosDat['pfet']['gds'] = np.zeros((len(mosLengths), len(vsb), len(vds), len(vgs)))
    mosDat['pfet']['cgg'] = np.zeros((len(mosLengths), len(vsb), len(vds), len(vgs)))
    mosDat['pfet']['cgs'] = np.zeros((len(mosLengths), len(vsb), len(vds), len(vgs)))
    mosDat['pfet']['cgd'] = np.zeros((len(mosLengths), len(vsb), len(vds), len(vgs)))
    mosDat['pfet']['cgb'] = np.zeros((len(mosLengths), len(vsb), len(vds), len(vgs)))
    mosDat['pfet']['cdd'] = np.zeros((len(mosLengths), len(vsb), len(vds), len(vgs)))
    mosDat['pfet']['css'] = np.zeros((len(mosLengths), len(vsb), len(vds), len(vgs)))



def genNetlistN(fName='charNMOS.net'):
    netlistN = open(fName, 'w')
    netlistN.write("Characterize N Channel MOSFET\n")
    netlistN.write("\n")
    netlistN.write(".include {0}\n".format(modelFile))
    netlistN.write(".include simParams.net\n")
    netlistN.write("\n")
    netlistN.write("vds  nDrain 0 dc 0\n")
    netlistN.write("vgs  nGate  0 dc 0\n")
    netlistN.write("vbs  nBulk  0 dc {-sb}\n")
    netlistN.write("\n")
    netlistN.write("mn nDrain nGate 0 nBulk cmosn  L={{length*1e-6}} W={{{0}*1e-6}}\n".format(width))
    netlistN.write("\n")
    netlistN.write(".options dccap post brief accurate\n")
    netlistN.write(".control\n")
    netlistN.write("save all @mn[id] \n")
    netlistN.write("+ @mn[vth]\n")
    netlistN.write("+ @mn[gm]\n")
    netlistN.write("+ @mn[gmbs] \n")
    netlistN.write("+ @mn[gds] \n")
    netlistN.write("+ @mn[cgg] \n")
    netlistN.write("+ @mn[cgs] \n")
    netlistN.write("+ @mn[cgd] \n")
    netlistN.write("+ @mn[cdd] \n")
    netlistN.write("+ @mn[cbs] \n")
    netlistN.write("\n")
    netlistN.write("dc vgs 0 {0} {1} vds 0 {2} {3}\n".format(vgsMax, vgsStep, vdsMax, vdsStep))
    netlistN.write("\n")
    netlistN.write("let id   = @mn[id]\n")
    netlistN.write("let vt   = @mn[vth]\n")
    netlistN.write("let gm   = @mn[gm]\n")
    netlistN.write("let gmb  = @mn[gmbs]\n")
    netlistN.write("let gds  = @mn[gds]\n")
    netlistN.write("let cgg  = @mn[cgg]\n")
    netlistN.write("let cgs  = -@mn[cgs]\n")
    netlistN.write("let cgd  = -@mn[cgd]\n")
    netlistN.write("let cgb  = @mn[cgg] - (-@mn[cgs])-(-@mn[cgd])\n")
    netlistN.write("let cdd  = @mn[cdd]\n")
    netlistN.write("let css  = -@mn[cgs]-@mn[cbs]\n")
    netlistN.write("\n")
    netlistN.write("write outN.raw id vt gm gmb gds cgg cgs cgd cgb cdd css\n")
    netlistN.write("exit\n")
    netlistN.write(".endc\n")
    netlistN.write(".end\n")
    netlistN.close();
    
def genNetlistP(fName='charPMOS.net'):
    netlistP = open(fName, 'w')
    netlistP.write("Characterize P Channel MOSFET\n")
    netlistP.write("\n")
    netlistP.write(".include {0}\n".format(modelFile))
    netlistP.write(".include simParams.net\n")
    netlistP.write("\n")
    netlistP.write("vds  nDrain 0 dc 0\n")
    netlistP.write("vgs  nGate  0 dc 0\n")
    netlistP.write("vbs  nBulk  0 dc sb\n")
    netlistP.write("\n")
    netlistP.write("mp nDrain nGate 0 nBulk cmosp  L={{length*1e-6}} W={{{0}*1e-6}}\n".format(width))
    netlistP.write("\n")
    netlistP.write(".options dccap post brief accurate\n")
    netlistP.write(".control\n")
    netlistP.write("save all @mp[id] \n")
    netlistP.write("+ @mp[vth]\n")
    netlistP.write("+ @mp[gm]\n")
    netlistP.write("+ @mp[gmbs] \n")
    netlistP.write("+ @mp[gds] \n")
    netlistP.write("+ @mp[cgg] \n")
    netlistP.write("+ @mp[cgs] \n")
    netlistP.write("+ @mp[cgd] \n")
    netlistP.write("+ @mp[cdd] \n")
    netlistP.write("+ @mp[cbs] \n")
    netlistP.write("\n")
    netlistP.write("dc vgs 0 {0} {1} vds 0 {2} {3}\n".format(-vgsMax, -vgsStep, -vdsMax, -vdsStep))
    netlistP.write("\n")
    netlistP.write("let id   = @mp[id]\n")
    netlistP.write("let vt   = @mp[vth]\n")
    netlistP.write("let gm   = @mp[gm]\n")
    netlistP.write("let gmb  = @mp[gmbs]\n")
    netlistP.write("let gds  = @mp[gds]\n")
    netlistP.write("let cgg  = @mp[cgg]\n")
    netlistP.write("let cgs  = -@mp[cgs]\n")
    netlistP.write("let cgd  = -@mp[cgd]\n")
    netlistP.write("let cgb  = @mp[cgg] - (-@mp[cgs])-(-@mp[cgd])\n")
    netlistP.write("let cdd  = @mp[cdd]\n")
    netlistP.write("let css  = -@mp[cgs]-@mp[cbs]\n")
    netlistP.write("\n")
    netlistP.write("write outP.raw id vt gm gmb gds cgg cgs cgd cgb cdd css\n")
    netlistP.write("exit\n")
    netlistP.write(".endc\n")
    netlistP.write(".end\n")
    netlistP.close();
        
def genSiMParams(L, VSB):
    paramFile = open("simParams.net", 'w')
    paramFile.write(".param length={0}\n".format(L))
    paramFile.write(".param sb={0}\n".format(VSB))
    paramFile.close()
    
def runSim(fileN='charNMOS.net', fileP='charPMOS.net'):
    os.system("ngspice {0} &> /dev/null".format(fileN))
    os.system("ngspice {0} &> /dev/null".format(fileP))
    
def genDB():
    genNetlistN()
    genNetlistP()
    
    progTotal = len(mosLengths)*len(vsb)
    progCurr  = 0
    print("Data generation in progress. Go have a coffee...")
    for idxL in range(len(mosLengths)):
        for idxVSB in range(len(vsb)):
            genSiMParams(mosLengths[idxL], vsb[idxVSB])
            runSim()
            
            simDat = pltNgspice.read('outN.raw')
            
            mosDat['nfet']['id'][idxL][idxVSB]  = simDat['i(id)']
            mosDat['nfet']['vt'][idxL][idxVSB]  = simDat['vt']
            mosDat['nfet']['gm'][idxL][idxVSB]  = simDat['gm']
            mosDat['nfet']['gmb'][idxL][idxVSB] = simDat['gmb']
            mosDat['nfet']['gds'][idxL][idxVSB] = simDat['gds']
            mosDat['nfet']['cgg'][idxL][idxVSB] = simDat['cgg']
            mosDat['nfet']['cgs'][idxL][idxVSB] = simDat['cgs']
            mosDat['nfet']['cgd'][idxL][idxVSB] = simDat['cgd']
            mosDat['nfet']['cgb'][idxL][idxVSB] = simDat['cgb']
            mosDat['nfet']['cdd'][idxL][idxVSB] = simDat['cdd']
            mosDat['nfet']['css'][idxL][idxVSB] = simDat['css']
            
            simDat = pltNgspice.read('outP.raw')
            
            mosDat['pfet']['id'][idxL][idxVSB]  = simDat['i(id)']
            mosDat['pfet']['vt'][idxL][idxVSB]  = simDat['vt']
            mosDat['pfet']['gm'][idxL][idxVSB]  = simDat['gm']
            mosDat['pfet']['gmb'][idxL][idxVSB] = simDat['gmb']
            mosDat['pfet']['gds'][idxL][idxVSB] = simDat['gds']
            mosDat['pfet']['cgg'][idxL][idxVSB] = simDat['cgg']
            mosDat['pfet']['cgs'][idxL][idxVSB] = simDat['cgs']
            mosDat['pfet']['cgd'][idxL][idxVSB] = simDat['cgd']
            mosDat['pfet']['cgb'][idxL][idxVSB] = simDat['cgb']
            mosDat['pfet']['cdd'][idxL][idxVSB] = simDat['cdd']
            mosDat['pfet']['css'][idxL][idxVSB] = simDat['css']
            
            rows, columns = os.popen('stty size', 'r').read().split()
            columns = int(columns) - 10
            progCurr += 1
            progPercent = 100 * progCurr / progTotal
            progLen = int(progPercent*columns/100)
            sys.stdout.write("\r[{0}{1}] {2}%".format("#"*progLen, " "*(columns-progLen), progPercent))
            sys.stdout.flush()

    os.system('rm -f charNMOS.net charPMOS.net simParams.net outN.raw outP.raw b3v33check.log')
    print
    print("Data generated. Saving...")
    pickle.dump(mosDat, open("MOS.dat", "wb"))
    print("Done! Data saved in MOS.dat")
