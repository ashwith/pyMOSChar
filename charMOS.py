import os
import os.path
import sys
import pickle
import spice3read
import numpy as np

import signal
import sys

mosDat = {}

modelFiles  = ("mosfet.mod",)
mosLengths  = np.arange(1, 10, 1)
simulator   = "ngspice"
modelN      = "cmosn"
modelP      = "cmosp"
simOptions  = ""
corners      = ('section=tt',)
subcktPath  = ""
datFileName = "MOS.dat"
vgsStep     =  25e-3 
vdsStep     =  25e-3 
vsbStep     =  25e-3 
vgsMax      =  1.8 
vdsMax      =  1.8 
vsbMax      =  1.8 
numfing     = 1
temp        = 300
width       = 1

vgs = None
vds = None
vsb = None

def handleKill(signal, frame):
    print('Data generation halted. Cleaning up...')
    os.system('rm -fr {0} charNMOS.net charPMOS.net simParams.net outN.raw outP.raw b3v33check.log, charMOS.scs, charMOS.raw charMOS.psf.raw'.format(datFileName))
    sys.exit(0)

signal.signal(signal.SIGINT, handleKill)

def init(**settings):

    global vgs
    global vsb
    global vds
    global mosDat

    for key in settings.keys():
        globals()[key] = settings[key]
    
    for modelFile in modelFiles: 
        if (not os.path.isfile(modelFile)):
            print("Model file {0} not found!".format(modelFile))
            print("Please call init() again with a valid model file")
            return None
    
    vgs = np.linspace(0, vgsMax, vgsMax/vgsStep + 1)
    vds = np.linspace(0, vdsMax, vdsMax/vdsStep + 1)
    vsb = np.linspace(0, vsbMax, vsbMax/vsbStep + 1)

    mosDat['pfet'] = {}
    mosDat['nfet'] = {}
    mosDat['modelFiles'] = modelFiles
    mosDat['simulator'] = simulator

    mosDat['nfet']['corners'] = corners
    mosDat['nfet']['temp'] = temp
    mosDat['nfet']['length'] = mosLengths
    mosDat['nfet']['width'] = width
    mosDat['nfet']['numfing'] = numfing
    mosDat['nfet']['vgs'] = vgs
    mosDat['nfet']['vds'] = vds
    mosDat['nfet']['vsb'] = -vsb
    
    mosDat['pfet']['corners'] = corners
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

def genNetlistNngspice(fName='charNMOS.net'):
    netlistN = open(fName, 'w')
    netlistN.write("Characterize N Channel MOSFET\n")
    netlistN.write("\n")
    for modelFile in modelFiles:
        netlistN.write(".include {0}\n".format(modelFile))
    netlistN.write(".include simParams.net\n")
    netlistN.write("\n")
    netlistN.write("vds  nDrain 0 dc 0\n")
    netlistN.write("vgs  nGate  0 dc 0\n")
    netlistN.write("vbs  nBulk  0 dc {-mosChar_sb}\n")
    netlistN.write("\n")
    netlistN.write("mn nDrain nGate 0 nBulk {0}  L={{length*1e-6}} W={{{1}*1e-6}}\n".format(modelN, width))
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
    
def genNetlistPngspice(fName='charPMOS.net'):
    netlistP = open(fName, 'w')
    netlistP.write("Characterize P Channel MOSFET\n")
    netlistP.write("\n")
    for modelFile in modelFiles:
        netlistP.write(".include {0}\n".format(modelFile))
    netlistP.write(".include simParams.net\n")
    netlistP.write("\n")
    netlistP.write("vds  nDrain 0 dc 0\n")
    netlistP.write("vgs  nGate  0 dc 0\n")
    netlistP.write("vbs  nBulk  0 dc mosChar_sb\n")
    netlistP.write("\n")
    netlistP.write("mp nDrain nGate 0 nBulk {0}  L={{length*1e-6}} W={{{1}*1e-6}}\n".format(modelP, width))
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

def genNetlistNEldo(fName='charNMOS.net'):
    netlistN = open(fName, 'w')


def genNetlistSpectre(fName='charMOS.scs'):

    if (subcktPath == ""):
        nmos = "mn"
        pmos = "mp"
    else:
        nmos = "mn." + subcktPath
        pmos = "mp." + subcktPath

    netlist = open(fName, 'w')
    netlist.write('//charMOS.scs \n')
    for modelFile, corner in zip(modelFiles, corners):
        netlist.write('include  "{0}" {1}\n'.format(modelFile, corner))
    netlist.write('include "simParams.scs" \n')
    netlist.write('save {0}:ids {0}:vth {0}:igd {0}:igs {0}:gm {0}:gmbs {0}:gds {0}:cgg {0}:cgs {0}:cgd {0}:cgb {0}:cdd {0}:cdg {0}:css {0}:csg {0}:cjd {0}:cjs {1}:ids {1}:vth {1}:igd {1}:igs {1}:gm {1}:gmbs {1}:gds {1}:cgg {1}:cgs {1}:cgd {1}:cgb {1}:cdd {1}:cdg {1}:css {1}:csg {1}:cjd {1}:cjs\n'.format(nmos, pmos))
    netlist.write('parameters mosChar_gs=0 mosChar_ds=0 \n')
    netlist.write('vdsn     (vdn 0)         vsource dc=mosChar_ds  \n')
    netlist.write('vgsn     (vgn 0)         vsource dc=mosChar_gs  \n')
    netlist.write('vbsn     (vbn 0)         vsource dc=-mosChar_sb \n')
    netlist.write('vdsp     (vdp 0)         vsource dc=-mosChar_ds \n')
    netlist.write('vgsp     (vgp 0)         vsource dc=-mosChar_gs \n')
    netlist.write('vbsp     (vbp 0)         vsource dc=mosChar_sb  \n')
    netlist.write('\n')
    netlist.write('mn (vdn vgn 0 vbn) {0} l=length*1e-6 w={1}e-6 multi=1 nf={2} _ccoflag=1\n'.format(modelN, width, numfing))
    netlist.write('mp (vdp vgp 0 vbp) {0} l=length*1e-6 w={1}e-6 multi=1 nf={2} _ccoflag=1\n'.format(modelP, width, numfing))
    netlist.write('\n')
    netlist.write('options1 options gmin=1e-13 dc_pivot_check=yes reltol=1e-4 vabstol=1e-6 iabstol=1e-10 temp=27 tnom=27 rawfmt=nutbin rawfile="./charMOS.raw" save=none\n')
    netlist.write('sweepvds sweep param=mosChar_ds start=0 stop={0} step={1} {{ \n'.format(vdsMax, vdsStep))
    netlist.write('sweepvgs dc param=mosChar_gs start=0 stop={0} step={1} \n'.format(vgsMax, vgsStep))
    netlist.write('}\n')

def genSimParams(L, VSB):
    paramFile = open("simParams.net", 'w')
    paramFile.write(".param length={0}\n".format(L))
    paramFile.write(".param mosChar_sb={0}\n".format(VSB))
    paramFile.close()

def genSimParamsSpectre(L, VSB):
    paramFile = open("simParams.scs", 'w')
    paramFile.write("parameters length={0}\n".format(L))
    paramFile.write("parameters mosChar_sb={0}\n".format(VSB))
    paramFile.close()
    
def runSim(fileName='charMOS.net', simulator='ngspice'):
    os.system("{0} {1} {2}  &>> charMOSPy.log".format(simulator, fileName, simOptions))


def genDB():

    if (simulator == "ngspice"):
        genNetlistNngspice()
        genNetlistPngspice()
    elif (simulator == "spectre"):
        genNetlistSpectre()
    else:
        print "ERROR: Invalid/Unsupported simulator specified"
        sys.exit(0)

    progTotal = len(mosLengths)*len(vsb)
    progCurr  = 0
    print("Data generation in progress. Go have a coffee...")
    for idxL in range(len(mosLengths)):
        for idxVSB in range(len(vsb)):
            
            if (simulator == "ngspice"):
                genSimParams(mosLengths[idxL], vsb[idxVSB])
                
                myfile = open("charMOSpy.log", "a")
                myfile.write("charMOS: Simulating for L={0}, VSB={1}\n".format(idxL, idxVSB))
                myfile.close()

                runSim("charNMOS.net", "ngspice")
                simDat = spice3read.read('outN.raw')
                
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

                runSim("charPMOS.net", "ngspice")
                simDat = spice3read.read('outP.raw')
                
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

            elif (simulator == "spectre"):
                genSimParamsSpectre(mosLengths[idxL], vsb[idxVSB])
                
                runSim("charMOS.scs", "spectre")
                simDat = spice3read.read('charMOS.raw', 'spectre')
                
                if (subcktPath == ""):
                    nmos = "mn"
                    pmos = "mp"
                else:
                    nmos = "mn." + subcktPath
                    pmos = "mp." + subcktPath

                mosDat['nfet']['id'][idxL][idxVSB]  = simDat['{0}:ids'.format(nmos)]
                mosDat['nfet']['vt'][idxL][idxVSB]  = simDat['{0}:vth'.format(nmos)]
                mosDat['nfet']['gm'][idxL][idxVSB]  = simDat['{0}:gm'.format(nmos)]
                mosDat['nfet']['gmb'][idxL][idxVSB] = simDat['{0}:gmbs'.format(nmos)]
                mosDat['nfet']['gds'][idxL][idxVSB] = simDat['{0}:gds'.format(nmos)]
                mosDat['nfet']['cgg'][idxL][idxVSB] = simDat['{0}:cgg'.format(nmos)]
                mosDat['nfet']['cgs'][idxL][idxVSB] = simDat['{0}:cgs'.format(nmos)]
                mosDat['nfet']['cgd'][idxL][idxVSB] = simDat['{0}:cgd'.format(nmos)]
                mosDat['nfet']['cgb'][idxL][idxVSB] = simDat['{0}:cgb'.format(nmos)]
                mosDat['nfet']['cdd'][idxL][idxVSB] = simDat['{0}:cdd'.format(nmos)]
                mosDat['nfet']['css'][idxL][idxVSB] = simDat['{0}:css'.format(nmos)]

                mosDat['pfet']['id'][idxL][idxVSB]  = simDat['{0}:ids'.format(pmos)]
                mosDat['pfet']['vt'][idxL][idxVSB]  = simDat['{0}:vth'.format(pmos)]
                mosDat['pfet']['gm'][idxL][idxVSB]  = simDat['{0}:gm'.format(pmos)]
                mosDat['pfet']['gmb'][idxL][idxVSB] = simDat['{0}:gmbs'.format(pmos)]
                mosDat['pfet']['gds'][idxL][idxVSB] = simDat['{0}:gds'.format(pmos)]
                mosDat['pfet']['cgg'][idxL][idxVSB] = simDat['{0}:cgg'.format(pmos)]
                mosDat['pfet']['cgs'][idxL][idxVSB] = simDat['{0}:cgs'.format(pmos)]
                mosDat['pfet']['cgd'][idxL][idxVSB] = simDat['{0}:cgd'.format(pmos)]
                mosDat['pfet']['cgb'][idxL][idxVSB] = simDat['{0}:cgb'.format(pmos)]
                mosDat['pfet']['cdd'][idxL][idxVSB] = simDat['{0}:cdd'.format(pmos)]
                mosDat['pfet']['css'][idxL][idxVSB] = simDat['{0}:css'.format(pmos)]
            
            
            rows, columns = os.popen('stty size', 'r').read().split()
            columns = int(columns) - 10
            progCurr += 1
            progPercent = 100 * progCurr / progTotal
            progLen = int(progPercent*columns/100)
            sys.stdout.write("\r[{0}{1}] {2}%".format("#"*progLen, " "*(columns-progLen), progPercent))
            sys.stdout.flush()

    os.system('rm -fr charNMOS.net charPMOS.net simParams.net outN.raw outP.raw b3v33check.log charMOS.scs simParams.scs charMOS.raw charMOS.raw.psf charMOS.ahdlSimDB charMOS.log')
    print
    print("Data generated. Saving...")
    pickle.dump(mosDat, open(datFileName, "wb"), pickle.HIGHEST_PROTOCOL)
    print("Done! Data saved in " + datFileName)
